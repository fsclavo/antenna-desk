# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided fan-dipole generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.fan_dipole import FanDipoleParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.fan_dipole_form import FanDipoleForm
from ..widgets.form_dialog import FormDialogFrame


class FanDipoleDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: FanDipoleParameters | None = None,
    ) -> None:
        form = FanDipoleForm(translator, unit_system, parameters, None)
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("fan.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("fan.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("fan.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(620, 620),
            scroll_form=False,
            parent=parent,
        )
        self._translator = translator
        self._fan_form = form
        self._parameters: FanDipoleParameters | None = None
        self._table = form._table
        self._add_element = form._add_element
        self._remove_element = form._remove_element
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> FanDipoleParameters:
        return self._fan_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("fan.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> FanDipoleParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
