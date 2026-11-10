# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Defensive schema guards for declared antenna types and payload shapes."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from antennadesk.domain.antennas.beverage import ANTENNA_TYPE_BEVERAGE
from antennadesk.domain.antennas.biquad import (
    ANTENNA_TYPE_BIQUAD,
    ANTENNA_TYPE_DOUBLE_BIQUAD,
    BiquadKind,
)
from antennadesk.domain.antennas.custom import ANTENNA_TYPE_CUSTOM
from antennadesk.domain.antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE
from antennadesk.domain.antennas.discone import ANTENNA_TYPE_DISCONE
from antennadesk.domain.antennas.endfed import ANTENNA_TYPE_ENDFED
from antennadesk.domain.antennas.fan_dipole import ANTENNA_TYPE_FAN_DIPOLE
from antennadesk.domain.antennas.folded_dipole import ANTENNA_TYPE_FOLDED_DIPOLE
from antennadesk.domain.antennas.hexbeam import ANTENNA_TYPE_HEXBEAM
from antennadesk.domain.antennas.inverted_l import ANTENNA_TYPE_INVERTED_L
from antennadesk.domain.antennas.inverted_v import ANTENNA_TYPE_INVERTED_V
from antennadesk.domain.antennas.j_pole import ANTENNA_TYPE_J_POLE
from antennadesk.domain.antennas.loaded_dipole import ANTENNA_TYPE_LOADED_DIPOLE
from antennadesk.domain.antennas.loop import ANTENNA_TYPE_LOOP
from antennadesk.domain.antennas.magnetic_loop import ANTENNA_TYPE_MAGNETIC_LOOP
from antennadesk.domain.antennas.moxon import ANTENNA_TYPE_MOXON
from antennadesk.domain.antennas.ocfd import ANTENNA_TYPE_OCFD
from antennadesk.domain.antennas.phased_vertical import ANTENNA_TYPE_PHASED_VERTICAL
from antennadesk.domain.antennas.quad_beam import ANTENNA_TYPE_QUAD_BEAM
from antennadesk.domain.antennas.ringo import ANTENNA_TYPE_RINGO
from antennadesk.domain.antennas.scv import (
    ANTENNA_TYPE_BOBTAIL_CURTAIN,
    ANTENNA_TYPE_HALF_SQUARE,
    ScvKind,
)
from antennadesk.domain.antennas.t2fd import ANTENNA_TYPE_T2FD
from antennadesk.domain.antennas.transmission_line_doublet import (
    ANTENNA_TYPE_G5RV,
    ANTENNA_TYPE_ZS6BKW,
    DoubletPreset,
)
from antennadesk.domain.antennas.trap_dipole import ANTENNA_TYPE_TRAP_DIPOLE
from antennadesk.domain.antennas.trap_yagi import ANTENNA_TYPE_TRAP_YAGI
from antennadesk.domain.antennas.vertical import ANTENNA_TYPE_VERTICAL
from antennadesk.domain.antennas.yagi import ANTENNA_TYPE_YAGI
from antennadesk.domain.antennas.zepp import ANTENNA_TYPE_ZEPP
from antennadesk.persistence import schema

DECLARED_TYPES = (
    ANTENNA_TYPE_WIRE_DIPOLE,
    ANTENNA_TYPE_FOLDED_DIPOLE,
    ANTENNA_TYPE_LOOP,
    ANTENNA_TYPE_MAGNETIC_LOOP,
    ANTENNA_TYPE_OCFD,
    ANTENNA_TYPE_VERTICAL,
    ANTENNA_TYPE_INVERTED_V,
    ANTENNA_TYPE_INVERTED_L,
    ANTENNA_TYPE_YAGI,
    ANTENNA_TYPE_MOXON,
    ANTENNA_TYPE_FAN_DIPOLE,
    ANTENNA_TYPE_ENDFED,
    ANTENNA_TYPE_LOADED_DIPOLE,
    ANTENNA_TYPE_DISCONE,
    ANTENNA_TYPE_HEXBEAM,
    ANTENNA_TYPE_PHASED_VERTICAL,
    ANTENNA_TYPE_QUAD_BEAM,
    ANTENNA_TYPE_J_POLE,
    ANTENNA_TYPE_RINGO,
    ANTENNA_TYPE_HALF_SQUARE,
    ANTENNA_TYPE_BOBTAIL_CURTAIN,
    ANTENNA_TYPE_BIQUAD,
    ANTENNA_TYPE_DOUBLE_BIQUAD,
    ANTENNA_TYPE_BEVERAGE,
    ANTENNA_TYPE_TRAP_DIPOLE,
    ANTENNA_TYPE_TRAP_YAGI,
    ANTENNA_TYPE_T2FD,
    ANTENNA_TYPE_G5RV,
    ANTENNA_TYPE_ZS6BKW,
    ANTENNA_TYPE_ZEPP,
    ANTENNA_TYPE_CUSTOM,
)


@pytest.mark.parametrize("antenna_type", DECLARED_TYPES)
def test_parameters_to_domain_rejects_a_foreign_payload(antenna_type: str) -> None:
    payload = SimpleNamespace(antenna_type=antenna_type, parameters=object())

    with pytest.raises(ValueError, match="wrong shape"):
        schema._parameters_to_domain(payload)  # type: ignore[arg-type]


def test_parameters_to_domain_rejects_an_unsupported_type() -> None:
    payload = SimpleNamespace(antenna_type="unsupported", parameters=object())

    with pytest.raises(ValueError, match="unsupported antenna type"):
        schema._parameters_to_domain(payload)  # type: ignore[arg-type]


def test_scv_payload_must_match_the_declared_array_variant() -> None:
    payload = SimpleNamespace(
        antenna_type=ANTENNA_TYPE_BOBTAIL_CURTAIN,
        parameters=schema.ScvParametersPayload.model_construct(kind=ScvKind.HALF_SQUARE),
    )

    with pytest.raises(ValueError, match="array variant"):
        schema._parameters_to_domain(payload)  # type: ignore[arg-type]


def test_biquad_payload_must_match_the_declared_variant() -> None:
    payload = SimpleNamespace(
        antenna_type=ANTENNA_TYPE_DOUBLE_BIQUAD,
        parameters=schema.BiquadParametersPayload.model_construct(kind=BiquadKind.SINGLE),
    )

    with pytest.raises(ValueError, match="biquad variant"):
        schema._parameters_to_domain(payload)  # type: ignore[arg-type]


def test_doublet_payload_must_match_the_declared_preset() -> None:
    payload = SimpleNamespace(
        antenna_type=ANTENNA_TYPE_ZS6BKW,
        parameters=schema.TransmissionLineDoubletParametersPayload.model_construct(
            preset=DoubletPreset.G5RV
        ),
    )

    with pytest.raises(ValueError, match="doublet preset"):
        schema._parameters_to_domain(payload)  # type: ignore[arg-type]
