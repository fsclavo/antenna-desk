# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Supported antenna design parameter types."""

from __future__ import annotations

from dataclasses import replace

from .beverage import ANTENNA_TYPE_BEVERAGE, BeverageParameters
from .biquad import (
    ANTENNA_TYPE_BIQUAD,
    ANTENNA_TYPE_DOUBLE_BIQUAD,
    BiquadKind,
    BiquadParameters,
)
from .custom import ANTENNA_TYPE_CUSTOM, CustomAntennaParameters
from .dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from .endfed import ANTENNA_TYPE_ENDFED, EndFedParameters
from .fan_dipole import ANTENNA_TYPE_FAN_DIPOLE, FanDipoleParameters
from .folded_dipole import ANTENNA_TYPE_FOLDED_DIPOLE, FoldedDipoleParameters
from .inverted_l import ANTENNA_TYPE_INVERTED_L, InvertedLParameters
from .inverted_v import ANTENNA_TYPE_INVERTED_V, InvertedVParameters
from .j_pole import ANTENNA_TYPE_J_POLE, JPoleParameters
from .loaded_dipole import ANTENNA_TYPE_LOADED_DIPOLE, LoadedDipoleParameters
from .loop import ANTENNA_TYPE_LOOP, LoopParameters
from .magnetic_loop import ANTENNA_TYPE_MAGNETIC_LOOP, MagneticLoopParameters
from .moxon import ANTENNA_TYPE_MOXON, MoxonParameters
from .ocfd import ANTENNA_TYPE_OCFD, OCFDParameters
from .ringo import ANTENNA_TYPE_RINGO, RingoParameters
from .scv import (
    ANTENNA_TYPE_BOBTAIL_CURTAIN,
    ANTENNA_TYPE_HALF_SQUARE,
    ScvKind,
    ScvParameters,
)
from .t2fd import ANTENNA_TYPE_T2FD, T2FDParameters
from .transmission_line_doublet import (
    ANTENNA_TYPE_G5RV,
    ANTENNA_TYPE_ZS6BKW,
    DoubletPreset,
    TransmissionLineDoubletParameters,
)
from .trap_dipole import ANTENNA_TYPE_TRAP_DIPOLE, TrapDipoleParameters
from .vertical import ANTENNA_TYPE_VERTICAL, VerticalParameters
from .yagi import ANTENNA_TYPE_YAGI, YagiParameters
from .zepp import ANTENNA_TYPE_ZEPP, ZeppParameters

AntennaDesignParameters = (
    DipoleParameters
    | FoldedDipoleParameters
    | LoopParameters
    | MagneticLoopParameters
    | OCFDParameters
    | VerticalParameters
    | InvertedVParameters
    | InvertedLParameters
    | YagiParameters
    | MoxonParameters
    | FanDipoleParameters
    | EndFedParameters
    | JPoleParameters
    | RingoParameters
    | ScvParameters
    | BiquadParameters
    | BeverageParameters
    | LoadedDipoleParameters
    | T2FDParameters
    | TransmissionLineDoubletParameters
    | TrapDipoleParameters
    | ZeppParameters
    | CustomAntennaParameters
)


def template_load_ids(parameters: AntennaDesignParameters) -> frozenset[str]:
    """Return load identifiers managed by the parameter template."""

    if isinstance(parameters, VerticalParameters):
        return parameters.managed_load_ids
    if isinstance(parameters, (T2FDParameters, TrapDipoleParameters)):
        return parameters.managed_load_ids
    if isinstance(parameters, (BeverageParameters, LoadedDipoleParameters)):
        return parameters.managed_load_ids
    return frozenset()


