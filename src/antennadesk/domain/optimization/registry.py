# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exhaustive family optimizer registry.

There is deliberately no generic fallback: every parameter type either returns
a descriptor or an explicit unavailable reason.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..antennas.beverage import BeverageParameters
from ..antennas.biquad import BiquadParameters
from ..antennas.custom import CustomAntennaParameters
from ..antennas.design import AntennaDesignParameters
from ..antennas.dipole import DipoleParameters
from ..antennas.endfed import EndFedParameters, EndFedPreset
from ..antennas.fan_dipole import FanDipoleParameters
from ..antennas.folded_dipole import FoldedDipoleParameters
from ..antennas.inverted_l import InvertedLParameters
from ..antennas.inverted_v import InvertedVParameters
from ..antennas.j_pole import JPoleParameters
from ..antennas.loaded_dipole import LoadedDipoleParameters
from ..antennas.loop import LoopParameters
from ..antennas.magnetic_loop import MagneticLoopParameters
from ..antennas.moxon import MoxonParameters
from ..antennas.ocfd import OCFDParameters
from ..antennas.phased_vertical import PhasedVerticalParameters
from ..antennas.quad_beam import QuadBeamParameters
from ..antennas.ringo import RingoParameters
from ..antennas.scv import ScvParameters
from ..antennas.t2fd import T2FDParameters
from ..antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ..antennas.trap_dipole import TrapDipoleParameters
from ..antennas.vertical import VerticalParameters
from ..antennas.yagi import YagiParameters
from ..antennas.zepp import ZeppParameters
from .descriptor import AntennaOptimizerDescriptor
from .families.dipole import dipole_descriptor
from .families.scv import scv_descriptor
from .families.typed import (
    beverage_descriptor,
    biquad_descriptor,
    endfed_descriptor,
    fan_dipole_descriptor,
    folded_dipole_descriptor,
    inverted_l_descriptor,
    inverted_v_descriptor,
    j_pole_descriptor,
    loaded_dipole_descriptor,
    loop_descriptor,
    moxon_descriptor,
    ocfd_descriptor,
    phased_vertical_descriptor,
    quad_beam_descriptor,
    ringo_descriptor,
    t2fd_descriptor,
    transmission_line_doublet_descriptor,
    trap_dipole_descriptor,
    zepp_descriptor,
)
from .families.vertical import vertical_descriptor
from .families.yagi import yagi_descriptor

_REASON_PENDING = "optimize.unavailable.pending_family"
_REASON_MAGNETIC_LOOP = "optimize.unavailable.magnetic_loop"
_REASON_RANDOM_WIRE = "optimize.unavailable.random_wire"
_REASON_CUSTOM_GENERATOR = "optimize.unavailable.custom_generator"
_REASON_CUSTOM_GEOMETRY = "optimize.unavailable.custom_geometry"
_REASON_UNSUPPORTED = "optimize.unavailable.unsupported"


@dataclass(frozen=True, slots=True)
class OptimizerAvailability:
    descriptor: AntennaOptimizerDescriptor | None = None
    reason_key: str | None = None

    def __post_init__(self) -> None:
        if (self.descriptor is None) == (self.reason_key is None):
            raise ValueError("provide exactly one of descriptor or reason_key")

    @property
    def available(self) -> bool:
        return self.descriptor is not None


