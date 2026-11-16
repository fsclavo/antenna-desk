# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Log-periodic domain geometry and reference checks."""

from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    with_primary_dimension,
)
from antennadesk.domain.antennas.family import antenna_family, antenna_template_id
from antennadesk.domain.antennas.log_periodic import (
    ANTENNA_TYPE_LOG_PERIODIC,
    LogPeriodicParameters,
    cebik_10m_log_periodic_parameters,
    log_periodic_parameters,
)
from antennadesk.domain.antennas.materials import ALUMINUM
from antennadesk.domain.environment.ground import GroundKind, GroundModel
from antennadesk.domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_wire_centers,
)

INCH_M = 0.0254


def test_cebik_reference_reproduces_the_published_geometry() -> None:
    parameters = cebik_10m_log_periodic_parameters()

    lengths_in = tuple(length / INCH_M for length in parameters.element_lengths_m)
    positions_in = tuple(position / INCH_M for position in parameters.element_positions_m)

    assert lengths_in == pytest.approx((215.074, 192.584, 172.445, 154.412), abs=1e-3)
    assert positions_in == pytest.approx((0.0, 35.592, 67.462, 96.000), abs=1e-3)
    assert parameters.boom_length_m == pytest.approx(96.0 * INCH_M, abs=1e-4)
    assert parameters.frequency_low_hz == pytest.approx(28_000_000.0)
    assert parameters.frequency_high_hz == pytest.approx(30_000_000.0)
    assert parameters.phase_line_impedance_ohm == pytest.approx(75.0)
    assert parameters.wire_radius_m == pytest.approx(0.5 * INCH_M)
    assert parameters.material == ALUMINUM


def test_ratios_and_spacings_follow_tau_and_sigma() -> None:
    parameters = cebik_10m_log_periodic_parameters()
    lengths = parameters.element_lengths_m
    spacings = parameters.element_spacings_m

    for index in range(1, len(lengths)):
        assert lengths[index] / lengths[index - 1] == pytest.approx(parameters.tau)
    for index in range(1, len(spacings)):
        assert spacings[index] / spacings[index - 1] == pytest.approx(parameters.tau)
    assert spacings[0] == pytest.approx(2.0 * parameters.sigma * lengths[0])


def test_to_antenna_builds_straight_elements_and_transposed_lines() -> None:
    parameters = cebik_10m_log_periodic_parameters()
    model = parameters.to_antenna()

    assert len(model.wires) == 4
    assert len(model.transmission_lines) == 3
    assert model.feed.wire_id == "log-periodic-element-4"
    assert model.feed.offset_m == pytest.approx(parameters.shortest_element_length_m / 2.0)
    assert all(line.phase_reversal for line in model.transmission_lines)
    assert all(
        line.characteristic_impedance_ohm == pytest.approx(75.0)
        for line in model.transmission_lines
    )
    assert [line.length_m for line in model.transmission_lines] == pytest.approx(
        list(parameters.element_spacings_m)
    )
    for index, wire in enumerate(model.wires, start=1):
        assert wire.id == f"log-periodic-element-{index}"
        assert wire.start.z_m == pytest.approx(0.0)
        assert wire.end.z_m == pytest.approx(0.0)
        assert wire.length_m == pytest.approx(parameters.element_length_m(index))


def test_each_generated_line_connects_adjacent_element_centers() -> None:
    parameters = cebik_10m_log_periodic_parameters()
    model = parameters.to_antenna()

    for index, line in enumerate(model.transmission_lines, start=1):
        start_wire = model.wire_by_id(line.start_wire_id)
        end_wire = model.wire_by_id(line.end_wire_id)
        assert line.start_offset_m == pytest.approx(start_wire.length_m / 2.0)
        assert line.end_offset_m == pytest.approx(end_wire.length_m / 2.0)
        assert line.length_m == pytest.approx(
            abs(parameters.element_positions_m[index] - parameters.element_positions_m[index - 1])
        )


def test_azimuth_rotation_keeps_the_boom_and_elements_perpendicular() -> None:
    parameters = log_periodic_parameters(frequency_hz=28_000_000.0, azimuth_deg=90.0)
    model = parameters.to_antenna()
    rear = model.wire_by_id("log-periodic-element-1")
    front = model.wire_by_id("log-periodic-element-4")

    # A 90-degree rotation puts the boom on the y axis and the elements on
    # the x axis.
    assert rear.start.y_m == pytest.approx(rear.end.y_m, abs=1e-12)
    assert front.start.y_m == pytest.approx(front.end.y_m, abs=1e-12)
    assert rear.end.x_m < 0.0 < rear.start.x_m
    rear_center_y = (rear.start.y_m + rear.end.y_m) / 2.0
    front_center_y = (front.start.y_m + front.end.y_m) / 2.0
    assert front_center_y > rear_center_y


