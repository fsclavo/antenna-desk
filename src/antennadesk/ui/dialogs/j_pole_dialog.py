# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided J-pole and Slim-Jim generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.j_pole import JPoleParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.j_pole_form import JPoleForm


class JPoleDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: JPoleParameters | None = None,
    ) -> None:
        form = JPoleForm(
            translator,
            unit_system,
            parameters,
            None,
            wide_layout=True,
        )
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("j_pole.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("j_pole.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("j_pole.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(920, 640),
            parent=parent,
        )
        self._translator = translator
        self._j_pole_form = form
        self._parameters: JPoleParameters | None = None
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> JPoleParameters:
        return self._j_pole_form.parameters()

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
