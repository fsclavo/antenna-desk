# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from antennadesk.domain.measurement import Measurement, MeasurementPoint
from antennadesk.domain.measurement_comparison import (
    compare_measurement,
    compare_measurement_pair,
    interpolate_impedance,
)


def _measurement(*points: MeasurementPoint) -> Measurement:
    return Measurement(
        id=UUID("00000000-0000-0000-0000-000000000010"),
        name="Field sweep",
        created_at=datetime(2026, 10, 31, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=points,
    )


def test_interpolates_complex_impedance_between_points() -> None:
    result = interpolate_impedance(
        [7_000_000.0, 7_200_000.0],
        [complex(50.0, -10.0), complex(70.0, 10.0)],
        7_100_000.0,
    )

    assert result == pytest.approx(complex(60.0, 0.0))


def test_interpolation_returns_none_outside_the_sweep() -> None:
    assert (
        interpolate_impedance(
            [7_000_000.0, 7_200_000.0],
            [complex(50.0, 0.0), complex(70.0, 0.0)],
            6_900_000.0,
        )
        is None
    )


def test_comparison_reports_error_and_summary() -> None:
    measurement = _measurement(
        MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
        MeasurementPoint(7_100_000.0, complex(60.0, 0.0)),
        MeasurementPoint(7_300_000.0, complex(80.0, 20.0)),
    )

    comparison = compare_measurement(
        measurement,
        [7_000_000.0, 7_100_000.0, 7_200_000.0],
        [complex(52.0, -10.0), complex(61.0, 0.0), complex(72.0, 10.0)],
    )

    assert comparison.compared_count == 2
    assert comparison.points[0].error_ohm == pytest.approx(2.0)
    assert comparison.points[1].error_ohm == pytest.approx(1.0)
    assert comparison.points[2].simulated_ohm is None
    assert comparison.mean_error_ohm == pytest.approx(1.5)
    assert comparison.max_error_ohm == pytest.approx(2.0)


def _pair_measurement(
    *points: MeasurementPoint,
    name: str,
) -> Measurement:
    return Measurement(
        id=UUID("00000000-0000-0000-0000-000000000011"),
        name=name,
        created_at=datetime(2026, 10, 31, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=points,
    )


def test_pair_comparison_aligns_the_overlapping_range() -> None:
    before = _pair_measurement(
        MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
        MeasurementPoint(7_200_000.0, complex(70.0, 10.0)),
        name="Before",
    )
    after = _pair_measurement(
        MeasurementPoint(7_100_000.0, complex(55.0, 0.0)),
        MeasurementPoint(7_300_000.0, complex(75.0, 20.0)),
        name="After",
    )

    comparison = compare_measurement_pair(before, after)

    assert comparison.compared_count == 2
    assert [point.frequency_hz for point in comparison.points] == pytest.approx(
        [7_100_000.0, 7_200_000.0]
    )
    assert comparison.points[0].before_ohm == pytest.approx(complex(60.0, 0.0))
    assert comparison.points[0].after_ohm == pytest.approx(complex(55.0, 0.0))
    assert comparison.points[1].before_ohm == pytest.approx(complex(70.0, 10.0))
    assert comparison.points[1].after_ohm == pytest.approx(complex(65.0, 10.0))
    assert comparison.mean_impedance_delta_ohm == pytest.approx(5.0)
    assert comparison.max_impedance_delta_ohm == pytest.approx(5.0)


def test_pair_comparison_reports_swr_delta() -> None:
    before = _pair_measurement(
        MeasurementPoint(7_000_000.0, complex(50.0, 0.0)),
        MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),
        MeasurementPoint(7_200_000.0, complex(50.0, 0.0)),
        name="Before",
    )
    after = _pair_measurement(
        MeasurementPoint(7_000_000.0, complex(75.0, 0.0)),
        MeasurementPoint(7_100_000.0, complex(75.0, 0.0)),
        MeasurementPoint(7_200_000.0, complex(75.0, 0.0)),
        name="After",
    )

    comparison = compare_measurement_pair(before, after)

    assert comparison.mean_swr_before == pytest.approx(1.0, rel=1e-9)
    assert comparison.mean_swr_after == pytest.approx(1.5, rel=1e-9)
    assert comparison.points[0].swr_delta == pytest.approx(0.5, rel=1e-9)


def test_pair_comparison_reports_resonance_shift() -> None:
    before = _pair_measurement(
        MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
        MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        name="Before",
    )
    after = _pair_measurement(
        MeasurementPoint(7_000_000.0, complex(75.0, 0.0)),
        MeasurementPoint(7_100_000.0, complex(75.0, 10.0)),
        name="After",
    )

    comparison = compare_measurement_pair(before, after)

    assert len(comparison.before_resonances) == 1
    assert len(comparison.after_resonances) == 1
    assert comparison.resonance_shift_hz == pytest.approx(-50_000.0)


def test_pair_comparison_without_overlap_has_no_points() -> None:
    before = _pair_measurement(
        MeasurementPoint(7_000_000.0, complex(50.0, 0.0)),
        MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),
        name="Before",
    )
    after = _pair_measurement(
        MeasurementPoint(14_000_000.0, complex(50.0, 0.0)),
        MeasurementPoint(14_100_000.0, complex(50.0, 0.0)),
        name="After",
    )

    comparison = compare_measurement_pair(before, after)

    assert comparison.compared_count == 0
    assert comparison.points == ()
    assert comparison.mean_impedance_delta_ohm is None
    assert comparison.mean_swr_before is None
    assert comparison.mean_swr_after is None


def test_pair_comparison_does_not_claim_a_shift_with_multiple_resonances() -> None:
    before = _pair_measurement(
        MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
        MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        MeasurementPoint(7_200_000.0, complex(50.0, -10.0)),
        MeasurementPoint(7_300_000.0, complex(50.0, 10.0)),
        name="Before",
    )
    after = _pair_measurement(
        MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
        MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        MeasurementPoint(7_200_000.0, complex(50.0, -10.0)),
        MeasurementPoint(7_300_000.0, complex(50.0, 10.0)),
        name="After",
    )

    comparison = compare_measurement_pair(before, after)

    assert len(comparison.before_resonances) > 1
    assert len(comparison.after_resonances) > 1
    assert comparison.resonance_shift_hz is None
