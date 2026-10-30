# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided J-pole and Slim-Jim generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.j_pole import JPoleParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.j_pole_form import JPoleForm


class JPoleDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: JPoleParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: JPoleParameters | None = None
        self._form = JPoleForm(translator, unit_system, parameters, self)
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
        self.setWindowTitle(translator.t("j_pole.title"))
        self.resize(560, 620)

        self._hint = QLabel(translator.t("j_pole.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("j_pole.evidence"), self)
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

    def parameters(self) -> JPoleParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("j_pole.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> JPoleParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
