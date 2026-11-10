# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Direct editor for the basic wire dipole, folded dipole, and loop templates."""

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

from ...domain.antennas.design import AntennaDesignParameters, antenna_type_for
from ...domain.antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE
from ...domain.antennas.folded_dipole import ANTENNA_TYPE_FOLDED_DIPOLE
from ...domain.antennas.loop import ANTENNA_TYPE_LOOP
from ...domain.design import (
    DesignIntent,
    LoopShape,
    UnsupportedEstimateError,
)
from ...domain.design.estimators import estimate_intent
from ...domain.environment.ground import GroundModel
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.dipole_form import DipoleForm

_TITLE_KEYS = {
    ANTENNA_TYPE_WIRE_DIPOLE: "antenna_type.wire_dipole",
    ANTENNA_TYPE_FOLDED_DIPOLE: "antenna_type.folded_dipole",
    ANTENNA_TYPE_LOOP: "antenna_type.loop",
}

_DESCRIPTION_KEYS = {
    ANTENNA_TYPE_WIRE_DIPOLE: "catalog.wire_dipole.description",
    ANTENNA_TYPE_FOLDED_DIPOLE: "catalog.folded_dipole.description",
    ANTENNA_TYPE_LOOP: "catalog.loop.description",
}


def _loop_shape(initial_sides: int | None) -> LoopShape:
    if initial_sides == 3:
        return LoopShape.DELTA
    if initial_sides == 4:
        return LoopShape.QUAD
    return LoopShape.LOOP


def _starting_parameters(
    antenna_type: str,
    frequency_hz: float,
    initial_sides: int | None,
) -> AntennaDesignParameters | None:
    """Build a frequency-aware starting point with the standard field defaults."""

    intent = DesignIntent(
        frequency_hz=frequency_hz,
        antenna_type=antenna_type,
        height_m=8.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
        loop_shape=_loop_shape(initial_sides),
    )
    try:
        return estimate_intent(intent).parameters
    except UnsupportedEstimateError:
        return None


class BasicAntennaDialog(QDialog):
    """Edit the variables of a basic dipole, folded dipole, or loop directly."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        antenna_type: str = ANTENNA_TYPE_WIRE_DIPOLE,
        frequency_hz: float = 7_100_000.0,
        initial_sides: int | None = None,
        parameters: AntennaDesignParameters | None = None,
    ) -> None:
        super().__init__(parent)
        if parameters is not None:
            antenna_type = antenna_type_for(parameters)
        if antenna_type not in _TITLE_KEYS:
            raise ValueError(f"unsupported basic antenna type: {antenna_type!r}")
        self._translator = translator
        self._parameters: AntennaDesignParameters | None = None
        self._form = DipoleForm(translator, unit_system, parent=self)
        self._form.set_template_header_visible(False)
        if parameters is not None:
            self._form.set_parameters(parameters, reset_sweep=True)
        else:
            starting = _starting_parameters(antenna_type, frequency_hz, initial_sides)
            if starting is not None:
                self._form.set_parameters(starting, reset_sweep=True)
            else:
                self._form.set_antenna_type(antenna_type)
                self._form.set_frequency_hz(frequency_hz)
                if antenna_type == ANTENNA_TYPE_LOOP and initial_sides is not None:
                    self._form.set_sides(initial_sides)

        if antenna_type == ANTENNA_TYPE_LOOP and initial_sides == 3:
            title_key = "catalog.delta_loop"
        elif antenna_type == ANTENNA_TYPE_LOOP and initial_sides == 4:
            title_key = "catalog.quad_loop"
        else:
            title_key = _TITLE_KEYS[antenna_type]
        self.setWindowTitle(translator.t(title_key))
        self.resize(*scaled_dialog_size(560, 740))

        self._hint = QLabel(translator.t(_DESCRIPTION_KEYS[antenna_type]), self)
        self._hint.setWordWrap(True)

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
        layout.addWidget(buttons)

    def parameters(self) -> AntennaDesignParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(
                self,
                self.windowTitle(),
                str(exc),
            )
            return
        self.accept()

    def result_parameters(self) -> AntennaDesignParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
