# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    with_primary_dimension,
)
from antennadesk.domain.antennas.family import AntennaFamily, antenna_family, antenna_template_id
from antennadesk.domain.antennas.scv import (
    BOBTAIL_REFERENCE_HORIZONTAL_LENGTH_M,
    BOBTAIL_REFERENCE_VERTICAL_HEIGHT_M,
    CENTER_VERTICAL_ID,
    HALF_SQUARE_REFERENCE_HORIZONTAL_LENGTH_M,
    HALF_SQUARE_REFERENCE_VERTICAL_HEIGHT_M,
    LEFT_VERTICAL_ID,
    SCV_REFERENCE_FREQUENCY_HZ,
    ScvKind,
    ScvParameters,
    scv_parameters,
    scv_starting_dimensions,
)


def test_half_square_generates_two_verticals_and_a_top_wire() -> None:
    parameters = scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0)
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 3
    assert custom.feed.wire_id == LEFT_VERTICAL_ID
    assert custom.feed.offset_m == pytest.approx(0.0)
    assert custom.generator_id == "half_square"
    assert custom.generator_name == "Half square"
    assert antenna_family(custom) is AntennaFamily.VERTICAL
    assert antenna_template_id(custom) == "half_square"
    assert parameters.horizontal_segment_m == pytest.approx(parameters.horizontal_length_m)
    assert parameters.total_conductor_length_m == pytest.approx(
        2.0 * parameters.vertical_height_m + parameters.horizontal_length_m
    )


def test_bobtail_curtain_generates_three_verticals_and_two_top_segments() -> None:
    parameters = scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0)
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 5
    assert custom.feed.wire_id == CENTER_VERTICAL_ID
    assert custom.feed.offset_m == pytest.approx(0.0)
    assert custom.generator_id == "bobtail_curtain"
    assert custom.generator_name == "Bobtail curtain"
    assert parameters.horizontal_segment_m == pytest.approx(parameters.horizontal_length_m / 2.0)
    assert parameters.total_conductor_length_m == pytest.approx(
        3.0 * parameters.vertical_height_m + parameters.horizontal_length_m
    )


def test_scv_design_type_and_primary_dimension_follow_the_variant() -> None:
    half = scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0)
    bobtail = scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0)

    assert antenna_type_for(half) == "half_square"
    assert antenna_type_for(bobtail) == "bobtail_curtain"
    assert primary_dimension_m(half) == pytest.approx(half.horizontal_length_m)
    edited = with_primary_dimension(bobtail, 40.0)
    assert isinstance(edited, ScvParameters)
    assert edited.horizontal_length_m == pytest.approx(40.0)
    assert edited.vertical_height_m == pytest.approx(bobtail.vertical_height_m)


def test_scv_feed_is_at_the_top_junction_and_offset_moves_down() -> None:
    parameters = scv_parameters(
        ScvKind.BOBTAIL_CURTAIN,
        7_150_000.0,
        base_height_m=2.0,
        feed_offset_m=1.5,
    )
    custom = parameters.to_custom_parameters()
    center = next(wire for wire in custom.wires if wire.id == CENTER_VERTICAL_ID)

    assert center.start.z_m == pytest.approx(parameters.top_height_m)
    assert center.end.z_m == pytest.approx(2.0)
    assert parameters.feed_height_m == pytest.approx(parameters.top_height_m - 1.5)
    assert custom.feed.offset_m == pytest.approx(1.5)


def test_published_cebik_reference_dimensions_match_the_scaled_start() -> None:
    half_horizontal, half_vertical = scv_starting_dimensions(
        ScvKind.HALF_SQUARE,
        SCV_REFERENCE_FREQUENCY_HZ,
    )
    bobtail_horizontal, bobtail_vertical = scv_starting_dimensions(
        ScvKind.BOBTAIL_CURTAIN,
        SCV_REFERENCE_FREQUENCY_HZ,
    )

    assert half_horizontal == pytest.approx(HALF_SQUARE_REFERENCE_HORIZONTAL_LENGTH_M)
    assert half_vertical == pytest.approx(HALF_SQUARE_REFERENCE_VERTICAL_HEIGHT_M)
    assert bobtail_horizontal == pytest.approx(BOBTAIL_REFERENCE_HORIZONTAL_LENGTH_M)
    assert bobtail_vertical == pytest.approx(BOBTAIL_REFERENCE_VERTICAL_HEIGHT_M)
    assert pytest.approx(62.4 * 0.3048) == HALF_SQUARE_REFERENCE_HORIZONTAL_LENGTH_M
    assert pytest.approx(39.0 * 0.3048) == HALF_SQUARE_REFERENCE_VERTICAL_HEIGHT_M
    assert pytest.approx(125.0 * 0.3048) == BOBTAIL_REFERENCE_HORIZONTAL_LENGTH_M
    assert pytest.approx(38.0 * 0.3048) == BOBTAIL_REFERENCE_VERTICAL_HEIGHT_M


