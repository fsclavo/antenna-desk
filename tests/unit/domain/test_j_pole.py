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

    assert len(custom.wires) == 5
    assert custom.generator_name == "Slim Jim"
    assert any(wire.id == "top-connector" for wire in custom.wires)
    assert any(wire.id == "right-upper" for wire in custom.wires)
    assert any(wire.id == "right-lower" for wire in custom.wires)


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


def test_slim_jim_requires_a_gap() -> None:
    with pytest.raises(ValueError, match="gap"):
        JPoleParameters(
            frequency_hz=145_000_000.0,
            radiator_height_m=1.0,
            stub_length_m=0.5,
            spacing_m=0.05,
            folded=True,
            gap_m=0.0,
        )


def test_slim_jim_top_connector_is_horizontal() -> None:
    custom = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        folded=True,
    ).to_custom_parameters()
    top = next(wire for wire in custom.wires if wire.id == "top-connector")

    assert top.start.z_m == pytest.approx(top.end.z_m)
    assert top.start.x_m == pytest.approx(0.0)
    assert top.end.x_m == pytest.approx(0.05)
