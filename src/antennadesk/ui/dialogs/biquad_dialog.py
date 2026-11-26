# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided biquad and double-biquad generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QWidget

from ...domain.antennas.biquad import BiquadKind, BiquadParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.biquad_form import BiquadForm
from ..widgets.form_dialog import FormDialogFrame


class BiquadDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        kind: BiquadKind = BiquadKind.SINGLE,
        frequency_hz: float | None = None,
        parameters: BiquadParameters | None = None,
    ) -> None:
        form = BiquadForm(
            translator,
            unit_system,
            parameters,
            None,
            kind=kind,
            wide_layout=True,
        )
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
            form.load_starting_dimensions()
        hint = QLabel(translator.t("biquad.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("biquad.evidence"))
        evidence.setWordWrap(True)
        starting = QPushButton(translator.t("biquad.load_starting"))
        starting.setToolTip(translator.t("biquad.load_starting_hint"))
        starting.clicked.connect(form.load_starting_dimensions)

        super().__init__(
            title=translator.t("biquad.title"),
            form=form,
            notes=(starting, hint, evidence),
            initial_size=(920, 640),
            parent=parent,
        )
        self._translator = translator
        self._biquad_form = form
        self._parameters: BiquadParameters | None = None
        self._hint = hint
        self._evidence = evidence
        self._starting = starting

    def parameters(self) -> BiquadParameters:
        return self._biquad_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("biquad.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> BiquadParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
