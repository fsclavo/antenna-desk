# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exhaustive family optimizer registry.

There is deliberately no generic fallback: every parameter type either returns
a descriptor or an explicit unavailable reason.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import assert_never

from ..antennas.beverage import BeverageParameters
from ..antennas.biquad import BiquadParameters
from ..antennas.custom import CustomAntennaParameters
from ..antennas.design import AntennaDesignParameters
from ..antennas.dipole import DipoleParameters
from ..antennas.discone import DisconeParameters
from ..antennas.endfed import EndFedParameters, EndFedPreset
from ..antennas.fan_dipole import FanDipoleParameters
from ..antennas.folded_dipole import FoldedDipoleParameters
from ..antennas.hexbeam import HexbeamParameters
from ..antennas.inverted_l import InvertedLParameters
from ..antennas.inverted_v import InvertedVParameters
from ..antennas.j_pole import JPoleParameters
from ..antennas.loaded_dipole import LoadedDipoleParameters
from ..antennas.log_periodic import LogPeriodicParameters
from ..antennas.loop import LoopParameters
from ..antennas.magnetic_loop import MagneticLoopParameters
from ..antennas.moxon import MoxonParameters
from ..antennas.ocfd import OCFDParameters
from ..antennas.phased_vertical import PhasedVerticalParameters
from ..antennas.quad_beam import QuadBeamParameters
from ..antennas.ringo import RingoParameters
from ..antennas.scv import ScvParameters
from ..antennas.stacked_yagi import StackedYagiParameters
from ..antennas.t2fd import T2FDParameters
from ..antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ..antennas.trap_dipole import TrapDipoleParameters
from ..antennas.trap_yagi import TrapYagiParameters
from ..antennas.vertical import VerticalParameters
from ..antennas.yagi import YagiParameters, yagi_gross_frequency_mismatch
from ..antennas.zepp import ZeppParameters
from .descriptor import AntennaOptimizerDescriptor, OptimizerBoundsError
from .families.dipole import dipole_descriptor
from .families.scv import scv_descriptor
from .families.stacked_yagi import stacked_yagi_descriptor
from .families.typed import (
    beverage_descriptor,
    biquad_descriptor,
    discone_descriptor,
    endfed_descriptor,
    fan_dipole_descriptor,
    folded_dipole_descriptor,
    hexbeam_band_descriptor,
    hexbeam_descriptor,
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
    trap_yagi_descriptor,
    zepp_descriptor,
)
from .families.vertical import vertical_descriptor
from .families.yagi import yagi_descriptor

_REASON_PENDING = "optimize.unavailable.pending_family"
_REASON_STACKED_YAGI_ENVELOPE = "optimize.unavailable.stacked_yagi_envelope"
_REASON_MAGNETIC_LOOP = "optimize.unavailable.magnetic_loop"
_REASON_LOG_PERIODIC = "optimize.unavailable.log_periodic"
_REASON_RANDOM_WIRE = "optimize.unavailable.random_wire"
_REASON_CUSTOM_GENERATOR = "optimize.unavailable.custom_generator"
_REASON_CUSTOM_GEOMETRY = "optimize.unavailable.custom_geometry"
_REASON_HEXBEAM_MULTIBAND = "optimize.unavailable.hexbeam_multiband"
_REASON_FREQUENCY_MISMATCH = "optimize.unavailable.frequency_mismatch"
_REASON_UNSUPPORTED = "optimize.unavailable.unsupported"


@dataclass(frozen=True, slots=True)
class OptimizerAvailability:
    descriptor: AntennaOptimizerDescriptor | None = None
    reason_key: str | None = None
    reason_values: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if (self.descriptor is None) == (self.reason_key is None):
            raise ValueError("provide exactly one of descriptor or reason_key")
        if self.reason_values and self.reason_key is None:
            raise ValueError("reason values require a reason key")
        object.__setattr__(self, "reason_values", dict(self.reason_values))

    @property
    def available(self) -> bool:
        return self.descriptor is not None


def optimizer_availability(
    parameters: AntennaDesignParameters,
    *,
    hexbeam_band: str | None = None,
) -> OptimizerAvailability:
    try:
        return _optimizer_availability(parameters, hexbeam_band=hexbeam_band)
    except OptimizerBoundsError as exc:
        return OptimizerAvailability(
            reason_key=exc.reason_key,
            reason_values=exc.reason_values,
        )


