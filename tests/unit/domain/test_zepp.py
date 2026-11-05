# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.antennas.zepp import (
    ZEPP_BASE_ID,
    ZEPP_MATCHING_FEED_ID,
    ZEPP_MATCHING_OPEN_ID,
    ZEPP_RADIATOR_ID,
    parallel_wire_impedance_ohm,
    zepp_choke,
    zepp_parameters,
    zepp_starting_dimensions,
)
from antennadesk.domain.environment.ground import GroundModel


def _wire(parameters: CustomAntennaParameters, wire_id: str) -> Wire:
    return next(wire for wire in parameters.wires if wire.id == wire_id)


def test_zepp_uses_a_half_wave_radiator_and_quarter_wave_stub() -> None:
    parameters = zepp_parameters()
    radiator_m, matching_m = zepp_starting_dimensions(7_100_000.0)

    assert parameters.generator_id == "zepp"
    assert parameters.generator_name == "Zepp"
    assert {wire.id for wire in parameters.wires} == {
        ZEPP_RADIATOR_ID,
        ZEPP_MATCHING_FEED_ID,
        ZEPP_MATCHING_OPEN_ID,
        ZEPP_BASE_ID,
    }
    assert parameters.transmission_lines == ()
    radiator = _wire(parameters, ZEPP_RADIATOR_ID)
    assert radiator.length_m == pytest.approx(radiator_m)
    matching_feed = _wire(parameters, ZEPP_MATCHING_FEED_ID)
    matching_open = _wire(parameters, ZEPP_MATCHING_OPEN_ID)
    assert matching_feed.length_m == pytest.approx(matching_m)
    assert matching_open.length_m == pytest.approx(matching_m)


def test_zepp_feed_is_the_middle_of_the_base_connector() -> None:
    parameters = zepp_parameters(spacing_m=0.08)

    assert parameters.feed.wire_id == ZEPP_BASE_ID
    assert parameters.feed.offset_m == pytest.approx(0.04)
    base = _wire(parameters, ZEPP_BASE_ID)
    assert base.length_m == pytest.approx(0.08)


def test_zepp_has_an_open_second_stub_conductor() -> None:
    parameters = zepp_parameters()
    radiator = _wire(parameters, ZEPP_RADIATOR_ID)
    matching_feed = _wire(parameters, ZEPP_MATCHING_FEED_ID)
    matching_open = _wire(parameters, ZEPP_MATCHING_OPEN_ID)

    assert matching_feed.end == radiator.start
    assert matching_feed.start == Point3D(0.0, 0.0, matching_feed.start.z_m)
    assert matching_open.start.z_m == pytest.approx(matching_feed.start.z_m)
    assert matching_open.end.z_m == pytest.approx(matching_feed.end.z_m)
    assert matching_open.end != radiator.start
    assert matching_open.end != radiator.end
    endpoints_at_open_top = sum(
        1
        for wire in parameters.wires
        for point in (wire.start, wire.end)
        if math.dist(
            (point.x_m, point.y_m, point.z_m),
            (
                matching_open.end.x_m,
                matching_open.end.y_m,
                matching_open.end.z_m,
            ),
        )
        < 1e-9
    )
    assert endpoints_at_open_top == 1


def test_zepp_radiator_is_perpendicular_to_the_stub_pair() -> None:
    parameters = zepp_parameters(
        azimuth_deg=30.0,
        radiator_length_m=20.0,
        matching_section_length_m=10.0,
        spacing_m=0.05,
        base_height_m=2.0,
    )
    radiator = _wire(parameters, ZEPP_RADIATOR_ID)
    matching_feed = _wire(parameters, ZEPP_MATCHING_FEED_ID)
    matching_open = _wire(parameters, ZEPP_MATCHING_OPEN_ID)

    radiator_direction = (
        radiator.end.x_m - radiator.start.x_m,
        radiator.end.y_m - radiator.start.y_m,
    )
    stub_direction = (
        matching_open.start.x_m - matching_feed.start.x_m,
        matching_open.start.y_m - matching_feed.start.y_m,
    )
    dot = radiator_direction[0] * stub_direction[0] + radiator_direction[1] * stub_direction[1]
    assert dot == pytest.approx(0.0, abs=1e-9)
    assert radiator.start.z_m == pytest.approx(12.0)
    assert radiator.end.z_m == pytest.approx(12.0)


def test_zepp_parallel_wire_impedance_matches_the_standard_formula() -> None:
    assert parallel_wire_impedance_ohm(0.05, 0.001) == pytest.approx(468.92, rel=1e-4)
    assert parallel_wire_impedance_ohm(0.10, 0.001) == pytest.approx(552.0, rel=1e-4)


def test_zepp_parallel_wire_impedance_rejects_overlapping_conductors() -> None:
    with pytest.raises(ValueError, match="diameter"):
        parallel_wire_impedance_ohm(0.002, 0.001)


def test_zepp_choke_is_a_required_unmodeled_one_to_one_choke() -> None:
    choke = zepp_choke()

    assert choke.ratio == pytest.approx(1.0)
    assert choke.modeled is False


def test_zepp_accepts_manual_radiator_stub_and_spacing() -> None:
    parameters = zepp_parameters(
        radiator_length_m=10.0,
        matching_section_length_m=2.5,
        spacing_m=0.06,
        base_height_m=3.0,
    )

    radiator = _wire(parameters, ZEPP_RADIATOR_ID)
    matching_feed = _wire(parameters, ZEPP_MATCHING_FEED_ID)
    base = _wire(parameters, ZEPP_BASE_ID)
    assert radiator.length_m == pytest.approx(10.0)
    assert matching_feed.length_m == pytest.approx(2.5)
    assert base.length_m == pytest.approx(0.06)
    assert matching_feed.start.z_m == pytest.approx(3.0)
    assert radiator.start.z_m == pytest.approx(5.5)


def test_zepp_rejects_spacing_that_overlaps_the_conductors() -> None:
    with pytest.raises(ValueError, match="diameter"):
        zepp_parameters(spacing_m=0.0015, wire_radius_m=0.001)


def test_zepp_propagates_the_ground_model() -> None:
    ground = GroundModel.finite(relative_permittivity=13.0, conductivity_s_per_m=0.005)
    parameters = zepp_parameters(ground=ground)

    assert parameters.ground == ground
