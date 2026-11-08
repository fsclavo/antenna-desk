# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Antenna families and template identifiers."""

from __future__ import annotations

from enum import StrEnum

from .beverage import BeverageParameters
from .biquad import BiquadParameters
from .custom import CustomAntennaParameters
from .design import AntennaDesignParameters
from .dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from .discone import DisconeParameters
from .endfed import EndFedParameters
from .fan_dipole import FanDipoleParameters
from .folded_dipole import ANTENNA_TYPE_FOLDED_DIPOLE, FoldedDipoleParameters
from .hexbeam import HexbeamParameters
from .inverted_l import InvertedLParameters
from .inverted_v import InvertedVParameters
from .j_pole import JPoleParameters
from .loaded_dipole import LoadedDipoleParameters
from .loop import ANTENNA_TYPE_LOOP, LoopParameters
from .magnetic_loop import MagneticLoopParameters
from .moxon import MoxonParameters
from .ocfd import OCFDParameters
from .phased_vertical import PhasedVerticalParameters
from .quad_beam import QuadBeamParameters
from .ringo import RingoParameters
from .scv import ScvParameters
from .t2fd import ANTENNA_TYPE_T2FD, T2FDParameters
from .transmission_line_doublet import TransmissionLineDoubletParameters
from .trap_dipole import ANTENNA_TYPE_TRAP_DIPOLE, TrapDipoleParameters
from .trap_yagi import TrapYagiParameters
from .vertical import VerticalParameters
from .yagi import YagiParameters
from .zepp import ZeppParameters


class AntennaFamily(StrEnum):
    DIPOLE = "dipole"
    YAGI = "yagi"
    LOOP = "loop"
    VERTICAL = "vertical"
    WIRE = "wire"
    CUSTOM = "custom"


_GENERATOR_FAMILIES: dict[str, AntennaFamily] = {
    "inverted_v": AntennaFamily.DIPOLE,
    "inverted_l": AntennaFamily.VERTICAL,
    "fan_dipole": AntennaFamily.DIPOLE,
    "endfed": AntennaFamily.DIPOLE,
    "ocfd": AntennaFamily.DIPOLE,
    "yagi": AntennaFamily.YAGI,
    "moxon": AntennaFamily.YAGI,
    "vertical": AntennaFamily.VERTICAL,
    "magnetic_loop": AntennaFamily.LOOP,
    "j_pole": AntennaFamily.VERTICAL,
    "slim_jim": AntennaFamily.VERTICAL,
    "ringo": AntennaFamily.VERTICAL,
    "half_square": AntennaFamily.VERTICAL,
    "bobtail_curtain": AntennaFamily.VERTICAL,
    "biquad": AntennaFamily.LOOP,
    "double_biquad": AntennaFamily.LOOP,
    "beverage": AntennaFamily.WIRE,
    "loaded_dipole": AntennaFamily.DIPOLE,
    "discone": AntennaFamily.VERTICAL,
    "phased_vertical": AntennaFamily.VERTICAL,
    "quad_beam": AntennaFamily.LOOP,
    "hexbeam": AntennaFamily.YAGI,
    "trap_yagi": AntennaFamily.YAGI,
    "trap_dipole": AntennaFamily.DIPOLE,
    "t2fd": AntennaFamily.DIPOLE,
    "g5rv": AntennaFamily.DIPOLE,
    "zs6bkw": AntennaFamily.DIPOLE,
    "zepp": AntennaFamily.DIPOLE,
}


def antenna_family(parameters: AntennaDesignParameters) -> AntennaFamily:
    if isinstance(parameters, (DipoleParameters, FoldedDipoleParameters)):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, LoopParameters):
        return AntennaFamily.LOOP
    if isinstance(parameters, MagneticLoopParameters):
        return AntennaFamily.LOOP
    if isinstance(parameters, OCFDParameters):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, VerticalParameters):
        return AntennaFamily.VERTICAL
    if isinstance(parameters, InvertedVParameters):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, InvertedLParameters):
        return AntennaFamily.VERTICAL
    if isinstance(parameters, YagiParameters):
        return AntennaFamily.YAGI
    if isinstance(parameters, MoxonParameters):
        return AntennaFamily.YAGI
    if isinstance(parameters, FanDipoleParameters):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, EndFedParameters):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, JPoleParameters):
        return AntennaFamily.VERTICAL
    if isinstance(parameters, RingoParameters):
        return AntennaFamily.VERTICAL
    if isinstance(parameters, ScvParameters):
        return AntennaFamily.VERTICAL
    if isinstance(parameters, BiquadParameters):
        return AntennaFamily.LOOP
    if isinstance(parameters, BeverageParameters):
        return AntennaFamily.WIRE
    if isinstance(parameters, LoadedDipoleParameters):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, DisconeParameters):
        return AntennaFamily.VERTICAL
    if isinstance(parameters, PhasedVerticalParameters):
        return AntennaFamily.VERTICAL
    if isinstance(parameters, QuadBeamParameters):
        return AntennaFamily.LOOP
    if isinstance(parameters, HexbeamParameters):
        return AntennaFamily.YAGI
    if isinstance(parameters, T2FDParameters):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, TrapDipoleParameters):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, TrapYagiParameters):
        return AntennaFamily.YAGI
    if isinstance(parameters, TransmissionLineDoubletParameters):
        return AntennaFamily.DIPOLE
    if isinstance(parameters, ZeppParameters):
        return AntennaFamily.DIPOLE
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
    if isinstance(parameters, MagneticLoopParameters):
        return "magnetic_loop"
    if isinstance(parameters, OCFDParameters):
        return "ocfd"
    if isinstance(parameters, VerticalParameters):
        return "vertical"
    if isinstance(parameters, InvertedVParameters):
        return "inverted_v"
    if isinstance(parameters, InvertedLParameters):
        return "inverted_l"
    if isinstance(parameters, YagiParameters):
        return "yagi"
    if isinstance(parameters, MoxonParameters):
        return "moxon"
    if isinstance(parameters, FanDipoleParameters):
        return "fan_dipole"
    if isinstance(parameters, EndFedParameters):
        return parameters.preset.value
    if isinstance(parameters, JPoleParameters):
        return "j_pole"
    if isinstance(parameters, RingoParameters):
        return "ringo"
    if isinstance(parameters, ScvParameters):
        return parameters.kind.value
    if isinstance(parameters, BiquadParameters):
        return parameters.kind.antenna_type
    if isinstance(parameters, BeverageParameters):
        return "beverage"
    if isinstance(parameters, LoadedDipoleParameters):
        return "loaded_dipole"
    if isinstance(parameters, DisconeParameters):
        return "discone"
    if isinstance(parameters, PhasedVerticalParameters):
        return "phased_vertical"
    if isinstance(parameters, QuadBeamParameters):
        return "quad_beam"
    if isinstance(parameters, HexbeamParameters):
        return "hexbeam"
    if isinstance(parameters, TrapDipoleParameters):
        return ANTENNA_TYPE_TRAP_DIPOLE
    if isinstance(parameters, TrapYagiParameters):
        return "trap_yagi"
    if isinstance(parameters, T2FDParameters):
        return ANTENNA_TYPE_T2FD
    if isinstance(parameters, TransmissionLineDoubletParameters):
        return parameters.preset.antenna_type
    if isinstance(parameters, ZeppParameters):
        return "zepp"
    if isinstance(parameters, CustomAntennaParameters):
        return parameters.generator_id or "custom"
    raise TypeError(f"unsupported antenna parameters: {type(parameters)!r}")
