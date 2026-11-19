# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Smith-chart projection and reference-plane tests."""

from __future__ import annotations

import math
from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.antennas.matching_network import (
    MatchingNetworkPosition,
    design_l_network,
)
from antennadesk.domain.design.smith_chart import (
    SmithPlane,
    available_smith_planes,
    constant_reactance_arc_points,
    constant_resistance_circle_points,
    smith_locus,
    smith_point,
    smith_points_for_measurement,
    smith_points_for_result,
    transform_with_feed_line,
)
from antennadesk.domain.measurement import Measurement, MeasurementPoint
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.link import link_budget
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
    SourceResult,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


def _result(*, with_source: bool = True) -> SimulationResult:
    source = SourceResult(
        wire_id="wire-1",
        offset_m=0.0,
        tag=1,
        segment=1,
        amplitude=1.0,
        phase_deg=0.0,
        voltage_v=1.0 + 0.0j,
        current_a=0.01 + 0.0j,
        impedance_ohm=complex(100.0, 0.0),
        power_w=0.01,
    )
    frequencies = (
        FrequencyResult(
            frequency_hz=14_000_000.0,
            feed_tag=1,
            feed_segment=1,
            impedance_ohm=complex(50.0, 0.0),
            swr=1.0,
            input_power_w=0.01,
            source_results=(source,) if with_source else (),
        ),
        FrequencyResult(
            frequency_hz=14_100_000.0,
            feed_tag=1,
            feed_segment=1,
            impedance_ohm=complex(75.0, 10.0),
            swr=1.5,
            input_power_w=0.01,
            source_results=(source,) if with_source else (),
        ),
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=SimulationSpec(frequency_plan=FrequencyPlan.sweep(14_000_000.0, 14_100_000.0, 2)),
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=frequencies,
        duration_s=0.1,
        started_at=datetime(2026, 11, 19, tzinfo=UTC),
        finished_at=datetime(2026, 11, 19, tzinfo=UTC),
    )


def test_fifty_ohm_maps_to_the_center_and_open_short_map_to_the_boundary() -> None:
    center = smith_point(14_000_000.0, complex(50.0, 0.0), 50.0)
    open_point = smith_point(14_000_000.0, complex(1.0e12, 0.0), 50.0)
    short_point = smith_point(14_000_000.0, complex(0.0, 0.0), 50.0)

    assert center.gamma == pytest.approx(0.0)
    assert center.swr == pytest.approx(1.0)
    assert open_point.gamma == pytest.approx(1.0)
    assert short_point.gamma == pytest.approx(-1.0)
    assert open_point.gamma_magnitude > 0.999
    assert math.isinf(short_point.swr)


def test_smith_locus_keeps_frequency_order_and_rejects_mismatched_lengths() -> None:
    points = smith_locus(
        [14_000_000.0, 14_100_000.0],
        [complex(50.0, 0.0), complex(75.0, 10.0)],
        50.0,
    )

    assert [point.frequency_hz for point in points] == [14_000_000.0, 14_100_000.0]
    assert points[0].gamma_magnitude == pytest.approx(0.0)
    assert points[1].swr > 1.0

    with pytest.raises(ValueError):
        smith_locus([14_000_000.0], [50.0 + 0.0j, 75.0 + 0.0j], 50.0)


def test_reference_planes_use_raw_and_feed_line_impedances() -> None:
    result = _result()
    simulated = smith_points_for_result(result, SmithPlane.SIMULATED)
    antenna = smith_points_for_result(result, SmithPlane.ANTENNA)

    assert simulated[0].impedance_ohm == pytest.approx(complex(50.0, 0.0))
    assert antenna[0].impedance_ohm == pytest.approx(complex(100.0, 0.0))
    assert SmithPlane.ANTENNA in available_smith_planes(result)
    assert SmithPlane.FEED_LINE not in available_smith_planes(result)

    with_line = _result()
    line = FeedLine(characteristic_impedance_ohm=50.0, length_m=10.0, velocity_factor=0.66)
    with_line = SimulationResult(
        status=with_line.status,
        spec=SimulationSpec(
            frequency_plan=with_line.spec.frequency_plan,
            feed_line=line,
        ),
        model_fingerprint=with_line.model_fingerprint,
        solver=with_line.solver,
        frequencies=with_line.frequencies,
        duration_s=with_line.duration_s,
        started_at=with_line.started_at,
        finished_at=with_line.finished_at,
    )
    feed_line = smith_points_for_result(with_line, SmithPlane.FEED_LINE)

    assert SmithPlane.FEED_LINE in available_smith_planes(with_line)
    assert feed_line[0].impedance_ohm != pytest.approx(complex(100.0, 0.0))


