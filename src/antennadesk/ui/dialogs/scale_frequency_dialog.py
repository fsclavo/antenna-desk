# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Target-frequency dialog for explicit geometry scaling."""

from __future__ import annotations

import math

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator


class ScaleFrequencyDialog(QDialog):
    """Ask for the target frequency before scaling a tuned design."""

    def __init__(
        self,
        translator: Translator,
        current_frequency_hz: float,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._current_frequency_hz = current_frequency_hz
        self.setWindowTitle(translator.t("scale_frequency.title"))
        self.resize(*scaled_dialog_size(520, 280))

        current_text = translator.t(
            "scale_frequency.current",
            frequency=f"{current_frequency_hz / 1_000_000.0:.6f}",
        )
        self._current = QLabel(current_text, self)
        self._current.setWordWrap(True)

        self._target = QDoubleSpinBox(self)
        self._target.setRange(0.1, 100_000.0)
        self._target.setDecimals(6)
        self._target.setSuffix(" MHz")
        self._target.setValue(current_frequency_hz / 1_000_000.0)
        target_label = QLabel(translator.t("scale_frequency.target"), self)
        apply_help(target_label, translator, "scale_frequency.target")
        apply_help(self._target, translator, "scale_frequency.target")

        self._warning = QLabel(translator.t("scale_frequency.warning"), self)
        self._warning.setWordWrap(True)
        apply_help(self._warning, translator, "scale_frequency.warning")

        form = QFormLayout()
        form.addRow(target_label, self._target)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self._ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        self._target.valueChanged.connect(self._update_ok)

        layout = QVBoxLayout(self)
        layout.addWidget(self._current)
        layout.addLayout(form)
        layout.addWidget(self._warning)
        layout.addStretch(1)
        layout.addWidget(buttons)
        self._update_ok()

    def target_frequency_hz(self) -> float:
        return self._target.value() * 1_000_000.0

    def _update_ok(self, *_args: object) -> None:
        same = math.isclose(
            self._target.value(),
            self._current_frequency_hz / 1_000_000.0,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
        self._ok.setEnabled(not same)

    def _accept(self) -> None:
        if not self._ok.isEnabled():
            return
        self.accept()
