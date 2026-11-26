# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided HexBeam generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.hexbeam import HexbeamParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.hexbeam_form import HexbeamForm


class HexbeamDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: HexbeamParameters | None = None,
    ) -> None:
        form = HexbeamForm(translator, unit_system, parameters, None)
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
            form.load_starting_dimensions()
        hint = QLabel(translator.t("hexbeam.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("hexbeam.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("hexbeam.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(580, 820),
            parent=parent,
        )
        self._translator = translator
        self._hexbeam_form = form
        self._parameters: HexbeamParameters | None = None
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> HexbeamParameters:
        return self._hexbeam_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(
                self,
                self._translator.t("hexbeam.title"),
                str(exc),
            )
            return
        self.accept()

    def result_parameters(self) -> HexbeamParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
