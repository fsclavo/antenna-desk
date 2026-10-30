# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed-line configuration dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
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

        self.setWindowTitle(translator.t("feed_line.title"))
        self.resize(440, 260)

        self._enabled = QCheckBox(translator.t("feed_line.enabled"), self)
        self._enabled.setChecked(feed_line is not None)
        self._enabled.toggled.connect(self._update_controls)

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
        form.addRow(self._label_impedance, self._impedance)
        form.addRow(self._label_length, self._length)
        form.addRow(self._label_velocity, self._velocity_factor)
        form.addRow(self._label_loss, self._loss)

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
        layout.addWidget(hint)
        layout.addStretch(1)
        layout.addWidget(buttons)

        self._update_controls()

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
