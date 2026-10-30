# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided inverted-V generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.inverted_v import InvertedVParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.inverted_v_form import InvertedVForm


class InvertedVDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: InvertedVParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: InvertedVParameters | None = None
        self._form = InvertedVForm(translator, unit_system, parameters, self)
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
        self._frequency = self._form._frequency
        self._apex_height = self._form._apex_height
        self._leg_length = self._form._leg_length
        self._included_angle = self._form._included_angle
        self._azimuth = self._form._azimuth
        self._radius = self._form._radius
        self._material = self._form._material
        self._ground = self._form._ground
        self._permittivity = self._form._permittivity
        self._conductivity = self._form._conductivity
        self._geometry = self._form._geometry

        self.setWindowTitle(translator.t("inverted_v.title"))
        self.resize(560, 560)

        self._hint = QLabel(translator.t("inverted_v.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("inverted_v.evidence"), self)
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

    def parameters(self) -> InvertedVParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("inverted_v.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> InvertedVParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
