# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Self-consistency verdicts for convergence studies."""

from __future__ import annotations

import pytest

from antennadesk.domain.simulation.convergence import (
    ConvergencePoint,
    ConvergenceResult,
    ConvergenceThresholds,
    ConvergenceVerdict,
    ConvergenceWireMetric,
    convergence_csv,
)


def _point(
    density: float,
    resistance: float,
    reactance: float,
    swr: float,
    *,
    gain: float | None = None,
    takeoff: float | None = None,
    error: str | None = None,
) -> ConvergencePoint:
    return ConvergencePoint(
        density_wavelengths=density,
        total_segments=round(10 / density),
        resistance_ohm=resistance,
        reactance_ohm=reactance,
        impedance_magnitude_ohm=(resistance**2 + reactance**2) ** 0.5,
        swr=swr,
        max_gain_db=gain,
        takeoff_deg=takeoff,
        wire_metrics=(ConvergenceWireMetric("wire", 10, 0.1, 0.001),),
        error=error,
    )


def test_converged_and_marginal_verdicts_use_the_two_finest_points() -> None:
    converged = ConvergenceResult(
        points=(
            _point(0.1, 50.0, 1.0, 1.02, gain=2.0, takeoff=10.0),
            _point(0.05, 50.2, 1.1, 1.03, gain=2.05, takeoff=10.1),
            _point(0.025, 50.3, 1.15, 1.035, gain=2.06, takeoff=10.1),
        )
    )
    marginal = ConvergenceResult(
        points=(
            _point(0.1, 48.0, 0.8, 1.0),
            _point(0.05, 52.0, 1.1, 1.05),
            _point(0.025, 54.5, 1.2, 1.08),
        )
    )

    assert converged.verdict is ConvergenceVerdict.CONVERGED
    assert marginal.verdict is ConvergenceVerdict.MARGINAL


def test_large_change_is_not_converged_and_invalid_point_is_visible() -> None:
    not_converged = ConvergenceResult(
        points=(
            _point(0.1, 40.0, 0.0, 1.2),
            _point(0.05, 50.0, 0.0, 1.0),
            _point(0.025, 70.0, -20.0, 2.5),
        )
    )
    invalid = ConvergenceResult(
        points=(
            _point(0.1, 50.0, 0.0, 1.0),
            _point(0.05, 50.0, 0.0, 1.0, error="solver failed"),
            _point(0.025, 50.0, 0.0, 1.0),
        )
    )

    assert not_converged.verdict is ConvergenceVerdict.NOT_CONVERGED
    assert invalid.verdict is ConvergenceVerdict.NOT_CONVERGED


def test_cancelled_study_is_incomplete_and_keeps_completed_points() -> None:
    result = ConvergenceResult(
        points=(
            _point(0.1, 50.0, 0.0, 1.0),
            _point(0.05, 50.0, 0.0, 1.0),
        ),
        cancelled=True,
    )

    assert result.verdict is ConvergenceVerdict.INCOMPLETE
    assert len(result.points) == 2
    assert result.swr_spread == pytest.approx(0.0)


def test_thresholds_reject_invalid_values() -> None:
    with pytest.raises(ValueError, match="marginal_factor"):
        ConvergenceThresholds(marginal_factor=0.5)
    with pytest.raises(ValueError, match="swr_absolute"):
        ConvergenceThresholds(swr_absolute=-1.0)


def test_csv_is_deterministic_and_contains_the_verdict_and_wire_metrics() -> None:
    result = ConvergenceResult(
        points=(
            _point(0.05, 50.0, 0.0, 1.0, gain=2.0, takeoff=10.0),
            _point(0.025, 50.0, 0.0, 1.0, gain=2.0, takeoff=10.0),
        )
    )

    text = convergence_csv(result)

    assert text.startswith("density_lambda,total_segments,resistance_ohm,")
    assert "converged" in text
    assert "wire:10:" in text
    assert text.count("\n") == 3
