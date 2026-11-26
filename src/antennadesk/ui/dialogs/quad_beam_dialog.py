# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided quad-beam generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.quad_beam import QuadBeamParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.quad_beam_form import QuadBeamForm


class QuadBeamDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: QuadBeamParameters | None = None,
    ) -> None:
        form = QuadBeamForm(translator, unit_system, parameters, None)
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
            form.load_starting_dimensions()
        hint = QLabel(translator.t("quad_beam.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("quad_beam.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("quad_beam.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(560, 780),
            parent=parent,
        )
        self._translator = translator
        self._quad_form = form
        self._parameters: QuadBeamParameters | None = None
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> QuadBeamParameters:
        return self._quad_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(
                self,
                self._translator.t("quad_beam.title"),
                str(exc),
            )
            return
        self.accept()

    def result_parameters(self) -> QuadBeamParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
