# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided off-center-fed dipole generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.ocfd import OCFDParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.ocfd_form import OCFDForm


class OCFDDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: OCFDParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: OCFDParameters | None = None
        self._form = OCFDForm(translator, unit_system, parameters, self)
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
        self._ground = self._form._ground
        self._material = self._form._material

        self.setWindowTitle(translator.t("ocfd.title"))
        self.resize(560, 560)

        self._hint = QLabel(translator.t("ocfd.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("ocfd.evidence"), self)
        self._evidence.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._form)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addStretch(1)
        layout.addWidget(buttons)

    def parameters(self) -> OCFDParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("ocfd.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> OCFDParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
