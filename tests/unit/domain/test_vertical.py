# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.family import AntennaFamily, antenna_family
from antennadesk.domain.antennas.vertical import VerticalParameters


def test_vertical_with_radials_generates_connected_wires() -> None:
    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.1,
        radial_count=16,
        radial_length_m=5.0,
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 17
    assert custom.feed.wire_id == "radiator"
    assert custom.feed.offset_m == 0.0
    assert custom.wires[0].start.z_m == pytest.approx(0.1)
    assert custom.wires[0].end.z_m == pytest.approx(10.1)
    assert all(wire.start.z_m == pytest.approx(0.1) for wire in custom.wires[1:])
    assert all(wire.end.z_m == pytest.approx(0.1) for wire in custom.wires[1:])
    assert all(
        math.hypot(wire.end.x_m, wire.end.y_m) == pytest.approx(5.0) for wire in custom.wires[1:]
    )
    assert custom.generator_id == "vertical"
    assert antenna_family(custom) is AntennaFamily.VERTICAL


def test_vertical_without_radials_is_a_single_wire() -> None:
    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 1
    assert parameters.top_height_m == pytest.approx(10.0)


def test_vertical_rejects_invalid_radials() -> None:
    with pytest.raises(ValueError, match="radial_length"):
        VerticalParameters(
            frequency_hz=7_100_000.0,
            height_m=10.0,
            radial_count=4,
        )
    with pytest.raises(ValueError, match="radial_count"):
        VerticalParameters(
            frequency_hz=7_100_000.0,
            height_m=10.0,
            radial_count=129,
        )
