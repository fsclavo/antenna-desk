# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Map canonical design parameters to catalog and label identifiers."""

from __future__ import annotations

from ..domain.antennas.biquad import BiquadKind, BiquadParameters
from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.dipole import DipoleParameters
from ..domain.antennas.endfed import EndFedParameters, EndFedPreset
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.folded_dipole import FoldedDipoleParameters
from ..domain.antennas.inverted_l import InvertedLParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.j_pole import JPoleParameters
from ..domain.antennas.loop import LoopParameters
from ..domain.antennas.magnetic_loop import MagneticLoopParameters
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.scv import ScvKind, ScvParameters
from ..domain.antennas.t2fd import T2FDParameters
from ..domain.antennas.transmission_line_doublet import (
    TransmissionLineDoubletParameters,
)
from ..domain.antennas.trap_dipole import TrapDipoleParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters
from ..domain.antennas.zepp import ZeppParameters
from .dialogs.antenna_catalog_dialog import (
    CATALOG_TYPE_BIQUAD,
    CATALOG_TYPE_BOBTAIL_CURTAIN,
    CATALOG_TYPE_CUSTOM,
    CATALOG_TYPE_DELTA_LOOP,
    CATALOG_TYPE_DOUBLE_BIQUAD,
    CATALOG_TYPE_DOUBLET,
    CATALOG_TYPE_ENDFED,
    CATALOG_TYPE_FAN_DIPOLE,
    CATALOG_TYPE_FOLDED_DIPOLE,
    CATALOG_TYPE_G5RV,
    CATALOG_TYPE_HALF_SQUARE,
    CATALOG_TYPE_INVERTED_L,
    CATALOG_TYPE_INVERTED_V,
    CATALOG_TYPE_J_POLE,
    CATALOG_TYPE_LOADED_VERTICAL,
    CATALOG_TYPE_LOOP,
    CATALOG_TYPE_MAGNETIC_LOOP,
    CATALOG_TYPE_MOXON,
    CATALOG_TYPE_OCFD,
    CATALOG_TYPE_QUAD_LOOP,
    CATALOG_TYPE_RANDOM_WIRE,
    CATALOG_TYPE_RINGO,
    CATALOG_TYPE_SLIM_JIM,
    CATALOG_TYPE_SLOPER,
    CATALOG_TYPE_T2FD,
    CATALOG_TYPE_TRAP_DIPOLE,
    CATALOG_TYPE_VERTICAL,
    CATALOG_TYPE_WIRE_DIPOLE,
    CATALOG_TYPE_YAGI,
    CATALOG_TYPE_ZEPP,
    CATALOG_TYPE_ZS6BKW,
)

_KNOWN_CUSTOM_GENERATORS = frozenset(
    {
        CATALOG_TYPE_DOUBLET,
        CATALOG_TYPE_ENDFED,
        CATALOG_TYPE_FAN_DIPOLE,
        CATALOG_TYPE_G5RV,
        CATALOG_TYPE_INVERTED_V,
        CATALOG_TYPE_J_POLE,
        CATALOG_TYPE_MAGNETIC_LOOP,
        CATALOG_TYPE_MOXON,
        CATALOG_TYPE_OCFD,
        CATALOG_TYPE_RINGO,
        CATALOG_TYPE_HALF_SQUARE,
        CATALOG_TYPE_BOBTAIL_CURTAIN,
        CATALOG_TYPE_BIQUAD,
        CATALOG_TYPE_DOUBLE_BIQUAD,
        CATALOG_TYPE_SLIM_JIM,
        CATALOG_TYPE_T2FD,
        CATALOG_TYPE_TRAP_DIPOLE,
        CATALOG_TYPE_VERTICAL,
        CATALOG_TYPE_YAGI,
        CATALOG_TYPE_ZEPP,
        CATALOG_TYPE_ZS6BKW,
    }
)

