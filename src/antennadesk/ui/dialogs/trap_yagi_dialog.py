# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided trapped Yagi generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.trap_yagi import TrapYagiParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.trap_yagi_form import TrapYagiForm


class TrapYagiDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: TrapYagiParameters | None = None,
    ) -> None:
        form = TrapYagiForm(translator, unit_system, parameters, None)
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
            form.load_starting_dimensions()
        hint = QLabel(translator.t("trap_yagi.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("trap_yagi.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("trap_yagi.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(580, 860),
            parent=parent,
        )
        self._translator = translator
        self._trap_yagi_form = form
        self._parameters: TrapYagiParameters | None = None
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> TrapYagiParameters:
        return self._trap_yagi_form.parameters()

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
