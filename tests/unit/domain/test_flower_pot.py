# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Domain contract for the half-wave Flower Pot family."""

from __future__ import annotations

import pytest

from antennadesk.domain.antennas.flower_pot import (
    BOTTOM_RADIATOR_ID,
    TOP_RADIATOR_ID,
    FlowerPotParameters,
    flower_pot_2m,
    flower_pot_6m,
)


def test_2m_published_row_keeps_physical_and_electrical_lengths_separate() -> None:
    parameters = flower_pot_2m()

    assert parameters.physical_total_length_m == pytest.approx(0.904)
    assert parameters.electrical_top_length_m == pytest.approx(0.457 * 1.087)
    assert parameters.electrical_bottom_length_m == pytest.approx(0.447 * 1.087)
    assert parameters.electrical_total_length_m == pytest.approx(0.904 * 1.087)
    assert parameters.physical_feed_height_m == pytest.approx(1.0 + 0.447)
    assert parameters.electrical_feed_height_m == pytest.approx(parameters.physical_feed_height_m)
    assert parameters.lower_tip_extension_m == pytest.approx(0.447 * 0.087)
    assert parameters.top_extension_m == pytest.approx(0.457 * 0.087)


def test_6m_published_row_keeps_physical_and_electrical_lengths_separate() -> None:
    parameters = flower_pot_6m()

    assert parameters.physical_total_length_m == pytest.approx(2.518)
    assert parameters.electrical_total_length_m == pytest.approx(2.518 * 1.087)
    assert parameters.lower_tip_extension_m == pytest.approx(1.245 * 0.087)
    assert parameters.top_extension_m == pytest.approx(1.273 * 0.087)


def test_to_antenna_uses_two_collinear_wires_and_the_scaled_feed_height() -> None:
    parameters = flower_pot_2m()
    model = parameters.to_antenna()

    assert len(model.wires) == 2
    top = model.wires[0]
    bottom = model.wires[1]
    assert top.id == TOP_RADIATOR_ID
    assert bottom.id == BOTTOM_RADIATOR_ID
    assert top.start.z_m == pytest.approx(parameters.electrical_feed_height_m)
    assert top.end.z_m == pytest.approx(
        parameters.electrical_feed_height_m + parameters.electrical_top_length_m
    )
    assert bottom.start.z_m == pytest.approx(parameters.electrical_lower_tip_m)
    assert bottom.end.z_m == pytest.approx(parameters.electrical_feed_height_m)
    assert model.feed.wire_id == TOP_RADIATOR_ID
    assert model.feed.offset_m == pytest.approx(0.0)
    assert model.design_frequency_hz == pytest.approx(146_000_000.0)


def test_parameters_reject_a_base_height_that_puts_the_scaled_tip_below_ground() -> None:
    with pytest.raises(ValueError, match="scaled electrical lower tip"):
        FlowerPotParameters(
            frequency_hz=146_000_000.0,
            top_length_m=0.457,
            bottom_length_m=0.447,
            base_height_m=0.01,
        )


@pytest.mark.parametrize(
    "field",
    [
        "frequency_hz",
        "top_length_m",
        "bottom_length_m",
        "top_radius_m",
        "bottom_radius_m",
        "base_height_m",
    ],
)
def test_parameters_reject_non_positive_dimensions(field: str) -> None:
    values = {
        "frequency_hz": 146_000_000.0,
        "top_length_m": 0.457,
        "bottom_length_m": 0.447,
        "top_radius_m": 0.0005,
        "bottom_radius_m": 0.0015,
        "base_height_m": 1.0,
    }
    values[field] = 0.0

    with pytest.raises(ValueError):
        FlowerPotParameters(**values)


def test_parameters_reject_out_of_range_factors() -> None:
    with pytest.raises(ValueError, match="construction_shortening_factor"):
        FlowerPotParameters(
            frequency_hz=146_000_000.0,
            top_length_m=0.457,
            bottom_length_m=0.447,
            construction_shortening_factor=0.4,
        )
    with pytest.raises(ValueError, match="electrical_length_scale"):
        FlowerPotParameters(
            frequency_hz=146_000_000.0,
            top_length_m=0.457,
            bottom_length_m=0.447,
            electrical_length_scale=1.6,
        )