def optimizer_availability(
    parameters: AntennaDesignParameters,
) -> OptimizerAvailability:
    if isinstance(parameters, DipoleParameters):
        return OptimizerAvailability(descriptor=dipole_descriptor(parameters))
    if isinstance(parameters, VerticalParameters):
        return OptimizerAvailability(descriptor=vertical_descriptor(parameters))
    if isinstance(parameters, YagiParameters):
        return OptimizerAvailability(descriptor=yagi_descriptor(parameters))
    if isinstance(parameters, ScvParameters):
        return OptimizerAvailability(descriptor=scv_descriptor(parameters))
    if isinstance(parameters, BiquadParameters):
        return OptimizerAvailability(descriptor=biquad_descriptor(parameters))
    if isinstance(parameters, BeverageParameters):
        return OptimizerAvailability(descriptor=beverage_descriptor(parameters))
    if isinstance(parameters, LoadedDipoleParameters):
        return OptimizerAvailability(descriptor=loaded_dipole_descriptor(parameters))
    if isinstance(parameters, PhasedVerticalParameters):
        return OptimizerAvailability(descriptor=phased_vertical_descriptor(parameters))
    if isinstance(parameters, QuadBeamParameters):
        return OptimizerAvailability(descriptor=quad_beam_descriptor(parameters))
    if isinstance(parameters, FoldedDipoleParameters):
        return OptimizerAvailability(descriptor=folded_dipole_descriptor(parameters))
    if isinstance(parameters, LoopParameters):
        return OptimizerAvailability(descriptor=loop_descriptor(parameters))
    if isinstance(parameters, InvertedVParameters):
        return OptimizerAvailability(descriptor=inverted_v_descriptor(parameters))
    if isinstance(parameters, InvertedLParameters):
        return OptimizerAvailability(descriptor=inverted_l_descriptor(parameters))
    if isinstance(parameters, JPoleParameters):
        return OptimizerAvailability(descriptor=j_pole_descriptor(parameters))
    if isinstance(parameters, RingoParameters):
        return OptimizerAvailability(descriptor=ringo_descriptor(parameters))
    if isinstance(parameters, OCFDParameters):
        return OptimizerAvailability(descriptor=ocfd_descriptor(parameters))
    if isinstance(parameters, EndFedParameters):
        if parameters.preset is EndFedPreset.RANDOM_WIRE:
            return OptimizerAvailability(reason_key=_REASON_RANDOM_WIRE)
        return OptimizerAvailability(descriptor=endfed_descriptor(parameters))
    if isinstance(parameters, FanDipoleParameters):
        return OptimizerAvailability(descriptor=fan_dipole_descriptor(parameters))
    if isinstance(parameters, TrapDipoleParameters):
        return OptimizerAvailability(descriptor=trap_dipole_descriptor(parameters))
    if isinstance(parameters, T2FDParameters):
        return OptimizerAvailability(descriptor=t2fd_descriptor(parameters))
    if isinstance(parameters, MoxonParameters):
        return OptimizerAvailability(descriptor=moxon_descriptor(parameters))
    if isinstance(parameters, TransmissionLineDoubletParameters):
        return OptimizerAvailability(descriptor=transmission_line_doublet_descriptor(parameters))
    if isinstance(parameters, ZeppParameters):
        return OptimizerAvailability(descriptor=zepp_descriptor(parameters))
    if isinstance(parameters, MagneticLoopParameters):
        return OptimizerAvailability(reason_key=_REASON_MAGNETIC_LOOP)
    if isinstance(parameters, CustomAntennaParameters):
        if parameters.generator_id is not None:
            return OptimizerAvailability(reason_key=_REASON_CUSTOM_GENERATOR)
        return OptimizerAvailability(reason_key=_REASON_CUSTOM_GEOMETRY)
    return OptimizerAvailability(reason_key=_REASON_UNSUPPORTED)  # type: ignore[unreachable]


SUPPORTED_OPTIMIZER_TYPES = frozenset(
    {
        DipoleParameters,
        FoldedDipoleParameters,
        LoopParameters,
        VerticalParameters,
        InvertedVParameters,
        InvertedLParameters,
        JPoleParameters,
        RingoParameters,
        ScvParameters,
        BiquadParameters,
        BeverageParameters,
        LoadedDipoleParameters,
        PhasedVerticalParameters,
        QuadBeamParameters,
        OCFDParameters,
        EndFedParameters,
        FanDipoleParameters,
        TrapDipoleParameters,
        T2FDParameters,
        YagiParameters,
        MoxonParameters,
        TransmissionLineDoubletParameters,
        ZeppParameters,
    }
)

KNOWN_UNAVAILABLE_TYPES = frozenset(
    {
        MagneticLoopParameters,
        CustomAntennaParameters,
    }
)

KNOWN_PARAMETER_TYPES = SUPPORTED_OPTIMIZER_TYPES | KNOWN_UNAVAILABLE_TYPES

# Kept public for exhaustive registry tests and future phases.
OPTIMIZER_REASON_KEYS = frozenset(
    {
        _REASON_PENDING,
        _REASON_MAGNETIC_LOOP,
        _REASON_RANDOM_WIRE,
        _REASON_CUSTOM_GENERATOR,
        _REASON_CUSTOM_GEOMETRY,
        _REASON_UNSUPPORTED,
    }
)