_LABEL_KEYS = {
    CATALOG_TYPE_WIRE_DIPOLE: "antenna_type.wire_dipole",
    CATALOG_TYPE_FOLDED_DIPOLE: "antenna_type.folded_dipole",
    CATALOG_TYPE_LOOP: "antenna_type.loop",
}


def catalog_key_for(parameters: AntennaDesignParameters) -> str:
    """Return the catalog entry that best matches the current template."""

    if isinstance(parameters, DipoleParameters):
        return CATALOG_TYPE_WIRE_DIPOLE
    if isinstance(parameters, FoldedDipoleParameters):
        return CATALOG_TYPE_FOLDED_DIPOLE
    if isinstance(parameters, LoopParameters):
        return {
            3: CATALOG_TYPE_DELTA_LOOP,
            4: CATALOG_TYPE_QUAD_LOOP,
        }.get(parameters.sides, CATALOG_TYPE_LOOP)
    if isinstance(parameters, MagneticLoopParameters):
        return CATALOG_TYPE_MAGNETIC_LOOP
    if isinstance(parameters, OCFDParameters):
        return CATALOG_TYPE_OCFD
    if isinstance(parameters, VerticalParameters):
        return (
            CATALOG_TYPE_LOADED_VERTICAL
            if parameters.loading_coil_enabled
            else CATALOG_TYPE_VERTICAL
        )
    if isinstance(parameters, InvertedVParameters):
        return CATALOG_TYPE_INVERTED_V
    if isinstance(parameters, InvertedLParameters):
        return CATALOG_TYPE_INVERTED_L
    if isinstance(parameters, YagiParameters):
        return CATALOG_TYPE_YAGI
    if isinstance(parameters, MoxonParameters):
        return CATALOG_TYPE_MOXON
    if isinstance(parameters, FanDipoleParameters):
        return CATALOG_TYPE_FAN_DIPOLE
    if isinstance(parameters, TrapDipoleParameters):
        return CATALOG_TYPE_TRAP_DIPOLE
    if isinstance(parameters, T2FDParameters):
        return CATALOG_TYPE_T2FD
    if isinstance(parameters, EndFedParameters):
        return {
            EndFedPreset.STANDARD: CATALOG_TYPE_ENDFED,
            EndFedPreset.SLOPER: CATALOG_TYPE_SLOPER,
            EndFedPreset.RANDOM_WIRE: CATALOG_TYPE_RANDOM_WIRE,
        }[parameters.preset]
    if isinstance(parameters, JPoleParameters):
        return CATALOG_TYPE_SLIM_JIM if parameters.folded else CATALOG_TYPE_J_POLE
    if isinstance(parameters, RingoParameters):
        return CATALOG_TYPE_RINGO
    if isinstance(parameters, ScvParameters):
        return (
            CATALOG_TYPE_HALF_SQUARE
            if parameters.kind is ScvKind.HALF_SQUARE
            else CATALOG_TYPE_BOBTAIL_CURTAIN
        )
    if isinstance(parameters, BiquadParameters):
        return (
            CATALOG_TYPE_BIQUAD
            if parameters.kind is BiquadKind.SINGLE
            else CATALOG_TYPE_DOUBLE_BIQUAD
        )
    if isinstance(parameters, TransmissionLineDoubletParameters):
        return (
            CATALOG_TYPE_G5RV
            if parameters.preset.value == CATALOG_TYPE_G5RV
            else CATALOG_TYPE_ZS6BKW
        )
    if isinstance(parameters, ZeppParameters):
        return CATALOG_TYPE_ZEPP
    if isinstance(parameters, CustomAntennaParameters):
        generator_id = parameters.generator_id
        if generator_id in _KNOWN_CUSTOM_GENERATORS:
            return generator_id
    return CATALOG_TYPE_CUSTOM


def label_key_for(parameters: AntennaDesignParameters) -> str:
    """Return the short translated label for the current template."""

    key = catalog_key_for(parameters)
    return _LABEL_KEYS.get(key, f"catalog.{key}")
