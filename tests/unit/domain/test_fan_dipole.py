# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.family import AntennaFamily, antenna_family
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement


def test_fan_dipole_generates_two_wires_per_pair() -> None:
    parameters = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(
            FanElement(length_m=20.0, included_angle_deg=120.0),
            FanElement(length_m=10.0, included_angle_deg=90.0),
        ),
        apex_height_m=12.0,
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 4
    assert custom.feed.wire_id == "fan-1-leg-1"
    assert custom.feed.offset_m == 0.0
    assert custom.generator_name == "Fan dipole"
    assert antenna_family(custom) is AntennaFamily.DIPOLE


def test_fan_dipole_rejects_below_ground_elements() -> None:
    with pytest.raises(ValueError, match="below ground"):
        FanDipoleParameters(
            frequency_hz=7_100_000.0,
            elements=(FanElement(length_m=20.0, included_angle_deg=20.0),),
            apex_height_m=5.0,
        )
