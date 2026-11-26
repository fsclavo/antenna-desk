# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided half-square and bobtail-curtain generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QWidget

from ...domain.antennas.scv import ScvKind, ScvParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.scv_form import ScvForm


class ScvDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        kind: ScvKind = ScvKind.HALF_SQUARE,
        frequency_hz: float | None = None,
        parameters: ScvParameters | None = None,
    ) -> None:
        form = ScvForm(
            translator,
            unit_system,
            parameters,
            None,
            kind=kind,
            wide_layout=True,
        )
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("scv.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("scv.evidence"))
        evidence.setWordWrap(True)
        example = QPushButton(translator.t("scv.load_reference"))
        example.setToolTip(translator.t("scv.load_reference_hint"))
        example.clicked.connect(form.load_reference_example)

        super().__init__(
            title=translator.t("scv.title"),
            form=form,
            notes=(example, hint, evidence),
            initial_size=(920, 640),
            parent=parent,
        )
        self._translator = translator
        self._scv_form = form
        self._parameters: ScvParameters | None = None
        self._hint = hint
        self._evidence = evidence
        self._example = example

    def parameters(self) -> ScvParameters:
        return self._scv_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("scv.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> ScvParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
