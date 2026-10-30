# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.family import AntennaFamily, antenna_family
from antennadesk.domain.antennas.ringo import RingoParameters


def test_ringo_generates_radiator_connector_and_ring() -> None:
    parameters = RingoParameters(
        frequency_hz=50_100_000.0,
        radiator_height_m=3.0,
        ring_diameter_m=0.33,
        ring_height_m=0.1,
        ring_sides=8,
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 10
    assert custom.feed.wire_id == "radiator"
    assert custom.generator_name == "Ringo"
    assert antenna_family(custom) is AntennaFamily.VERTICAL


def test_ringo_rejects_invalid_ring_sides() -> None:
    with pytest.raises(ValueError, match="ring_sides"):
        RingoParameters(
            frequency_hz=50_100_000.0,
            radiator_height_m=3.0,
            ring_diameter_m=0.33,
            ring_sides=2,
        )
