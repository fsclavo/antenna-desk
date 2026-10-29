# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.loop import LoopParameters


def _parameters(**overrides: object) -> LoopParameters:
    values: dict[str, object] = {
        "frequency_hz": 7_100_000.0,
        "circumference_m": 40.0,
        "height_m": 8.0,
        "sides": 4,
        "azimuth_deg": 0.0,
        "wire_radius_m": 0.001,
    }
    values.update(overrides)
    return LoopParameters(**values)  # type: ignore[arg-type]


def test_loop_generates_a_closed_regular_polygon() -> None:
    antenna = _parameters().to_antenna()

    assert len(antenna.wires) == 4
    assert [wire.id for wire in antenna.wires] == [
        "loop-0",
        "loop-1",
        "loop-2",
        "loop-3",
    ]
    assert antenna.feed.wire_id == "loop-0"
    assert antenna.feed.offset_m == pytest.approx(5.0)
    for wire in antenna.wires:
        assert wire.length_m == pytest.approx(10.0)
    assert min(antenna_wire.start.z_m for antenna_wire in antenna.wires) == pytest.approx(8.0)
    assert max(antenna_wire.end.z_m for antenna_wire in antenna.wires) == pytest.approx(
        8.0 + _parameters().diameter_m
    )
    assert all(antenna_wire.start.y_m == pytest.approx(0.0) for antenna_wire in antenna.wires)


def test_loop_vertices_are_connected_end_to_start() -> None:
    wires = _parameters().to_antenna().wires

    for index, wire in enumerate(wires):
        following = wires[(index + 1) % len(wires)]
        assert wire.end.x_m == pytest.approx(following.start.x_m)
        assert wire.end.y_m == pytest.approx(following.start.y_m)
        assert wire.end.z_m == pytest.approx(following.start.z_m)


def test_loop_side_and_diameter() -> None:
    parameters = _parameters()

    assert parameters.side_length_m == pytest.approx(10.0)
    assert parameters.diameter_m == pytest.approx(10.0 / math.sin(math.pi / 4.0))
    assert parameters.top_height_m == pytest.approx(8.0 + parameters.diameter_m)


def test_loop_azimuth_rotates_the_first_vertex() -> None:
    parameters = _parameters(azimuth_deg=90.0)
    wire = parameters.to_antenna().wires[0]

    assert wire.start.x_m == pytest.approx(0.0, abs=1e-12)
    assert wire.start.y_m == pytest.approx(parameters.diameter_m / 2.0)
    assert wire.start.z_m == pytest.approx(parameters.height_m + parameters.diameter_m / 2.0)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("frequency_hz", 0.0),
        ("circumference_m", 0.0),
        ("height_m", -1.0),
        ("sides", 2),
        ("sides", 129),
        ("wire_radius_m", 0.0),
    ],
)
def test_loop_rejects_invalid_parameters(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        _parameters(**{field: value})
