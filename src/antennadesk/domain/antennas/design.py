# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Supported antenna design parameter types."""

from __future__ import annotations

from dataclasses import replace

from .custom import ANTENNA_TYPE_CUSTOM, CustomAntennaParameters
from .dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from .endfed import ANTENNA_TYPE_ENDFED, EndFedParameters
from .fan_dipole import ANTENNA_TYPE_FAN_DIPOLE, FanDipoleParameters
from .folded_dipole import ANTENNA_TYPE_FOLDED_DIPOLE, FoldedDipoleParameters
from .inverted_v import ANTENNA_TYPE_INVERTED_V, InvertedVParameters
from .j_pole import ANTENNA_TYPE_J_POLE, JPoleParameters
from .loop import ANTENNA_TYPE_LOOP, LoopParameters
from .moxon import ANTENNA_TYPE_MOXON, MoxonParameters
from .ocfd import ANTENNA_TYPE_OCFD, OCFDParameters
from .ringo import ANTENNA_TYPE_RINGO, RingoParameters
from .vertical import ANTENNA_TYPE_VERTICAL, VerticalParameters
from .yagi import ANTENNA_TYPE_YAGI, YagiParameters

AntennaDesignParameters = (
    DipoleParameters
    | FoldedDipoleParameters
    | LoopParameters
    | OCFDParameters
    | VerticalParameters
    | InvertedVParameters
    | YagiParameters
    | MoxonParameters
    | FanDipoleParameters
    | EndFedParameters
    | JPoleParameters
    | RingoParameters
    | CustomAntennaParameters
)


def antenna_type_for(parameters: AntennaDesignParameters) -> str:
    if isinstance(parameters, DipoleParameters):
        return ANTENNA_TYPE_WIRE_DIPOLE
    if isinstance(parameters, FoldedDipoleParameters):
        return ANTENNA_TYPE_FOLDED_DIPOLE
    if isinstance(parameters, LoopParameters):
        return ANTENNA_TYPE_LOOP
    if isinstance(parameters, OCFDParameters):
        return ANTENNA_TYPE_OCFD
    if isinstance(parameters, VerticalParameters):
        return ANTENNA_TYPE_VERTICAL
    if isinstance(parameters, InvertedVParameters):
        return ANTENNA_TYPE_INVERTED_V
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
    raise TypeError(f"antenna has no single primary dimension: {type(parameters)!r}")
