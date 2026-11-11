# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Configure a frequency-dependent balun or unun insertion loss."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.balun import BalunLoss
from ..fonts import scaled_dialog_size
from ..help import apply_row_help
from ..i18n import Translator


class BalunLossDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        parent: QWidget | None = None,
        *,
        balun_loss: BalunLoss | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._result: BalunLoss | None = None

        self._enabled = QCheckBox(translator.t("balun_loss.enabled"), self)
        self._reference_loss = QDoubleSpinBox(self)
        self._reference_loss.setRange(0.0, 100.0)
        self._reference_loss.setDecimals(3)
        self._reference_loss.setSuffix(" dB")
        self._reference_frequency = QDoubleSpinBox(self)
        self._reference_frequency.setRange(0.1, 100_000.0)
        self._reference_frequency.setDecimals(3)
        self._reference_frequency.setSuffix(" MHz")
        self._exponent = QDoubleSpinBox(self)
        self._exponent.setRange(0.0, 5.0)
        self._exponent.setDecimals(3)
        self._preview = QLabel(self)
        self._preview.setWordWrap(True)
        self._hint = QLabel(translator.t("balun_loss.hint"), self)
        self._hint.setWordWrap(True)

        if balun_loss is None:
            self._enabled.setChecked(False)
            self._reference_loss.setValue(0.5)
            self._reference_frequency.setValue(7.0)
            self._exponent.setValue(0.5)
        else:
            self._enabled.setChecked(balun_loss.enabled)
            self._reference_loss.setValue(balun_loss.reference_loss_db)
            self._reference_frequency.setValue(balun_loss.reference_frequency_hz / 1_000_000.0)
            self._exponent.setValue(balun_loss.exponent)

        form = QFormLayout()
        form.addRow(self._enabled)
        form.addRow(translator.t("balun_loss.reference_frequency"), self._reference_frequency)
        form.addRow(translator.t("balun_loss.reference_loss"), self._reference_loss)
        form.addRow(translator.t("balun_loss.exponent"), self._exponent)
        form.addRow(self._preview)
        apply_row_help(form, 1, translator, "balun_loss.reference_frequency")
        apply_row_help(form, 2, translator, "balun_loss.reference_loss")
        apply_row_help(form, 3, translator, "balun_loss.exponent")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._hint)
        layout.addStretch(1)
        layout.addWidget(buttons)

        self.setWindowTitle(translator.t("balun_loss.title"))
        self.resize(*scaled_dialog_size(520, 420))
        self._enabled.toggled.connect(self._update_state)
        self._reference_loss.valueChanged.connect(self._update_preview)
        self._reference_frequency.valueChanged.connect(self._update_preview)
        self._exponent.valueChanged.connect(self._update_preview)
        self._update_state()

    def _update_state(self, *_args: object) -> None:
        enabled = self._enabled.isChecked()
        self._reference_loss.setEnabled(enabled)
        self._reference_frequency.setEnabled(enabled)
        self._exponent.setEnabled(enabled)
        self._update_preview()

    def _update_preview(self, *_args: object) -> None:
        if not self._enabled.isChecked():
            self._preview.setText(self._translator.t("balun_loss.disabled"))
            return
        model = BalunLoss(
            enabled=True,
            reference_frequency_hz=self._reference_frequency.value() * 1_000_000.0,
            reference_loss_db=self._reference_loss.value(),
            exponent=self._exponent.value(),
        )
        values = " · ".join(
            f"{frequency:g} MHz: {model.loss_db(frequency * 1_000_000.0):.3f} dB"
            for frequency in (1.8, 7.0, 14.0, 28.0)
        )
        self._preview.setText(self._translator.t("balun_loss.preview", values=values))

    def _accept(self) -> None:
        if not self._enabled.isChecked():
            self._result = None
        else:
            try:
                self._result = BalunLoss(
                    enabled=True,
                    reference_frequency_hz=self._reference_frequency.value() * 1_000_000.0,
                    reference_loss_db=self._reference_loss.value(),
                    exponent=self._exponent.value(),
                )
            except ValueError as exc:
                self._preview.setText(str(exc))
                return
        self.accept()

    def result_balun_loss(self) -> BalunLoss | None:
        return self._result
