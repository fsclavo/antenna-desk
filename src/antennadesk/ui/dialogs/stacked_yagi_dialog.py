# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided stacked-Yagi generator with an embedded Yagi editor."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.stacked_yagi import StackedYagiParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.stacked_yagi_form import StackedYagiForm


class StackedYagiDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: StackedYagiParameters | None = None,
    ) -> None:
        form = StackedYagiForm(translator, unit_system, parameters, None)
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
            form.load_starting_dimensions()
        hint = QLabel(translator.t("stacked_yagi.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("stacked_yagi.evidence"))
        evidence.setWordWrap(True)
        feed_note = QLabel(translator.t("stacked_yagi.feed_note"))
        feed_note.setWordWrap(True)

        super().__init__(
            title=translator.t("stacked_yagi.title"),
            form=form,
            notes=(feed_note, hint, evidence),
            initial_size=(940, 900),
            parent=parent,
        )
        self._translator = translator
        self._stacked_form = form
        self._parameters: StackedYagiParameters | None = None
        self._hint = hint
        self._evidence = evidence
        self._feed_note = feed_note

    def parameters(self) -> StackedYagiParameters:
        return self._stacked_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(
                self,
                self._translator.t("stacked_yagi.title"),
                str(exc),
            )
            return
        self.accept()

    def result_parameters(self) -> StackedYagiParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
