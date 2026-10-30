# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.environment.ground import GroundModel


def test_inverted_v_geometry_and_feed() -> None:
    parameters = InvertedVParameters(
        frequency_hz=7_100_000.0,
        leg_length_m=10.6,
        apex_height_m=12.0,
        included_angle_deg=120.0,
        ground=GroundModel.free_space(),
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 2
    assert custom.feed.wire_id == "leg-1"
    assert custom.feed.offset_m == 0.0
    assert parameters.vertical_drop_m == pytest.approx(10.6 * math.cos(math.radians(60.0)))
    assert parameters.horizontal_span_m == pytest.approx(10.6 * math.sin(math.radians(60.0)))
    assert parameters.end_height_m == pytest.approx(12.0 - parameters.vertical_drop_m)
    assert custom.wires[0].start.z_m == pytest.approx(12.0)
    assert custom.wires[0].end.z_m == pytest.approx(parameters.end_height_m)


def test_inverted_v_azimuth_rotates_the_plane() -> None:
    parameters = InvertedVParameters(
        frequency_hz=7_100_000.0,
        leg_length_m=10.0,
        apex_height_m=12.0,
        included_angle_deg=90.0,
        azimuth_deg=90.0,
    )
    custom = parameters.to_custom_parameters()
    first = custom.wires[0]

    assert first.start.x_m == pytest.approx(first.end.x_m)
    assert first.start.y_m == pytest.approx(0.0)
    assert first.end.y_m < 0.0


def test_inverted_v_rejects_ends_below_ground() -> None:
    with pytest.raises(ValueError, match="below ground"):
        InvertedVParameters(
            frequency_hz=7_100_000.0,
            leg_length_m=20.0,
            apex_height_m=5.0,
            included_angle_deg=30.0,
        )


def test_inverted_v_rejects_invalid_angle() -> None:
    with pytest.raises(ValueError, match="included_angle"):
        InvertedVParameters(
            frequency_hz=7_100_000.0,
            leg_length_m=10.0,
            apex_height_m=12.0,
            included_angle_deg=180.0,
        )