def test_a_known_l_network_moves_the_simulated_locus_to_the_target() -> None:
    base = _result()
    load = complex(100.0, 0.0)
    network = design_l_network(load, 14_000_000.0, source_impedance_ohm=50.0)
    assert network is not None
    spec = replace(
        base.spec,
        matching_network=network,
        matching_network_position=MatchingNetworkPosition.FEEDPOINT,
    )
    link = link_budget(
        antenna_impedance_ohm=load,
        frequency_hz=14_000_000.0,
        spec=spec,
    )
    frequency = replace(
        base.frequencies[0],
        impedance_ohm=link.input_impedance_ohm,
        swr=1.0,
    )
    result = replace(base, spec=spec, frequencies=(frequency,))

    simulated = smith_points_for_result(result, SmithPlane.SIMULATED)
    antenna = smith_points_for_result(result, SmithPlane.ANTENNA)

    assert simulated[0].impedance_ohm.real == pytest.approx(50.0, abs=0.1)
    assert simulated[0].impedance_ohm.imag == pytest.approx(0.0, abs=0.1)
    assert antenna[0].impedance_ohm == pytest.approx(load)


def test_transform_with_feed_line_preserves_frequency_and_reference() -> None:
    points = smith_locus([14_000_000.0], [complex(100.0, 0.0)], 50.0)
    line = FeedLine(characteristic_impedance_ohm=50.0, length_m=10.0, velocity_factor=0.66)

    transformed = transform_with_feed_line(points, line)

    assert len(transformed) == 1
    assert transformed[0].frequency_hz == points[0].frequency_hz
    assert transformed[0].reference_impedance_ohm == points[0].reference_impedance_ohm
    assert transformed[0].impedance_ohm != points[0].impedance_ohm


def test_measured_points_use_the_display_reference_impedance() -> None:
    measurement = Measurement(
        id=uuid4(),
        name="measurement",
        created_at=datetime(2026, 11, 19, tzinfo=UTC),
        reference_impedance_ohm=75.0,
        points=(MeasurementPoint(14_000_000.0, complex(75.0, 0.0)),),
    )

    points = smith_points_for_measurement(measurement, 50.0)

    assert points[0].reference_impedance_ohm == 50.0
    assert points[0].gamma.real == pytest.approx(0.2)


def test_constant_resistance_circles_and_reactance_arcs_stay_in_the_gamma_plane() -> None:
    unit_circle = constant_resistance_circle_points(0.0, count=9)
    matched_circle = constant_resistance_circle_points(1.0, count=9)
    inductive_arc = constant_reactance_arc_points(1.0, count=9)
    capacitive_arc = constant_reactance_arc_points(-1.0, count=9)
    real_axis = constant_reactance_arc_points(0.0, count=5)

    assert all(abs(point) == pytest.approx(1.0) for point in unit_circle)
    assert all(point.real >= 0.0 for point in matched_circle)
    assert all(abs(point) <= 1.0 + 1e-9 for point in inductive_arc)
    assert all(abs(point) <= 1.0 + 1e-9 for point in capacitive_arc)
    assert real_axis[0] == pytest.approx(-1.0)
    assert real_axis[-1] == pytest.approx(1.0)
    assert inductive_arc[0].imag > 0.0
    assert capacitive_arc[0].imag < 0.0

    with pytest.raises(ValueError):
        constant_resistance_circle_points(-0.1)
    with pytest.raises(ValueError):
        constant_reactance_arc_points(math.inf)
