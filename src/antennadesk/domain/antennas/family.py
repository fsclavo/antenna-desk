# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Antenna families and template identifiers."""

from __future__ import annotations

from enum import StrEnum

from .custom import CustomAntennaParameters
from .design import AntennaDesignParameters
from .dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from .folded_dipole import ANTENNA_TYPE_FOLDED_DIPOLE, FoldedDipoleParameters
from .inverted_v import InvertedVParameters
from .loop import ANTENNA_TYPE_LOOP, LoopParameters
from .ocfd import OCFDParameters
from .vertical import VerticalParameters
from .yagi import YagiParameters


class AntennaFamily(StrEnum):
    DIPOLE = "dipole"
    YAGI = "yagi"
    LOOP = "loop"
    VERTICAL = "vertical"
    CUSTOM = "custom"


_GENERATOR_FAMILIES: dict[str, AntennaFamily] = {
    "inverted_v": AntennaFamily.DIPOLE,
    "ocfd": AntennaFamily.DIPOLE,
    "yagi": AntennaFamily.YAGI,
    "vertical": AntennaFamily.VERTICAL,
}


def antenna_family(parameters: AntennaDesignParameters) -> AntennaFamily:
    if isinstance(parameters, (DipoleParameters, FoldedDipoleParameters)):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, LoopParameters):
        return AntennaFamily.LOOP
    if isinstance(parameters, OCFDParameters):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, VerticalParameters):
        return AntennaFamily.VERTICAL
    if isinstance(parameters, InvertedVParameters):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, YagiParameters):
        return AntennaFamily.YAGI
    if isinstance(parameters, CustomAntennaParameters):
        if parameters.generator_id is not None:
            return _GENERATOR_FAMILIES.get(parameters.generator_id, AntennaFamily.CUSTOM)
        return AntennaFamily.CUSTOM
    raise TypeError(f"unsupported antenna parameters: {type(parameters)!r}")


def antenna_template_id(parameters: AntennaDesignParameters) -> str:
    if isinstance(parameters, DipoleParameters):
        return ANTENNA_TYPE_WIRE_DIPOLE
    if isinstance(parameters, FoldedDipoleParameters):
        return ANTENNA_TYPE_FOLDED_DIPOLE
    if isinstance(parameters, LoopParameters):
        return ANTENNA_TYPE_LOOP
    if isinstance(parameters, OCFDParameters):
        return "ocfd"
    if isinstance(parameters, VerticalParameters):
        return "vertical"
    if isinstance(parameters, InvertedVParameters):
        return "inverted_v"
    if isinstance(parameters, YagiParameters):
        return "yagi"
    if isinstance(parameters, CustomAntennaParameters):
        return parameters.generator_id or "custom"
    raise TypeError(f"unsupported antenna parameters: {type(parameters)!r}")