def antenna_type_for(parameters: AntennaDesignParameters) -> str:
    if isinstance(parameters, DipoleParameters):
        return ANTENNA_TYPE_WIRE_DIPOLE
    if isinstance(parameters, FoldedDipoleParameters):
        return ANTENNA_TYPE_FOLDED_DIPOLE
    if isinstance(parameters, LoopParameters):
        return ANTENNA_TYPE_LOOP
    if isinstance(parameters, MagneticLoopParameters):
        return ANTENNA_TYPE_MAGNETIC_LOOP
    if isinstance(parameters, OCFDParameters):
        return ANTENNA_TYPE_OCFD
    if isinstance(parameters, VerticalParameters):
        return ANTENNA_TYPE_VERTICAL
    if isinstance(parameters, InvertedVParameters):
        return ANTENNA_TYPE_INVERTED_V
    if isinstance(parameters, InvertedLParameters):
        return ANTENNA_TYPE_INVERTED_L
    if isinstance(parameters, YagiParameters):
        return ANTENNA_TYPE_YAGI
    if isinstance(parameters, MoxonParameters):
        return ANTENNA_TYPE_MOXON
    if isinstance(parameters, FanDipoleParameters):
        return ANTENNA_TYPE_FAN_DIPOLE
    if isinstance(parameters, EndFedParameters):
        return ANTENNA_TYPE_ENDFED
    if isinstance(parameters, JPoleParameters):
        return ANTENNA_TYPE_J_POLE
    if isinstance(parameters, RingoParameters):
        return ANTENNA_TYPE_RINGO
    if isinstance(parameters, ScvParameters):
        return (
            ANTENNA_TYPE_HALF_SQUARE
            if parameters.kind is ScvKind.HALF_SQUARE
            else ANTENNA_TYPE_BOBTAIL_CURTAIN
        )
    if isinstance(parameters, BiquadParameters):
        return (
            ANTENNA_TYPE_BIQUAD
            if parameters.kind is BiquadKind.SINGLE
            else ANTENNA_TYPE_DOUBLE_BIQUAD
        )
    if isinstance(parameters, BeverageParameters):
        return ANTENNA_TYPE_BEVERAGE
    if isinstance(parameters, LoadedDipoleParameters):
        return ANTENNA_TYPE_LOADED_DIPOLE
    if isinstance(parameters, TrapDipoleParameters):
        return ANTENNA_TYPE_TRAP_DIPOLE
    if isinstance(parameters, T2FDParameters):
        return ANTENNA_TYPE_T2FD
    if isinstance(parameters, TransmissionLineDoubletParameters):
        return ANTENNA_TYPE_G5RV if parameters.preset is DoubletPreset.G5RV else ANTENNA_TYPE_ZS6BKW
    if isinstance(parameters, ZeppParameters):
        return ANTENNA_TYPE_ZEPP
    if isinstance(parameters, CustomAntennaParameters):
        return ANTENNA_TYPE_CUSTOM
    raise TypeError(f"unsupported antenna parameters: {type(parameters)!r}")


def primary_dimension_m(parameters: AntennaDesignParameters) -> float:
    if isinstance(parameters, DipoleParameters):
        return parameters.total_length_m
    if isinstance(parameters, FoldedDipoleParameters):
        return parameters.total_length_m
    if isinstance(parameters, LoopParameters):
        return parameters.circumference_m
    if isinstance(parameters, OCFDParameters):
        return parameters.total_length_m
    if isinstance(parameters, VerticalParameters):
        return parameters.height_m
    if isinstance(parameters, InvertedVParameters):
        return parameters.leg_length_m
    if isinstance(parameters, ScvParameters):
        return parameters.horizontal_length_m
    if isinstance(parameters, BiquadParameters):
        return parameters.loop_side_m
    if isinstance(parameters, BeverageParameters):
        return parameters.length_m
    if isinstance(parameters, LoadedDipoleParameters):
        return parameters.active_length_m
    if isinstance(parameters, EndFedParameters):
        return parameters.length_m
    if isinstance(parameters, TrapDipoleParameters):
        return parameters.total_length_m
    if isinstance(parameters, T2FDParameters):
        return parameters.length_m
    if isinstance(parameters, TransmissionLineDoubletParameters):
        return parameters.dipole_total_length_m
    if isinstance(parameters, ZeppParameters):
        return parameters.radiator_length_m
    raise TypeError(f"antenna has no single primary dimension: {type(parameters)!r}")


def with_primary_dimension(
    parameters: AntennaDesignParameters,
    dimension_m: float,
) -> AntennaDesignParameters:
    if isinstance(parameters, DipoleParameters):
        return parameters.with_length(dimension_m)
    if isinstance(parameters, FoldedDipoleParameters):
        return replace(parameters, total_length_m=dimension_m)
    if isinstance(parameters, LoopParameters):
        return replace(parameters, circumference_m=dimension_m)
    if isinstance(parameters, OCFDParameters):
        return parameters.with_length(dimension_m)
    if isinstance(parameters, VerticalParameters):
        return replace(parameters, height_m=dimension_m)
    if isinstance(parameters, InvertedVParameters):
        return replace(parameters, leg_length_m=dimension_m)
    if isinstance(parameters, ScvParameters):
        return replace(parameters, horizontal_length_m=dimension_m)
    if isinstance(parameters, BiquadParameters):
        ratio = dimension_m / parameters.loop_side_m
        return replace(
            parameters,
            loop_side_m=dimension_m,
            reflector_spacing_m=parameters.reflector_spacing_m * ratio,
        )
    if isinstance(parameters, BeverageParameters):
        return replace(parameters, length_m=dimension_m)
    if isinstance(parameters, LoadedDipoleParameters):
        if parameters.link_open:
            return replace(
                parameters,
                link_offset_m=dimension_m / 2.0,
                total_length_m=max(parameters.total_length_m, dimension_m),
            )
        return replace(parameters, total_length_m=dimension_m)
    if isinstance(parameters, EndFedParameters):
        return replace(parameters, length_m=dimension_m)
    if isinstance(parameters, TrapDipoleParameters):
        return parameters.with_total_length(dimension_m)
    if isinstance(parameters, T2FDParameters):
        return parameters.with_length(dimension_m)
    if isinstance(parameters, TransmissionLineDoubletParameters):
        return replace(parameters, dipole_total_length_m=dimension_m)
    if isinstance(parameters, ZeppParameters):
        return replace(parameters, radiator_length_m=dimension_m)
    raise TypeError(f"antenna has no single primary dimension: {type(parameters)!r}")
