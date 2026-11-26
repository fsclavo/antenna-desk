# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided log-periodic dipole array generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.log_periodic import LogPeriodicParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.log_periodic_form import LogPeriodicForm


class LogPeriodicDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: LogPeriodicParameters | None = None,
    ) -> None:
        form = LogPeriodicForm(translator, unit_system, parameters, None)
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("log_periodic.hint"))
        hint.setWordWrap(True)

        super().__init__(
            title=translator.t("log_periodic.title"),
            form=form,
            notes=(hint,),
            initial_size=(640, 900),
            parent=parent,
        )
        self._translator = translator
        self._log_periodic_form = form
        self._parameters: LogPeriodicParameters | None = None
        self._hint = hint

    def parameters(self) -> LogPeriodicParameters:
        return self._log_periodic_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(
                self,
                self._translator.t("log_periodic.title"),
                str(exc),
            )
            return
        self.accept()

    def result_parameters(self) -> LogPeriodicParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
