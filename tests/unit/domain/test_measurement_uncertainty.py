# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Qualitative measurement uncertainty assessment."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from antennadesk.domain.measurement import Measurement, MeasurementPoint, MeasurementSession
from antennadesk.domain.measurement_uncertainty import (
    MeasurementDocumentationStatus,
    MeasurementUncertaintyLevel,
    assess_measurement_uncertainty,
)
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec

_MEASUREMENT_ID = UUID("00000000-0000-0000-0000-000000000061")
_SESSION_ID = UUID("00000000-0000-0000-0000-000000000062")


def _measurement(
    *points: MeasurementPoint,
    calibration: str = "",
    reference_plane: str = "",
    feed_line: str = "",
) -> Measurement:
    return Measurement(
        id=_MEASUREMENT_ID,
        name="Field sweep",
        created_at=datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=points
        or (
            MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
            MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        ),
        calibration=calibration,
        reference_plane=reference_plane,
        feed_line=feed_line,
    )


def _session(*, conditions: str = "Dry ground, 8 m") -> MeasurementSession:
    return MeasurementSession(
        id=_SESSION_ID,
        name="Before tuning",
        created_at=datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
        conditions=conditions,
    )


def _simulation(
    frequencies: tuple[float, ...] = (6_900_000.0, 7_100_000.0, 7_300_000.0),
) -> SimulationResult:
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(frequencies[0], frequencies[-1], len(frequencies))
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=tuple(
            FrequencyResult(
                frequency_hz=frequency,
                feed_tag=1,
                feed_segment=1,
                impedance_ohm=complex(50.0, 0.0),
                swr=1.0,
                input_power_w=0.001,
            )
            for frequency in frequencies
        ),
        duration_s=0.0,
    )


def test_documented_measurement_with_full_coverage() -> None:
    measurement = _measurement(
        calibration="SOL",
        reference_plane="antenna terminals",
        feed_line="10 m RG-58",
    )

    assessment = assess_measurement_uncertainty(
        measurement,
        session=_session(),
        simulation=_simulation(),
    )

    assert assessment.level is MeasurementUncertaintyLevel.DOCUMENTED
    assert assessment.calibration_status is MeasurementDocumentationStatus.DOCUMENTED
    assert assessment.reference_plane_status is MeasurementDocumentationStatus.DOCUMENTED
    assert assessment.feed_line_status is MeasurementDocumentationStatus.DOCUMENTED
    assert assessment.conditions_status is MeasurementDocumentationStatus.DOCUMENTED
    assert assessment.compared_count == 2
    assert assessment.coverage_fraction == pytest.approx(1.0)
    assert assessment.warnings == ()


def test_missing_metadata_is_limited_and_warned() -> None:
    assessment = assess_measurement_uncertainty(_measurement())

    assert assessment.level is MeasurementUncertaintyLevel.LIMITED
    assert assessment.calibration_status is MeasurementDocumentationStatus.MISSING
    assert "measurement.uncertainty.warning.calibration_missing" in assessment.warnings
    assert "measurement.uncertainty.warning.reference_plane_missing" in assessment.warnings
    assert "measurement.uncertainty.warning.feed_line_missing" in assessment.warnings
    assert "measurement.uncertainty.warning.conditions_missing" in assessment.warnings
    assert "measurement.uncertainty.warning.no_comparison" not in assessment.warnings


def test_unrecognized_calibration_is_uncertain() -> None:
    assessment = assess_measurement_uncertainty(_measurement(calibration="unknown"))

    assert assessment.calibration_status is MeasurementDocumentationStatus.UNCERTAIN
    assert "measurement.uncertainty.warning.calibration_unverified" in assessment.warnings


def test_partial_simulation_coverage_is_flagged() -> None:
    measurement = _measurement(
        MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
        MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        MeasurementPoint(7_200_000.0, complex(50.0, 0.0)),
        MeasurementPoint(7_300_000.0, complex(50.0, 0.0)),
    )

    assessment = assess_measurement_uncertainty(
        measurement,
        simulation=_simulation((7_000_000.0, 7_050_000.0)),
    )

    assert assessment.compared_count == 1
    assert assessment.coverage_fraction == pytest.approx(0.25)
    assert "measurement.uncertainty.warning.partial_comparison" in assessment.warnings


def test_no_overlap_is_flagged() -> None:
    measurement = _measurement(
        MeasurementPoint(14_000_000.0, complex(50.0, -10.0)),
        MeasurementPoint(14_100_000.0, complex(50.0, 10.0)),
    )

    assessment = assess_measurement_uncertainty(
        measurement,
        simulation=_simulation(),
    )

    assert assessment.compared_count == 0
    assert assessment.coverage_fraction == pytest.approx(0.0)
    assert "measurement.uncertainty.warning.no_comparison" in assessment.warnings


def test_multiple_resonances_and_no_simulation() -> None:
    measurement = _measurement(
        MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
        MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        MeasurementPoint(7_200_000.0, complex(50.0, 10.0)),
        MeasurementPoint(13_900_000.0, complex(50.0, 10.0)),
        MeasurementPoint(14_000_000.0, complex(50.0, -10.0)),
    )

    assessment = assess_measurement_uncertainty(measurement)

    assert len(assessment.resonance_frequencies_hz) == 2
    assert "measurement.uncertainty.warning.multiple_resonances" in assessment.warnings
    assert assessment.compared_count is None
    assert assessment.coverage_fraction is None


def test_sweep_statistics_are_exposed() -> None:
    assessment = assess_measurement_uncertainty(
        _measurement(
            MeasurementPoint(7_000_000.0, complex(50.0, 0.0)),
            MeasurementPoint(7_050_000.0, complex(50.0, 0.0)),
            MeasurementPoint(7_200_000.0, complex(50.0, 0.0)),
        )
    )

    assert assessment.point_count == 3
    assert assessment.start_frequency_hz == pytest.approx(7_000_000.0)
    assert assessment.stop_frequency_hz == pytest.approx(7_200_000.0)
    assert assessment.max_spacing_hz == pytest.approx(150_000.0)
