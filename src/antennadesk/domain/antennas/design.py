# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Supported antenna design parameter types."""

from __future__ import annotations

from dataclasses import replace

from .custom import ANTENNA_TYPE_CUSTOM, CustomAntennaParameters
from .dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from .folded_dipole import ANTENNA_TYPE_FOLDED_DIPOLE, FoldedDipoleParameters
from .loop import ANTENNA_TYPE_LOOP, LoopParameters

AntennaDesignParameters = (
    DipoleParameters | FoldedDipoleParameters | LoopParameters | CustomAntennaParameters
)


def antenna_type_for(parameters: AntennaDesignParameters) -> str:
    if isinstance(parameters, DipoleParameters):
        return ANTENNA_TYPE_WIRE_DIPOLE
    if isinstance(parameters, FoldedDipoleParameters):
        return ANTENNA_TYPE_FOLDED_DIPOLE
    if isinstance(parameters, LoopParameters):
        return ANTENNA_TYPE_LOOP
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
    raise TypeError(f"antenna has no single primary dimension: {type(parameters)!r}")
