# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided Beverage receiving-antenna generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QWidget

from ...domain.antennas.beverage import BeverageParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.beverage_form import BeverageForm
from ..widgets.form_dialog import FormDialogFrame


class BeverageDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: BeverageParameters | None = None,
    ) -> None:
        form = BeverageForm(
            translator,
            unit_system,
            parameters,
            None,
            wide_layout=True,
        )
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
            form.load_starting_dimensions()
        hint = QLabel(translator.t("beverage.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("beverage.evidence"))
        evidence.setWordWrap(True)
        starting = QPushButton(translator.t("beverage.load_starting"))
        starting.setToolTip(translator.t("beverage.load_starting_hint"))
        starting.clicked.connect(form.load_starting_dimensions)

        super().__init__(
            title=translator.t("beverage.title"),
            form=form,
            notes=(starting, hint, evidence),
            initial_size=(920, 640),
            parent=parent,
        )
        self._translator = translator
        self._beverage_form = form
        self._parameters: BeverageParameters | None = None
        self._hint = hint
        self._evidence = evidence
        self._starting = starting

    def parameters(self) -> BeverageParameters:
        return self._beverage_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("beverage.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> BeverageParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
