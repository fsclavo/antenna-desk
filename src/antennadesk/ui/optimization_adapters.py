# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit UI adapters for family optimizers.

The optimizer route never falls back to the basic dipole form. A family must
have an adapter here, or the Optimize action remains disabled.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.dipole import DipoleParameters
from ..domain.antennas.endfed import EndFedParameters
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.folded_dipole import FoldedDipoleParameters
from ..domain.antennas.inverted_l import InvertedLParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.j_pole import JPoleParameters
from ..domain.antennas.loop import LoopParameters
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.scv import ScvParameters
from ..domain.antennas.t2fd import T2FDParameters
from ..domain.antennas.transmission_line_doublet import (
    TransmissionLineDoubletParameters,
)
from ..domain.antennas.trap_dipole import TrapDipoleParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters
from ..domain.antennas.zepp import ZeppParameters
from ..domain.simulation.spec import SimulationSpec


@dataclass(frozen=True, slots=True)
class OptimizationUiAdapter:
    simulation_spec: Callable[[Any, AntennaDesignParameters], SimulationSpec]
    apply_parameters: Callable[[Any, AntennaDesignParameters], None]


ADAPTERS: dict[type[AntennaDesignParameters], OptimizationUiAdapter] = {
    DipoleParameters: OptimizationUiAdapter(
        lambda window, _parameters: window._form.simulation_spec(),
        lambda window, parameters: window._form.set_parameters(parameters, reset_sweep=False),
    ),
    FoldedDipoleParameters: OptimizationUiAdapter(
        lambda window, _parameters: window._form.simulation_spec(),
        lambda window, parameters: window._form.set_parameters(parameters, reset_sweep=False),
    ),
    LoopParameters: OptimizationUiAdapter(
        lambda window, _parameters: window._form.simulation_spec(),
        lambda window, parameters: window._form.set_parameters(parameters, reset_sweep=False),
    ),
    VerticalParameters: OptimizationUiAdapter(
        lambda window, parameters: window._vertical_simulation_spec(parameters),
        lambda window, parameters: window._vertical_form.set_parameters(parameters),
    ),
    InvertedVParameters: OptimizationUiAdapter(
        lambda window, parameters: window._inverted_v_simulation_spec(parameters),
        lambda window, parameters: window._inverted_v_form.set_parameters(parameters),
    ),
    InvertedLParameters: OptimizationUiAdapter(
        lambda window, parameters: window._inverted_l_simulation_spec(parameters),
        lambda window, parameters: window._inverted_l_form.set_parameters(parameters),
    ),
    JPoleParameters: OptimizationUiAdapter(
        lambda window, parameters: window._j_pole_simulation_spec(parameters),
        lambda window, parameters: window._j_pole_form.set_parameters(parameters),
    ),
    RingoParameters: OptimizationUiAdapter(
        lambda window, parameters: window._ringo_simulation_spec(parameters),
        lambda window, parameters: window._ringo_form.set_parameters(parameters),
    ),
    ScvParameters: OptimizationUiAdapter(
        lambda window, parameters: window._scv_simulation_spec(parameters),
        lambda window, parameters: window._scv_form.set_parameters(parameters),
    ),
    OCFDParameters: OptimizationUiAdapter(
        lambda window, parameters: window._ocfd_simulation_spec(parameters),
        lambda window, parameters: window._ocfd_form.set_parameters(parameters),
    ),
    EndFedParameters: OptimizationUiAdapter(
        lambda window, parameters: window._endfed_simulation_spec(parameters),
        lambda window, parameters: window._endfed_form.set_parameters(parameters),
    ),
    FanDipoleParameters: OptimizationUiAdapter(
        lambda window, parameters: window._fan_dipole_simulation_spec(parameters),
        lambda window, parameters: window._fan_dipole_form.set_parameters(parameters),
    ),
    TrapDipoleParameters: OptimizationUiAdapter(
        lambda window, parameters: window._trap_dipole_simulation_spec(parameters),
        lambda window, parameters: window._trap_dipole_form.set_parameters(parameters),
    ),
    T2FDParameters: OptimizationUiAdapter(
        lambda window, parameters: window._t2fd_simulation_spec(parameters),
        lambda window, parameters: window._t2fd_form.set_parameters(parameters),
    ),
    YagiParameters: OptimizationUiAdapter(
        lambda window, parameters: window._yagi_simulation_spec(parameters),
        lambda window, parameters: window._yagi_form.set_parameters(parameters),
    ),
    MoxonParameters: OptimizationUiAdapter(
        lambda window, parameters: window._moxon_simulation_spec(parameters),
        lambda window, parameters: window._moxon_form.set_parameters(parameters),
    ),
    TransmissionLineDoubletParameters: OptimizationUiAdapter(
        lambda window, parameters: window._doublet_simulation_spec(parameters),
        lambda window, parameters: window._doublet_form.set_parameters(parameters),
    ),
    ZeppParameters: OptimizationUiAdapter(
        lambda window, parameters: window._zepp_simulation_spec(parameters),
        lambda window, parameters: window._zepp_form.set_parameters(parameters),
    ),
}


def adapter_for(parameters: AntennaDesignParameters) -> OptimizationUiAdapter | None:
    return ADAPTERS.get(type(parameters))
