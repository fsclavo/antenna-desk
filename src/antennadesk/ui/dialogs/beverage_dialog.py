# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided Beverage receiving-antenna generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.beverage import BeverageParameters
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.beverage_form import BeverageForm


class BeverageDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: BeverageParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: BeverageParameters | None = None
        self._form = BeverageForm(translator, unit_system, parameters, self)
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
            self._form.load_starting_dimensions()
        self.setWindowTitle(translator.t("beverage.title"))
        self.resize(*scaled_dialog_size(560, 760))

        self._hint = QLabel(translator.t("beverage.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("beverage.evidence"), self)
        self._evidence.setWordWrap(True)

        self._starting = QPushButton(translator.t("beverage.load_starting"), self)
        self._starting.setToolTip(translator.t("beverage.load_starting_hint"))
        self._starting.clicked.connect(self._form.load_starting_dimensions)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._form)
        layout.addWidget(self._starting)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addStretch(1)
        layout.addWidget(buttons)

    def parameters(self) -> BeverageParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("beverage.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> BeverageParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
