# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from datetime import UTC, datetime

from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.reporting.csv_export import CSV_HEADER, result_to_csv


def make_result() -> SimulationResult:
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_100_000.0, 2),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        far_field=FarFieldRequest(),
    )
    frequencies = (
        FrequencyResult(
            frequency_hz=6_900_000.0,
            feed_tag=1,
            feed_segment=11,
            impedance_ohm=complex(60.0, -10.0),
            swr=2.0,
            input_power_w=0.001,
            far_field=(
                FarFieldPoint(0.0, 0.0, 2.0, None, 2.0, 0.0, 0.0, None, None, None, None, None),
            ),
        ),
        FrequencyResult(
            frequency_hz=7_100_000.0,
            feed_tag=1,
            feed_segment=11,
            impedance_ohm=complex(70.0, 0.0),
            swr=1.4,
            input_power_w=0.002,
            far_field=(
                FarFieldPoint(0.0, 0.0, 2.1, None, 2.1, 0.0, 0.0, None, None, None, None, None),
            ),
        ),
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=frequencies,
        duration_s=0.1,
        started_at=datetime(2026, 10, 29, tzinfo=UTC),
        finished_at=datetime(2026, 10, 29, tzinfo=UTC),
    )


def test_csv_header_and_rows() -> None:
    text = result_to_csv(make_result())
    lines = text.strip().splitlines()

    assert lines[0] == CSV_HEADER
    assert len(lines) == 3
    assert lines[1].startswith("6900000.000000,6.900000000,60.000000,-10.000000")
    assert lines[2].startswith("7100000.000000,7.100000000,70.000000,0.000000")
