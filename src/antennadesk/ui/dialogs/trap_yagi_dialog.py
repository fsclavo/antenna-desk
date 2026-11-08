# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided trapped Yagi generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.trap_yagi import TrapYagiParameters
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.trap_yagi_form import TrapYagiForm


class TrapYagiDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: TrapYagiParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: TrapYagiParameters | None = None
        self._form = TrapYagiForm(translator, unit_system, parameters, self)
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
        self.setWindowTitle(translator.t("trap_yagi.title"))
        self.resize(*scaled_dialog_size(580, 860))

        self._hint = QLabel(translator.t("trap_yagi.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("trap_yagi.evidence"), self)
        self._evidence.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._form)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll, 1)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addWidget(buttons)

    def parameters(self) -> TrapYagiParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(
                self,
                self._translator.t("trap_yagi.title"),
                str(exc),
            )
            return
        self.accept()

    def result_parameters(self) -> TrapYagiParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
