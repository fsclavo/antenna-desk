# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed-line configuration dialog."""

from __future__ import annotations

import math

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.feed_line import FeedLine
from ...domain.design.materials_reference import COAX_REFERENCES, CoaxReference
from ..fonts import scaled_dialog_size
from ..help import apply_help, apply_row_help
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key


class FeedLineDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        feed_line: FeedLine | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._feed_line = feed_line
        self._catalog_updating = False

        self.setWindowTitle(translator.t("feed_line.title"))
        self.resize(*scaled_dialog_size(520, 340))

        self._enabled = QCheckBox(translator.t("feed_line.enabled"), self)
        self._enabled.setChecked(feed_line is not None)

        self._catalog_label = QLabel(translator.t("feed_line.catalog"), self)
        self._catalog = QComboBox(self)
        self._catalog.addItem(translator.t("feed_line.catalog_custom"), None)
        for entry in COAX_REFERENCES:
            self._catalog.addItem(translator.t(f"materials.coax.{entry.key}.name"), entry)

        self._impedance = QDoubleSpinBox(self)
        self._impedance.setRange(5.0, 1_000.0)
        self._impedance.setDecimals(2)
        self._impedance.setSuffix(" Ω")
        self._impedance.setValue(feed_line.characteristic_impedance_ohm if feed_line else 50.0)

        self._length = QDoubleSpinBox(self)
        self._length.setDecimals(3)
        self._length.setRange(0.0, 100_000.0)
        self._length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._length.setValue(length_from_m(feed_line.length_m if feed_line else 10.0, unit_system))

        self._velocity_factor = QDoubleSpinBox(self)
        self._velocity_factor.setRange(0.1, 1.0)
        self._velocity_factor.setDecimals(3)
        self._velocity_factor.setSingleStep(0.01)
        self._velocity_factor.setValue(feed_line.velocity_factor if feed_line else 0.66)

        self._loss = QDoubleSpinBox(self)
        self._loss.setRange(0.0, 100.0)
        self._loss.setDecimals(3)
        self._loss.setSingleStep(0.1)
        self._loss.setSuffix(" dB/100m")
        self._loss.setValue(feed_line.matched_loss_db_per_100m if feed_line else 0.0)

        self._label_impedance = QLabel(translator.t("feed_line.characteristic_impedance"), self)
        self._label_length = QLabel(translator.t("feed_line.length"), self)
        self._label_velocity = QLabel(translator.t("feed_line.velocity_factor"), self)
        self._label_loss = QLabel(translator.t("feed_line.loss"), self)

        form = QFormLayout()
        form.addRow(self._catalog_label, self._catalog)
        form.addRow(self._label_impedance, self._impedance)
        form.addRow(self._label_length, self._length)
        form.addRow(self._label_velocity, self._velocity_factor)
        form.addRow(self._label_loss, self._loss)
        apply_row_help(form, 0, translator, "feed_line.catalog")
        apply_row_help(form, 1, translator, "feed_line.characteristic_impedance")
        apply_row_help(form, 2, translator, "feed_line.length")
        apply_row_help(form, 3, translator, "feed_line.velocity_factor")
        apply_row_help(form, 4, translator, "feed_line.loss")

        self._catalog_hint = QLabel(self)
        self._catalog_hint.setWordWrap(True)
        apply_help(self._catalog_hint, translator, "feed_line.catalog_hint")

        hint = QLabel(translator.t("feed_line.hint"), self)
        hint.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._enabled)
        layout.addLayout(form)
        layout.addWidget(self._catalog_hint)
        layout.addWidget(hint)
        layout.addStretch(1)
        layout.addWidget(buttons)

        self._catalog.currentIndexChanged.connect(self._on_catalog_changed)
        self._impedance.valueChanged.connect(self._on_manual_change)
        self._velocity_factor.valueChanged.connect(self._on_manual_change)
        self._loss.valueChanged.connect(self._on_manual_change)
        self._enabled.toggled.connect(self._update_controls)

        self._restore_catalog_selection()
        self._update_controls()

    def _matching_catalog_entry(self) -> CoaxReference | None:
        if self._feed_line is None:
            return None
        matches = [
            entry
            for entry in COAX_REFERENCES
            if math.isclose(
                entry.characteristic_impedance_ohm,
                self._feed_line.characteristic_impedance_ohm,
                rel_tol=1e-9,
            )
            and math.isclose(
                entry.velocity_factor,
                self._feed_line.velocity_factor,
                rel_tol=1e-9,
            )
            and math.isclose(
                entry.matched_loss_db_per_100m,
                self._feed_line.matched_loss_db_per_100m,
                rel_tol=1e-9,
            )
        ]
        # The catalog key is not persisted.  When several cables share the same
        # electrical values, show Custom instead of claiming a specific one.
        return matches[0] if len(matches) == 1 else None

    def _restore_catalog_selection(self) -> None:
        entry = self._matching_catalog_entry()
        if entry is None:
            self._set_catalog_index(0)
            self._update_catalog_hint(None)
            return
        index = next(
            (
                candidate
                for candidate in range(self._catalog.count())
                if self._catalog.itemData(candidate) is entry
            ),
            0,
        )
        self._set_catalog_index(index)
        self._update_catalog_hint(entry)

    def _set_catalog_index(self, index: int) -> None:
        self._catalog_updating = True
        try:
            self._catalog.setCurrentIndex(index)
        finally:
            self._catalog_updating = False

    def _on_catalog_changed(self, _index: int) -> None:
        if self._catalog_updating:
            return
        entry = self._catalog.currentData()
        if not isinstance(entry, CoaxReference):
            self._update_catalog_hint(None)
            return
        self._catalog_updating = True
        try:
            self._enabled.setChecked(True)
            self._impedance.setValue(entry.characteristic_impedance_ohm)
            self._velocity_factor.setValue(entry.velocity_factor)
            self._loss.setValue(entry.matched_loss_db_per_100m)
        finally:
            self._catalog_updating = False
        self._update_catalog_hint(entry)
        self._update_controls()

    def _on_manual_change(self, _value: float) -> None:
        if self._catalog_updating or self._catalog.currentData() is None:
            return
        self._set_catalog_index(0)
        self._update_catalog_hint(None)

    def _update_catalog_hint(self, entry: CoaxReference | None) -> None:
        if entry is None:
            self._catalog_hint.setText(self._translator.t("feed_line.catalog_custom_hint"))
            return
        self._catalog_hint.setText(
            self._translator.t(
                "feed_line.catalog_hint",
                loss=f"{entry.matched_loss_db_per_100m:.2f} dB/100m",
                frequency=f"{entry.reference_frequency_hz / 1_000_000.0:g} MHz",
            )
        )

    def _update_controls(self) -> None:
        enabled = self._enabled.isChecked()
        for widget in (self._impedance, self._length, self._velocity_factor, self._loss):
            widget.setEnabled(enabled)

    def accept(self) -> None:
        try:
            self._feed_line = self.feed_line()
        except ValueError as exc:
            QMessageBox.critical(self, self._translator.t("feed_line.title"), str(exc))
            return
        super().accept()

    def feed_line(self) -> FeedLine | None:
        if not self._enabled.isChecked():
            return None
        return FeedLine(
            characteristic_impedance_ohm=self._impedance.value(),
            length_m=length_to_m(self._length.value(), self._unit_system),
            velocity_factor=self._velocity_factor.value(),
            matched_loss_db_per_100m=self._loss.value(),
        )

    def result_feed_line(self) -> FeedLine | None:
        return self._feed_line
