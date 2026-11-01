# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from antennadesk.domain.measurement import Measurement, MeasurementPoint
from antennadesk.domain.measurement_comparison import (
    compare_measurement,
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
