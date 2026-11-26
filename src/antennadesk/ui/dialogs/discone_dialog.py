# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided discone generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.discone import DisconeParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.discone_form import DisconeForm
from ..widgets.form_dialog import FormDialogFrame


class DisconeDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: DisconeParameters | None = None,
    ) -> None:
        form = DisconeForm(translator, unit_system, parameters, None)
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
            form.load_starting_dimensions()
        hint = QLabel(translator.t("discone.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("discone.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("discone.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(560, 780),
            parent=parent,
        )
        self._translator = translator
        self._discone_form = form
        self._parameters: DisconeParameters | None = None
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> DisconeParameters:
        return self._discone_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(
                self,
                self._translator.t("discone.title"),
                str(exc),
            )
            return
        self.accept()

    def result_parameters(self) -> DisconeParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
