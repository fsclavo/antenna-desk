# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.family import AntennaFamily, antenna_family
from antennadesk.domain.antennas.j_pole import JPoleParameters


def test_j_pole_generates_radiator_stub_and_connector() -> None:
    parameters = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 3
    assert custom.feed.wire_id == "stub"
    assert custom.feed.offset_m == pytest.approx(0.1)
    assert custom.generator_name == "J Pole"
    assert antenna_family(custom) is AntennaFamily.VERTICAL


def test_slim_jim_keeps_the_top_gap_open() -> None:
    parameters = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        folded=True,
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 3
    assert custom.generator_name == "Slim Jim"
    assert not any(wire.id == "top-connector" for wire in custom.wires)


def test_j_pole_validates_feed_and_stub() -> None:
    with pytest.raises(ValueError, match="feed_offset"):
        JPoleParameters(
            frequency_hz=145_000_000.0,
            radiator_height_m=1.0,
            stub_length_m=0.5,
            spacing_m=0.05,
            feed_offset_m=0.5,
        )
    with pytest.raises(ValueError, match="radiator_height"):
        JPoleParameters(
            frequency_hz=145_000_000.0,
            radiator_height_m=0.4,
            stub_length_m=0.5,
            spacing_m=0.05,
        )


def test_j_pole_rejects_a_ground_level_base() -> None:
    with pytest.raises(ValueError, match="base_height"):
        JPoleParameters(
            frequency_hz=145_000_000.0,
            radiator_height_m=1.0,
            stub_length_m=0.5,
            spacing_m=0.05,
            base_height_m=0.0,
        )
