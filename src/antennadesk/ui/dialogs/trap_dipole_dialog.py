# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided trapped-dipole generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.trap_dipole import TrapDipoleParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.trap_dipole_form import TrapDipoleForm


class TrapDipoleDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: TrapDipoleParameters | None = None,
    ) -> None:
        form = TrapDipoleForm(translator, unit_system, parameters, None)
        if parameters is None and frequency_hz is not None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("trap_dipole.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("trap_dipole.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("trap_dipole.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(600, 760),
            parent=parent,
        )
        self._translator = translator
        self._trap_dipole_form = form
        self._parameters: TrapDipoleParameters | None = None
        self._frequency = form._frequency
        self._high_band = form._high_band
        self._inner_length = form._inner_length
        self._outer_length = form._outer_length
        self._start = form._start
        self._trap_frequency = form._trap_frequency
        self._trap_inductance = form._trap_inductance
        self._trap_capacitance = form._trap_capacitance
        self._height = form._height
        self._orientation = form._orientation
        self._azimuth = form._azimuth
        self._radius = form._radius
        self._material = form._material
        self._ground = form._ground
        self._permittivity = form._permittivity
        self._conductivity = form._conductivity
        self._geometry = form._geometry
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> TrapDipoleParameters:
        return self._trap_dipole_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("trap_dipole.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> TrapDipoleParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
