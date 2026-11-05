# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided two-band trap dipole generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.trap_dipole import TrapDipoleParameters
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.trap_dipole_form import TrapDipoleForm


class TrapDipoleDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: TrapDipoleParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: TrapDipoleParameters | None = None
        self._form = TrapDipoleForm(translator, unit_system, parameters, self)
        if parameters is None and frequency_hz is not None:
            self._form.set_frequency_hz(frequency_hz)
        self._frequency = self._form._frequency
        self._high_band = self._form._high_band
        self._inner_length = self._form._inner_length
        self._outer_length = self._form._outer_length
        self._start = self._form._start
        self._trap_frequency = self._form._trap_frequency
        self._trap_inductance = self._form._trap_inductance
        self._trap_capacitance = self._form._trap_capacitance
        self._height = self._form._height
        self._orientation = self._form._orientation
        self._azimuth = self._form._azimuth
        self._radius = self._form._radius
        self._material = self._form._material
        self._ground = self._form._ground
        self._permittivity = self._form._permittivity
        self._conductivity = self._form._conductivity
        self._geometry = self._form._geometry

        self.setWindowTitle(translator.t("trap_dipole.title"))
        self.resize(*scaled_dialog_size(600, 760))

        self._hint = QLabel(translator.t("trap_dipole.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("trap_dipole.evidence"), self)
        self._evidence.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._form)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll, 1)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addWidget(buttons)

    def parameters(self) -> TrapDipoleParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("trap_dipole.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> TrapDipoleParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
