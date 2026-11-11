# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create, edit, duplicate, and activate installation profiles."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from uuid import UUID, uuid4

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.environment.ground import GroundModel
from ...domain.projects.installation import (
    InstallationProfile,
    InstallationSupport,
)
from ..fonts import scaled_dialog_size
from ..help import apply_help, apply_row_help
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key
from ..widgets.ground_presets import SOIL_PRESETS


class InstallationProfileDialog(QDialog):
    """Manage the project's installation profiles and the active one."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        profiles: tuple[InstallationProfile, ...] = (),
        active_profile_id: UUID | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._profiles = list(profiles)
        self._active_profile_id = active_profile_id
        self._current_index = -1
        self._loading = False
        self._custom_ground: GroundModel | None = None

        if not self._profiles:
            self._profiles.append(self._default_profile(1))

        self.setWindowTitle(translator.t("installation.title"))
        self.resize(*scaled_dialog_size(760, 560))
        self._build_ui()
        self._refresh_list(active_profile_id or self._profiles[0].id)

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        t = self._translator.t
        self._hint = QLabel(t("installation.hint"), self)
        self._hint.setWordWrap(True)

        self._list = QListWidget(self)
        self._list.setMinimumWidth(190)
        self._list.currentRowChanged.connect(self._on_current_row_changed)
        apply_help(self._list, self._translator, "installation.profiles")

        self._add_button = QPushButton(t("installation.add"), self)
        self._add_button.clicked.connect(self._add_profile)
        self._duplicate_button = QPushButton(t("installation.duplicate"), self)
        self._duplicate_button.clicked.connect(self._duplicate_profile)
        self._remove_button = QPushButton(t("installation.remove"), self)
        self._remove_button.clicked.connect(self._remove_profile)
        apply_help(self._add_button, self._translator, "installation.add")
        apply_help(self._duplicate_button, self._translator, "installation.duplicate")
        apply_help(self._remove_button, self._translator, "installation.remove")

        list_buttons = QHBoxLayout()
        list_buttons.setContentsMargins(0, 0, 0, 0)
        list_buttons.addWidget(self._add_button)
        list_buttons.addWidget(self._duplicate_button)
        list_buttons.addWidget(self._remove_button)

        self._active_note = QLabel(t("installation.active_note"), self)
        self._active_note.setWordWrap(True)

        left = QVBoxLayout()
        left.addWidget(self._list, 1)
        left.addLayout(list_buttons)
        left.addWidget(self._active_note)

        self._form_widget = QWidget(self)
        form = QFormLayout(self._form_widget)

        self._name = QLineEdit(self)
        self._name.setMaxLength(200)
        self._height = QDoubleSpinBox(self)
        self._height.setRange(0.0, 10_000.0)
        self._height.setDecimals(2)
        self._height.setSpecialValueText(t("installation.not_set"))
        self._height.setSuffix(f" {t(length_unit_key(self._unit_system))}")
        self._width = QDoubleSpinBox(self)
        self._width.setRange(0.0, 10_000.0)
        self._width.setDecimals(2)
        self._width.setSpecialValueText(t("installation.not_set"))
        self._width.setSuffix(f" {t(length_unit_key(self._unit_system))}")
        self._orientation = QDoubleSpinBox(self)
        self._orientation.setRange(0.0, 360.0)
        self._orientation.setDecimals(1)
        self._orientation.setWrapping(True)
        self._orientation.setSuffix("°")
        self._support = QComboBox(self)
        for support in InstallationSupport:
            self._support.addItem(t(f"installation.support.{support.value}"), support.value)
        self._ground = QComboBox(self)
        self._ground.addItem(t("installation.ground_none"), None)
        self._ground.addItem(t("installation.ground_free_space"), GroundModel.free_space())
        self._ground.addItem(t("installation.ground_perfect"), GroundModel.perfect())
        for preset in SOIL_PRESETS:
            self._ground.addItem(
                t(preset.label_key),
                GroundModel.finite(
                    relative_permittivity=preset.relative_permittivity,
                    conductivity_s_per_m=preset.conductivity_s_per_m,
                ),
            )
        self._ground.addItem(t("installation.ground_custom"), "custom")
        self._notes = QPlainTextEdit(self)
        self._notes.setFixedHeight(76)
        self._notes.setPlaceholderText(t("installation.notes_placeholder"))
        self._image = QLineEdit(self)
        self._browse = QPushButton(t("installation.browse"), self)
        self._browse.clicked.connect(self._browse_image)
        apply_help(self._browse, self._translator, "installation.image_reference")
        image_row = QHBoxLayout()
        image_row.setContentsMargins(0, 0, 0, 0)
        image_row.addWidget(self._image, 1)
        image_row.addWidget(self._browse)
        image_widget = QWidget(self)
        image_widget.setLayout(image_row)

        rows: list[tuple[str, QWidget]] = [
            (t("installation.name"), self._name),
            (t("installation.available_height"), self._height),
            (t("installation.available_width"), self._width),
            (t("installation.orientation"), self._orientation),
            (t("installation.support"), self._support),
            (t("installation.ground"), self._ground),
            (t("installation.notes"), self._notes),
            (t("installation.image_reference"), image_widget),
        ]
        for row, (label_text, widget) in enumerate(rows):
            label = QLabel(label_text, self)
            form.addRow(label, widget)
            apply_row_help(form, row, self._translator, f"installation.{self._help_key(row)}")

        body = QHBoxLayout()
        body.addLayout(left, 0)
        body.addWidget(self._form_widget, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(t("action.ok"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(t("action.cancel"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._hint)
        layout.addLayout(body, 1)
        layout.addWidget(buttons)

    @staticmethod
    def _help_key(row: int) -> str:
        return (
            "name",
            "available_height",
            "available_width",
            "orientation",
            "support",
            "ground",
            "notes",
            "image_reference",
        )[row]

    def _default_profile(self, index: int) -> InstallationProfile:
        return InstallationProfile(
            id=uuid4(),
            name=self._translator.t("installation.default_name", index=index),
        )

    def _refresh_list(self, select_id: UUID | None) -> None:
        self._loading = True
        self._list.clear()
        selected_row = 0
        for row, profile in enumerate(self._profiles):
            item = QListWidgetItem(profile.name)
            item.setData(Qt.ItemDataRole.UserRole, str(profile.id))
            self._list.addItem(item)
            if select_id is not None and profile.id == select_id:
                selected_row = row
        if self._profiles:
            self._list.setCurrentRow(selected_row)
        self._loading = False
        self._load_profile(self._list.currentRow())
        self._update_buttons()

    def _update_buttons(self) -> None:
        has_profile = 0 <= self._current_index < len(self._profiles)
        self._duplicate_button.setEnabled(has_profile)
        self._remove_button.setEnabled(has_profile)
        self._form_widget.setEnabled(has_profile)

    def _on_current_row_changed(self, row: int) -> None:
        if self._loading:
            return
        previous = self._current_index
        if previous >= 0 and not self._commit_current():
            self._loading = True
            self._list.setCurrentRow(previous)
            self._loading = False
            return
        self._load_profile(row)

    def _load_profile(self, row: int) -> None:
        self._current_index = row
        self._update_buttons()
        if row < 0 or row >= len(self._profiles):
            return
        profile = self._profiles[row]
        self._loading = True
        try:
            self._name.setText(profile.name)
            self._height.setValue(
                length_from_m(profile.available_height_m, self._unit_system)
                if profile.available_height_m is not None
                else 0.0
            )
            self._width.setValue(
                length_from_m(profile.available_width_m, self._unit_system)
                if profile.available_width_m is not None
                else 0.0
            )
            self._orientation.setValue(profile.orientation_deg)
            self._support.setCurrentIndex(self._support.findData(profile.support.value))
            self._set_ground(profile.ground)
            self._notes.setPlainText(profile.notes)
            self._image.setText(profile.image_reference)
        finally:
            self._loading = False

    def _set_ground(self, ground: GroundModel | None) -> None:
        index = self._ground_index(ground)
        if index < 0 and ground is not None:
            self._custom_ground = ground
            custom_index = self._ground.findData("custom")
            self._ground.setItemText(
                custom_index,
                self._translator.t(
                    "installation.ground_custom_value",
                    permittivity=f"{ground.relative_permittivity or 0.0:g}",
                    conductivity=f"{ground.conductivity_s_per_m or 0.0:g}",
                ),
            )
            index = custom_index
        else:
            self._custom_ground = None
        if index < 0:
            index = 0
        self._ground.setCurrentIndex(index)

    def _ground_index(self, ground: GroundModel | None) -> int:
        for index in range(self._ground.count()):
            data = self._ground.itemData(index)
            if ground is None and data is None:
                return index
            if isinstance(data, GroundModel) and data == ground:
                return index
        return -1

    def _selected_ground(self) -> GroundModel | None:
        data = self._ground.currentData()
        if data == "custom":
            return self._custom_ground
        return data if isinstance(data, GroundModel) else None

    def _form_profile(self) -> InstallationProfile:
        if not 0 <= self._current_index < len(self._profiles):
            raise ValueError(self._translator.t("installation.no_selection"))
        current = self._profiles[self._current_index]
        height = self._height.value()
        width = self._width.value()
        return replace(
            current,
            name=self._name.text(),
            available_height_m=(length_to_m(height, self._unit_system) if height > 0.0 else None),
            available_width_m=(length_to_m(width, self._unit_system) if width > 0.0 else None),
            orientation_deg=self._orientation.value(),
            support=InstallationSupport(self._support.currentData()),
            ground=self._selected_ground(),
            notes=self._notes.toPlainText(),
            image_reference=self._image.text().strip(),
        )

    def _commit_current(self) -> bool:
        if not 0 <= self._current_index < len(self._profiles):
            return True
        try:
            profile = self._form_profile()
        except ValueError as exc:
            QMessageBox.warning(self, self._translator.t("installation.title"), str(exc))
            return False
        self._profiles[self._current_index] = profile
        item = self._list.item(self._current_index)
        if item is not None:
            item.setText(profile.name)
        return True

    def _unique_name(self, base: str) -> str:
        names = {profile.name for profile in self._profiles}
        if base not in names:
            return base
        index = 2
        while f"{base} {index}" in names:
            index += 1
        return f"{base} {index}"

    def _add_profile(self) -> None:
        if not self._commit_current():
            return
        profile = self._default_profile(len(self._profiles) + 1)
        profile = replace(profile, name=self._unique_name(profile.name))
        self._profiles.append(profile)
        self._refresh_list(profile.id)

    def _duplicate_profile(self) -> None:
        if not self._commit_current():
            return
        if not 0 <= self._current_index < len(self._profiles):
            return
        current = self._profiles[self._current_index]
        copy = replace(
            current,
            id=uuid4(),
            name=self._unique_name(self._translator.t("installation.copy_name", name=current.name)),
        )
        self._profiles.append(copy)
        self._refresh_list(copy.id)

    def _remove_profile(self) -> None:
        if not 0 <= self._current_index < len(self._profiles):
            return
        del self._profiles[self._current_index]
        select_id = (
            self._profiles[min(self._current_index, len(self._profiles) - 1)].id
            if self._profiles
            else None
        )
        self._refresh_list(select_id)

    def _browse_image(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self._translator.t("installation.image_title"),
            str(Path.home()),
            self._translator.t("installation.image_filter"),
        )
        if filename:
            self._image.setText(filename)

    # ------------------------------------------------------------- results

    def profiles(self) -> tuple[InstallationProfile, ...]:
        return tuple(self._profiles)

    def active_profile_id(self) -> UUID | None:
        if 0 <= self._current_index < len(self._profiles):
            return self._profiles[self._current_index].id
        return None

    def accept(self) -> None:
        if not self._commit_current():
            return
        names = [profile.name for profile in self._profiles]
        if len(names) != len(set(names)):
            QMessageBox.warning(
                self,
                self._translator.t("installation.title"),
                self._translator.t("installation.duplicate_name"),
            )
            return
        self._active_profile_id = self.active_profile_id()
        super().accept()
