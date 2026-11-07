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
from antennadesk.reporting.csv_export import (
    CSV_HEADER,
    PATTERN_HEADER,
    pattern_to_csv,
    result_to_csv,
)


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
            directivity_db=2.2,
            realized_gain_db=1.8,
            mismatch_loss_db=0.2,
            feed_line_loss_db=0.1,
            network_loss_db=0.05,
            balun_loss_db=0.03,
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
    assert lines[1].endswith(",2.0000,2.2000,1.8000,0.200000,0.100000,0.050000,0.030000")
    assert lines[2].startswith("7100000.000000,7.100000000,70.000000,0.000000")


def test_pattern_csv_has_one_row_per_far_field_point() -> None:
    text = pattern_to_csv(make_result())
    lines = text.strip().splitlines()

    assert lines[0] == PATTERN_HEADER
    assert len(lines) == 3
    assert lines[1].startswith("6900000.000000,6.900000000,0.000000,0.000000,2.000000")
    assert lines[2].startswith("7100000.000000,7.100000000,0.000000,0.000000,2.100000")


def test_band_csv_adds_a_band_column() -> None:
    from uuid import uuid4

    from antennadesk.domain.simulation.band_result import BandAnalysisResult, BandResult
    from antennadesk.domain.simulation.bands import amateur_band_by_id
    from antennadesk.reporting.csv_export import (
        band_analysis_pattern_to_csv,
        band_analysis_to_csv,
    )

    band = amateur_band_by_id("40m")
    assert band is not None
    analysis = BandAnalysisResult(
        design_id=uuid4(),
        batch_id=uuid4(),
        created_at=datetime(2026, 11, 3, tzinfo=UTC),
        bands=(BandResult(band=band, result=make_result()),),
    )

    lines = band_analysis_to_csv(analysis).strip().splitlines()
    pattern_lines = band_analysis_pattern_to_csv(analysis).strip().splitlines()

    assert lines[0] == f"band,{CSV_HEADER}"
    assert lines[1].startswith("40m,6900000.000000")
    assert pattern_lines[0] == f"band,{PATTERN_HEADER}"
    assert pattern_lines[1].startswith("40m,6900000.000000")
