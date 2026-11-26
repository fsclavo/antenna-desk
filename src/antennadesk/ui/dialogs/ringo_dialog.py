# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided Ringo vertical generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QWidget

from ...domain.antennas.ringo import RingoParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.ringo_form import RingoForm


class RingoDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: RingoParameters | None = None,
    ) -> None:
        form = RingoForm(translator, unit_system, parameters, None)
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("ringo.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("ringo.evidence"))
        evidence.setWordWrap(True)
        example = QPushButton(translator.t("ringo.ar6_example"))
        example.setToolTip(translator.t("ringo.ar6_example_hint"))
        example.clicked.connect(form.load_cushcraft_ar6_example)

        super().__init__(
            title=translator.t("ringo.title"),
            form=form,
            notes=(example, hint, evidence),
            initial_size=(560, 620),
            scroll_form=False,
            parent=parent,
        )
        self._translator = translator
        self._ringo_form = form
        self._parameters: RingoParameters | None = None
        self._example = example
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> RingoParameters:
        return self._ringo_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("ringo.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> RingoParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