def test_scaled_factory_preserves_the_reference_electrical_design() -> None:
    reference = log_periodic_parameters(frequency_hz=28_000_000.0)
    scaled = log_periodic_parameters(frequency_hz=14_000_000.0)

    assert scaled.frequency_low_hz == pytest.approx(14_000_000.0)
    assert scaled.frequency_high_hz == pytest.approx(15_000_000.0)
    assert scaled.longest_element_length_m == pytest.approx(
        reference.longest_element_length_m * 2.0
    )
    assert scaled.tau == pytest.approx(reference.tau)
    assert scaled.sigma == pytest.approx(reference.sigma)


def test_with_frequency_low_scales_the_array_and_band() -> None:
    parameters = cebik_10m_log_periodic_parameters()
    scaled = parameters.with_frequency_low(14_000_000.0)

    assert scaled.frequency_high_hz == pytest.approx(15_000_000.0)
    assert scaled.longest_element_length_m == pytest.approx(
        parameters.longest_element_length_m * 2.0
    )
    assert scaled.tau == pytest.approx(parameters.tau)
    assert scaled.sigma == pytest.approx(parameters.sigma)


def test_family_and_template_identity() -> None:
    parameters = cebik_10m_log_periodic_parameters()

    assert antenna_type_for(parameters) == ANTENNA_TYPE_LOG_PERIODIC
    assert antenna_template_id(parameters) == "log_periodic"
    assert antenna_family(parameters).value == "log_periodic"


def test_ground_and_height_are_preserved() -> None:
    parameters = log_periodic_parameters(
        frequency_hz=28_000_000.0,
        height_m=12.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    model = parameters.to_antenna()

    assert model.environment.ground.kind is GroundKind.FINITE
    assert all(wire.start.z_m == pytest.approx(12.0) for wire in model.wires)


def test_aligned_policy_for_wire_centers_uses_odd_counts() -> None:
    model = cebik_10m_log_periodic_parameters().to_antenna()
    policy = aligned_policy_for_wire_centers(
        model,
        30_000_000.0,
        SegmentationPolicy(min_segments_per_wire=3),
    )

    assert policy.segments_per_wire is None
    for wire in model.wires:
        count = policy.segments_for(wire, 30_000_000.0)
        assert count % 2 == 1
        assert count >= 3


@pytest.mark.parametrize(
    "kwargs",
    [
        {"frequency_high_hz": 27_000_000.0},
        {"tau": 0.2},
        {"sigma": 0.001},
        {"element_count": 2},
        {"wire_radius_m": 3.0},
        {"phase_line_impedance_ohm": 0.0},
        {"phase_line_velocity_factor": 1.1},
        {"feed_transformer_ratio": 0.0},
        {"height_m": -1.0},
    ],
)
def test_invalid_parameters_are_rejected(kwargs: dict[str, float | int]) -> None:
    base = {
        "frequency_low_hz": 28_000_000.0,
        "frequency_high_hz": 30_000_000.0,
        "longest_element_length_m": 5.4628796,
        "tau": 0.8954,
        "sigma": 0.0827,
        "element_count": 4,
        "wire_radius_m": 0.0127,
        "phase_line_impedance_ohm": 75.0,
    }
    base.update(kwargs)
    with pytest.raises(ValueError):
        LogPeriodicParameters(**base)  # type: ignore[arg-type]


def test_frequency_hz_is_the_geometric_center() -> None:
    parameters = cebik_10m_log_periodic_parameters()

    assert parameters.frequency_hz == pytest.approx(math.sqrt(28.0 * 30.0) * 1_000_000.0)


def test_primary_dimension_scales_only_the_longest_element() -> None:
    parameters = cebik_10m_log_periodic_parameters()

    assert primary_dimension_m(parameters) == pytest.approx(parameters.longest_element_length_m)
    edited = with_primary_dimension(parameters, 6.0)
    assert isinstance(edited, LogPeriodicParameters)
    assert edited.longest_element_length_m == pytest.approx(6.0)
    assert edited.frequency_low_hz == pytest.approx(parameters.frequency_low_hz)
    assert edited.frequency_high_hz == pytest.approx(parameters.frequency_high_hz)
    assert edited.tau == pytest.approx(parameters.tau)
    assert edited.sigma == pytest.approx(parameters.sigma)
