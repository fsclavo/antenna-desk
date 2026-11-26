# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided magnetic-loop generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.magnetic_loop import MagneticLoopParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.magnetic_loop_form import MagneticLoopForm


class MagneticLoopDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: MagneticLoopParameters | None = None,
    ) -> None:
        form = MagneticLoopForm(
            translator,
            unit_system,
            parameters,
            None,
            wide_layout=True,
        )
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("magnetic_loop.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("magnetic_loop.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("magnetic_loop.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(920, 640),
            parent=parent,
        )
        self._translator = translator
        self._loop_form = form
        self._parameters: MagneticLoopParameters | None = None
        self._frequency = form._frequency
        self._diameter = form._diameter
        self._height = form._height
        self._sides = form._sides
        self._gap = form._gap
        self._capacitance = form._capacitance
        self._esr = form._esr
        self._azimuth = form._azimuth
        self._radius = form._radius
        self._material = form._material
        self._ground = form._ground
        self._permittivity = form._permittivity
        self._conductivity = form._conductivity
        self._geometry = form._geometry
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> MagneticLoopParameters:
        return self._loop_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("magnetic_loop.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> MagneticLoopParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