def _optimizer_availability(
    parameters: AntennaDesignParameters,
    *,
    hexbeam_band: str | None = None,
) -> OptimizerAvailability:
    if isinstance(parameters, DipoleParameters):
        return OptimizerAvailability(descriptor=dipole_descriptor(parameters))
    if isinstance(parameters, VerticalParameters):
        return OptimizerAvailability(descriptor=vertical_descriptor(parameters))
    if isinstance(parameters, YagiParameters):
        descriptor = yagi_descriptor(parameters)
        mismatch = yagi_gross_frequency_mismatch(parameters)
        if mismatch is not None:
            index, ratio = mismatch
            return OptimizerAvailability(
                reason_key=_REASON_FREQUENCY_MISMATCH,
                reason_values={
                    "family": "yagi",
                    "element": index + 1,
                    "wavelength_ratio": f"{ratio:.3g}",
                },
            )
        return OptimizerAvailability(descriptor=descriptor)
    if isinstance(parameters, StackedYagiParameters):
        maximum_spacing = parameters.maximum_spacing_m
        if maximum_spacing is None or maximum_spacing <= parameters.minimum_spacing_m:
            return OptimizerAvailability(reason_key=_REASON_STACKED_YAGI_ENVELOPE)
        return OptimizerAvailability(descriptor=stacked_yagi_descriptor(parameters))
    if isinstance(parameters, ScvParameters):
        return OptimizerAvailability(descriptor=scv_descriptor(parameters))
    if isinstance(parameters, BiquadParameters):
        return OptimizerAvailability(descriptor=biquad_descriptor(parameters))
    if isinstance(parameters, BeverageParameters):
        return OptimizerAvailability(descriptor=beverage_descriptor(parameters))
    if isinstance(parameters, LoadedDipoleParameters):
        return OptimizerAvailability(descriptor=loaded_dipole_descriptor(parameters))
    if isinstance(parameters, DisconeParameters):
        return OptimizerAvailability(descriptor=discone_descriptor(parameters))
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
    if isinstance(parameters, TrapYagiParameters):
        return OptimizerAvailability(descriptor=trap_yagi_descriptor(parameters))
    if isinstance(parameters, HexbeamParameters):
        if parameters.bands:
            if hexbeam_band is not None:
                key = hexbeam_band.casefold()
                for index, band in enumerate(parameters.bands):
                    if band.label.casefold() == key:
                        return OptimizerAvailability(
                            descriptor=hexbeam_band_descriptor(parameters, band, index)
                        )
            return OptimizerAvailability(reason_key=_REASON_HEXBEAM_MULTIBAND)
        return OptimizerAvailability(descriptor=hexbeam_descriptor(parameters))
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
    if isinstance(parameters, LogPeriodicParameters):
        return OptimizerAvailability(reason_key=_REASON_LOG_PERIODIC)
    if isinstance(parameters, CustomAntennaParameters):
        if parameters.generator_id is not None:
            return OptimizerAvailability(reason_key=_REASON_CUSTOM_GENERATOR)
        return OptimizerAvailability(reason_key=_REASON_CUSTOM_GEOMETRY)
    assert_never(parameters)


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
        DisconeParameters,
        PhasedVerticalParameters,
        QuadBeamParameters,
        OCFDParameters,
        EndFedParameters,
        FanDipoleParameters,
        TrapDipoleParameters,
        TrapYagiParameters,
        HexbeamParameters,
        T2FDParameters,
        YagiParameters,
        MoxonParameters,
        TransmissionLineDoubletParameters,
        ZeppParameters,
        StackedYagiParameters,
    }
)

KNOWN_UNAVAILABLE_TYPES = frozenset(
    {
        MagneticLoopParameters,
        LogPeriodicParameters,
        CustomAntennaParameters,
    }
)

KNOWN_PARAMETER_TYPES = SUPPORTED_OPTIMIZER_TYPES | KNOWN_UNAVAILABLE_TYPES

# Kept public for exhaustive registry tests and future phases.
OPTIMIZER_REASON_KEYS = frozenset(
    {
        _REASON_PENDING,
        _REASON_STACKED_YAGI_ENVELOPE,
        _REASON_MAGNETIC_LOOP,
        _REASON_LOG_PERIODIC,
        _REASON_RANDOM_WIRE,
        _REASON_CUSTOM_GENERATOR,
        _REASON_CUSTOM_GEOMETRY,
        _REASON_HEXBEAM_MULTIBAND,
        _REASON_FREQUENCY_MISMATCH,
        _REASON_UNSUPPORTED,
    }
)
