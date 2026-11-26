# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided Moxon rectangle generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.moxon import MoxonParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.moxon_form import MoxonForm


class MoxonDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: MoxonParameters | None = None,
    ) -> None:
        form = MoxonForm(
            translator,
            unit_system,
            parameters,
            None,
            wide_layout=True,
        )
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("moxon.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("moxon.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("moxon.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(920, 640),
            parent=parent,
        )
        self._translator = translator
        self._moxon_form = form
        self._parameters: MoxonParameters | None = None
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> MoxonParameters:
        return self._moxon_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("moxon.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> MoxonParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
