# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided half-wave Flower Pot coax vertical generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QWidget

from ...domain.antennas.flower_pot import FlowerPotParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.flower_pot_form import FlowerPotForm
from ..widgets.form_dialog import FormDialogFrame


class FlowerPotDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: FlowerPotParameters | None = None,
    ) -> None:
        form = FlowerPotForm(translator, unit_system, parameters, None)
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("flower_pot.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("flower_pot.evidence"))
        evidence.setWordWrap(True)
        example_2m = QPushButton(translator.t("flower_pot.load_2m"))
        example_2m.setToolTip(translator.t("flower_pot.load_2m_hint"))
        example_2m.clicked.connect(form.load_2m_example)
        example_6m = QPushButton(translator.t("flower_pot.load_6m"))
        example_6m.setToolTip(translator.t("flower_pot.load_6m_hint"))
        example_6m.clicked.connect(form.load_6m_example)

        super().__init__(
            title=translator.t("flower_pot.title"),
            form=form,
            notes=(example_2m, example_6m, hint, evidence),
            initial_size=(600, 760),
            parent=parent,
        )
        self._translator = translator
        self._flower_pot_form = form
        self._parameters: FlowerPotParameters | None = None
        self._example_2m = example_2m
        self._example_6m = example_6m
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> FlowerPotParameters:
        return self._flower_pot_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("flower_pot.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> FlowerPotParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
