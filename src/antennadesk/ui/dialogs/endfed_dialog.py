# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided end-fed wire generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.endfed import EndFedParameters, EndFedPreset
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.endfed_form import EndFedForm


class EndFedDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: EndFedParameters | None = None,
        preset: EndFedPreset = EndFedPreset.STANDARD,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: EndFedParameters | None = None
        if parameters is not None:
            preset = parameters.preset
        self._form = EndFedForm(
            translator,
            unit_system,
            parameters,
            self,
            preset=preset,
        )
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
        title_key = {
            EndFedPreset.STANDARD: "endfed.title",
            EndFedPreset.SLOPER: "endfed.sloper_title",
            EndFedPreset.RANDOM_WIRE: "endfed.random_wire_title",
        }[preset]
        self.setWindowTitle(translator.t(title_key))
        self.resize(620, 720)

        hint_key = {
            EndFedPreset.STANDARD: "endfed.hint",
            EndFedPreset.SLOPER: "endfed.sloper_hint",
            EndFedPreset.RANDOM_WIRE: "endfed.random_wire_hint",
        }[preset]
        evidence_key = {
            EndFedPreset.STANDARD: "endfed.evidence",
            EndFedPreset.SLOPER: "endfed.sloper_evidence",
            EndFedPreset.RANDOM_WIRE: "endfed.random_wire_evidence",
        }[preset]
        self._hint = QLabel(translator.t(hint_key), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t(evidence_key), self)
        self._evidence.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._form)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addStretch(1)
        layout.addWidget(buttons)

    def parameters(self) -> EndFedParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("endfed.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> EndFedParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