def test_scv_starting_dimensions_scale_inversely_with_frequency() -> None:
    half_horizontal, half_vertical = scv_starting_dimensions(
        ScvKind.HALF_SQUARE,
        SCV_REFERENCE_FREQUENCY_HZ / 2.0,
    )

    assert half_horizontal == pytest.approx(2.0 * HALF_SQUARE_REFERENCE_HORIZONTAL_LENGTH_M)
    assert half_vertical == pytest.approx(2.0 * HALF_SQUARE_REFERENCE_VERTICAL_HEIGHT_M)


def test_scv_geometry_rotates_the_whole_array_with_azimuth() -> None:
    parameters = scv_parameters(
        ScvKind.HALF_SQUARE,
        7_150_000.0,
        azimuth_deg=90.0,
    )
    custom = parameters.to_custom_parameters()
    right = next(wire for wire in custom.wires if wire.id == "right-vertical")

    assert right.start.x_m == pytest.approx(0.0, abs=1e-9)
    assert right.start.y_m == pytest.approx(parameters.horizontal_length_m)
    assert math.hypot(right.start.x_m, right.start.y_m) == pytest.approx(
        parameters.horizontal_length_m
    )


def test_scv_custom_round_trip_preserves_the_geometry() -> None:
    for kind in ScvKind:
        parameters = scv_parameters(
            kind,
            7_050_000.0,
            base_height_m=1.5,
            feed_offset_m=0.5,
            azimuth_deg=35.0,
        )

        restored = ScvParameters.from_custom_parameters(parameters.to_custom_parameters())

        assert restored.kind is parameters.kind
        assert restored.frequency_hz == pytest.approx(parameters.frequency_hz)
        assert restored.horizontal_length_m == pytest.approx(parameters.horizontal_length_m)
        assert restored.vertical_height_m == pytest.approx(parameters.vertical_height_m)
        assert restored.base_height_m == pytest.approx(parameters.base_height_m)
        assert restored.feed_offset_m == pytest.approx(parameters.feed_offset_m)
        assert restored.azimuth_deg == pytest.approx(parameters.azimuth_deg)
        assert restored.wire_radius_m == pytest.approx(parameters.wire_radius_m)
        assert restored.material == parameters.material
        assert restored.ground == parameters.ground


def test_scv_rejects_invalid_dimensions_and_feed_offset() -> None:
    with pytest.raises(ValueError, match="horizontal_length"):
        ScvParameters(
            frequency_hz=7_100_000.0,
            kind=ScvKind.HALF_SQUARE,
            horizontal_length_m=0.0,
            vertical_height_m=10.0,
        )
    with pytest.raises(ValueError, match="vertical_height"):
        ScvParameters(
            frequency_hz=7_100_000.0,
            kind=ScvKind.HALF_SQUARE,
            horizontal_length_m=20.0,
            vertical_height_m=-1.0,
        )
    with pytest.raises(ValueError, match="feed_offset"):
        ScvParameters(
            frequency_hz=7_100_000.0,
            kind=ScvKind.BOBTAIL_CURTAIN,
            horizontal_length_m=40.0,
            vertical_height_m=10.0,
            feed_offset_m=10.0,
        )


def test_scv_custom_round_trip_rejects_a_foreign_layout() -> None:
    parameters = scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0)
    custom = parameters.to_custom_parameters()
    malformed = custom.__class__(
        frequency_hz=custom.frequency_hz,
        wires=custom.wires[:2],
        feed=custom.feed,
        generator_id=custom.generator_id,
        generator_name=custom.generator_name,
    )

    with pytest.raises(ValueError, match="family wires"):
        ScvParameters.from_custom_parameters(malformed)
