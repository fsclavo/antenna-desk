# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project-level cliff/second-medium site ground dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...domain.environment.site_ground import (
    MAX_SITE_LABEL_LENGTH,
    EdgeShape,
    SiteGroundProfile,
)
from ..fonts import scaled_dialog_size
from ..help import apply_help, apply_row_help
from ..i18n import Translator
from ..units import DisplayUnits
from ..widgets.form_units import LengthField, LengthFieldSpec


class SiteGroundDialog(QDialog):
    """Edit the optional far-field-only cliff/second-medium profile."""

    def __init__(
        self,
        translator: Translator,
        display_units: DisplayUnits,
        profile: SiteGroundProfile | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self.setWindowTitle(translator.t("site_ground.title"))
        self.resize(*scaled_dialog_size(560, 470))

        self._enabled = QCheckBox(translator.t("site_ground.enabled"), self)
        self._enabled.setChecked(profile is not None)

        self._permittivity = QDoubleSpinBox(self)
        self._permittivity.setRange(1.0, 1_000.0)
        self._permittivity.setDecimals(3)
        self._permittivity.setValue(
            profile.second_medium_relative_permittivity if profile else 81.0
        )

        self._conductivity = QDoubleSpinBox(self)
        self._conductivity.setRange(0.000001, 100.0)
        self._conductivity.setDecimals(6)
        self._conductivity.setSingleStep(0.001)
        conductivity_suffix = " S/m"
        self._conductivity.setSuffix(conductivity_suffix)
        self._conductivity.setValue(profile.second_medium_conductivity_s_per_m if profile else 5.0)

        self._edge_shape = QComboBox(self)
        self._edge_shape.addItem(translator.t("site_ground.linear"), EdgeShape.LINEAR)
        self._edge_shape.addItem(translator.t("site_ground.circular"), EdgeShape.CIRCULAR)
        if profile is not None:
            index = self._edge_shape.findData(profile.edge_shape)
            if index >= 0:
                self._edge_shape.setCurrentIndex(index)

        self._edge_distance = QDoubleSpinBox(self)
        self._edge_distance_field = LengthField(
            self._edge_distance,
            LengthFieldSpec(0.0, 1_000_000.0, scale_hint="m"),
            translator,
            display_units,
        )
        self._edge_distance_field.configure(
            profile.edge_distance_m if profile is not None else 50.0
        )

        self._edge_height = QDoubleSpinBox(self)
        self._edge_height_field = LengthField(
            self._edge_height,
            LengthFieldSpec(0.0, 10_000.0, scale_hint="m"),
            translator,
            display_units,
        )
        self._edge_height_field.configure(profile.edge_height_m if profile is not None else 0.0)

        self._label = QLineEdit(self)
        self._label.setMaxLength(MAX_SITE_LABEL_LENGTH)
        self._label.setText(profile.label if profile else "")
        self._notes = QPlainTextEdit(self)
        self._notes.setPlainText(profile.notes if profile else "")
        self._notes.setFixedHeight(64)

        self._labels = (
            QLabel(translator.t("site_ground.permittivity"), self),
            QLabel(translator.t("site_ground.conductivity"), self),
            QLabel(translator.t("site_ground.edge_shape"), self),
            QLabel(translator.t("site_ground.edge_distance"), self),
            QLabel(translator.t("site_ground.edge_height"), self),
            QLabel(translator.t("site_ground.label"), self),
            QLabel(translator.t("site_ground.notes"), self),
        )
        form = QFormLayout()
        form.addRow(self._labels[0], self._permittivity)
        form.addRow(self._labels[1], self._conductivity)
        form.addRow(self._labels[2], self._edge_shape)
        form.addRow(self._labels[3], self._edge_distance)
        form.addRow(self._labels[4], self._edge_height)
        form.addRow(self._labels[5], self._label)
        form.addRow(self._labels[6], self._notes)
        for row, key in enumerate(
            (
                "site_ground.permittivity",
                "site_ground.conductivity",
                "site_ground.edge_shape",
                "site_ground.edge_distance",
                "site_ground.edge_height",
                "site_ground.label",
                "site_ground.notes",
            )
        ):
            apply_row_help(form, row, translator, key)

        hint = QLabel(translator.t("site_ground.hint"), self)
        hint.setWordWrap(True)
        apply_help(hint, translator, "site_ground.hint")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._enabled)
        layout.addLayout(form)
        layout.addWidget(hint)
        layout.addStretch(1)
        layout.addWidget(buttons)

        apply_help(self._enabled, translator, "site_ground.enabled")
        self._enabled.toggled.connect(self._update_enabled)
        self._update_enabled(self._enabled.isChecked())

    def _update_enabled(self, enabled: bool) -> None:
        for widget in (
            self._permittivity,
            self._conductivity,
            self._edge_shape,
            self._edge_distance,
            self._edge_height,
            self._label,
            self._notes,
        ):
            widget.setEnabled(enabled)

    def profile(self) -> SiteGroundProfile | None:
        if not self._enabled.isChecked():
            return None
        return SiteGroundProfile(
            second_medium_relative_permittivity=self._permittivity.value(),
            second_medium_conductivity_s_per_m=self._conductivity.value(),
            edge_distance_m=self._edge_distance_field.value_m(),
            edge_shape=self._edge_shape.currentData(),
            edge_height_m=self._edge_height_field.value_m(),
            label=self._label.text(),
            notes=self._notes.toPlainText(),
        )

    def accept(self) -> None:
        try:
            self.profile()
        except ValueError as exc:
            QMessageBox.warning(self, self.windowTitle(), str(exc))
            return
        super().accept()
