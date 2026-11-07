# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.design import antenna_type_for
from antennadesk.domain.antennas.family import AntennaFamily, antenna_family
from antennadesk.domain.antennas.load import SeriesLoad
from antennadesk.domain.antennas.magnetic_loop import (
    ANTENNA_TYPE_MAGNETIC_LOOP,
    CAPACITOR_LOAD_ID,
    CAPACITOR_WIRE_ID,
    MagneticLoopParameters,
)
from antennadesk.domain.design.estimators import supports_estimation


def _parameters(**overrides: object) -> MagneticLoopParameters:
    values: dict[str, object] = {
        "frequency_hz": 7_100_000.0,
        "diameter_m": 1.0,
        "tuning_capacitance_f": 200e-12,
        "height_m": 1.0,
        "sides": 36,
        "gap_length_m": 0.05,
        "capacitor_esr_ohm": 0.2,
        "azimuth_deg": 0.0,
        "wire_radius_m": 0.005,
    }
    values.update(overrides)
    return MagneticLoopParameters(**values)  # type: ignore[arg-type]


def test_magnetic_loop_generates_a_split_loop_and_capacitor() -> None:
    parameters = _parameters()
    antenna = parameters.to_antenna()

    assert len(antenna.wires) == parameters.sides + 2
    capacitor_wire = next(wire for wire in antenna.wires if wire.id == CAPACITOR_WIRE_ID)
    assert capacitor_wire.length_m == pytest.approx(parameters.gap_length_m)
    assert antenna.feed.wire_id == "loop-26"
    assert antenna.feed.offset_m == pytest.approx(parameters.side_length_m / 2.0)
    load = next(load for load in antenna.loads if isinstance(load, SeriesLoad))
    assert load.id == CAPACITOR_LOAD_ID
    assert load.wire_id == CAPACITOR_WIRE_ID
    assert load.capacitance_f == pytest.approx(parameters.tuning_capacitance_f)
    assert load.resistance_ohm == pytest.approx(0.2)


def test_magnetic_loop_vertices_are_connected_and_centred() -> None:
    parameters = _parameters()
    antenna = parameters.to_antenna()
    loop_wires = tuple(wire for wire in antenna.wires if wire.id != CAPACITOR_WIRE_ID)

    for wire in loop_wires:
        assert wire.start.z_m >= parameters.height_m - 1e-9
        assert math.hypot(wire.start.x_m, wire.start.y_m) <= parameters.radius_m + 1e-9
    assert min(point.z_m for wire in loop_wires for point in (wire.start, wire.end)) == (
        pytest.approx(parameters.height_m)
    )
    assert max(
        point.z_m for wire in loop_wires for point in (wire.start, wire.end)
    ) == pytest.approx(parameters.top_height_m)


def test_magnetic_loop_gap_is_centred_on_the_top_side() -> None:
    parameters = _parameters()
    antenna = parameters.to_antenna()
    capacitor = next(wire for wire in antenna.wires if wire.id == CAPACITOR_WIRE_ID)

    x_values = sorted((capacitor.start.x_m, capacitor.end.x_m))
    assert x_values[0] == pytest.approx(-parameters.gap_length_m / 2.0)
    assert x_values[1] == pytest.approx(parameters.gap_length_m / 2.0)
    assert capacitor.start.z_m == pytest.approx(parameters.top_height_m)
    assert capacitor.end.z_m == pytest.approx(parameters.top_height_m)


def test_magnetic_loop_azimuth_rotates_the_loop_plane() -> None:
    parameters = _parameters(azimuth_deg=90.0)
    first = parameters.to_antenna().wires[0]

    assert first.start.x_m == pytest.approx(0.0, abs=1e-12)
    assert first.start.y_m == pytest.approx(
        parameters.radius_m * math.cos(parameters.step_rad / 2.0),
        abs=1e-3,
    )


def test_magnetic_loop_properties() -> None:
    parameters = _parameters()

    assert parameters.circumference_m == pytest.approx(parameters.sides * parameters.side_length_m)
    assert parameters.loop_conductor_length_m == pytest.approx(
        parameters.circumference_m - parameters.gap_length_m
    )
    assert parameters.capacitor_reactance_ohm == pytest.approx(
        1.0 / (2.0 * math.pi * parameters.frequency_hz * parameters.tuning_capacitance_f)
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("frequency_hz", 0.0),
        ("diameter_m", 0.0),
        ("tuning_capacitance_f", 0.0),
        ("height_m", -1.0),
        ("sides", 7),
        ("sides", 9),
        ("sides", 129),
        ("gap_length_m", 0.0),
        ("gap_length_m", 10.0),
        ("capacitor_esr_ohm", -1.0),
        ("wire_radius_m", 0.0),
    ],
)
def test_magnetic_loop_rejects_invalid_parameters(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        _parameters(**{field: value})


def test_magnetic_loop_round_trips_through_custom_parameters() -> None:
    parameters = _parameters(azimuth_deg=35.0)
    custom = parameters.to_custom_parameters()

    restored = MagneticLoopParameters.from_custom_parameters(custom)

    assert restored.diameter_m == pytest.approx(parameters.diameter_m)
    assert restored.height_m == pytest.approx(parameters.height_m)
    assert restored.sides == parameters.sides
    assert restored.gap_length_m == pytest.approx(parameters.gap_length_m)
    assert restored.tuning_capacitance_f == pytest.approx(parameters.tuning_capacitance_f)
    assert restored.capacitor_esr_ohm == pytest.approx(parameters.capacitor_esr_ohm)
    assert restored.azimuth_deg == pytest.approx(parameters.azimuth_deg)
    assert restored.wire_radius_m == pytest.approx(parameters.wire_radius_m)


def test_magnetic_loop_identity_and_family() -> None:
    parameters = _parameters()

    assert antenna_type_for(parameters) == ANTENNA_TYPE_MAGNETIC_LOOP
    assert antenna_family(parameters) is AntennaFamily.LOOP
    assert supports_estimation(parameters) is False
