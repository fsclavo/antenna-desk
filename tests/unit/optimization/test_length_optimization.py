# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.optimization.length import (
    LengthEvaluation,
    LengthOptimizationSpec,
    LengthOptimizationStatus,
    OptimizationObjective,
    optimize_length,
)


def _linear_evaluator(
    *,
    resonance_length_m: float = 20.0,
    slope_ohm_per_m: float = 5.0,
) -> object:
    def evaluate(length_m: float) -> LengthEvaluation:
        reactance = slope_ohm_per_m * (length_m - resonance_length_m)
        return LengthEvaluation(
            length_m=length_m,
            impedance_ohm=complex(70.0, reactance),
            swr=2.0,
        )

    return evaluate


def test_converges_on_a_linear_zero_crossing() -> None:
    spec = LengthOptimizationSpec(min_length_m=18.0, max_length_m=22.0)
    result = optimize_length(_linear_evaluator(), spec)  # type: ignore[arg-type]

    assert result.status is LengthOptimizationStatus.CONVERGED
    assert result.best_length_m == pytest.approx(20.0, abs=0.02)
    assert result.best_impedance_ohm is not None
    assert result.best_impedance_ohm.imag == pytest.approx(0.0, abs=0.1)
    assert len(result.evaluations) <= spec.max_evaluations


def test_converges_on_a_target_reactance() -> None:
    spec = LengthOptimizationSpec(
        min_length_m=18.0,
        max_length_m=22.0,
        target_reactance_ohm=10.0,
    )
    result = optimize_length(_linear_evaluator(), spec)  # type: ignore[arg-type]

    assert result.status is LengthOptimizationStatus.CONVERGED
    assert result.best_length_m == pytest.approx(22.0, abs=0.1)


def test_reports_when_the_target_is_not_bracketed() -> None:
    spec = LengthOptimizationSpec(
        min_length_m=18.0,
        max_length_m=22.0,
        target_reactance_ohm=100.0,
    )
    result = optimize_length(_linear_evaluator(), spec)  # type: ignore[arg-type]

    assert result.status is LengthOptimizationStatus.NO_BRACKET
    assert result.best_length_m == pytest.approx(22.0)


def test_stops_at_max_evaluations() -> None:
    def evaluate(length_m: float) -> LengthEvaluation:
        reactance = (length_m - 20.0) ** 3 + 0.1
        return LengthEvaluation(length_m, complex(70.0, reactance), 2.0)

    spec = LengthOptimizationSpec(
        min_length_m=19.0,
        max_length_m=21.0,
        max_evaluations=3,
        reactance_tolerance_ohm=1e-9,
        length_tolerance_m=1e-9,
    )
    result = optimize_length(evaluate, spec)

    assert result.status is LengthOptimizationStatus.MAX_EVALUATIONS
    assert len(result.evaluations) == 3


def test_honours_cancellation() -> None:
    calls = 0

    def evaluate(length_m: float) -> LengthEvaluation:
        nonlocal calls
        calls += 1
        return LengthEvaluation(length_m, complex(70.0, length_m - 20.0), 2.0)

    def cancel_check() -> bool:
        return calls >= 1

    result = optimize_length(
        evaluate,
        LengthOptimizationSpec(min_length_m=18.0, max_length_m=22.0),
        cancel_check=cancel_check,
    )

    assert result.status is LengthOptimizationStatus.CANCELLED
    assert calls == 1


def test_reports_solver_failure() -> None:
    def evaluate(length_m: float) -> LengthEvaluation:
        if length_m > 19.0:
            return LengthEvaluation(length_m, None, error="solver failed")
        return LengthEvaluation(length_m, complex(70.0, length_m - 20.0), 2.0)

    result = optimize_length(
        evaluate,
        LengthOptimizationSpec(min_length_m=18.0, max_length_m=22.0),
    )

    assert result.status is LengthOptimizationStatus.ERROR
    assert result.message == "solver failed"


def _swr_evaluator(
    *,
    minimum_length_m: float = 20.3,
    minimum_swr: float = 1.0,
) -> object:
    def evaluate(length_m: float) -> LengthEvaluation:
        swr = minimum_swr + abs(length_m - minimum_length_m)
        return LengthEvaluation(
            length_m=length_m,
            impedance_ohm=complex(50.0, 0.0),
            swr=swr,
        )

    return evaluate


def test_minimizes_swr_within_the_bounds() -> None:
    spec = LengthOptimizationSpec(
        min_length_m=18.0,
        max_length_m=22.0,
        objective=OptimizationObjective.MIN_SWR,
    )
    result = optimize_length(_swr_evaluator(), spec)  # type: ignore[arg-type]

    assert result.status is LengthOptimizationStatus.CONVERGED
    assert result.best_length_m == pytest.approx(20.3, abs=0.05)
    assert result.best_swr == pytest.approx(1.0, abs=0.05)


def test_swr_search_stops_at_max_evaluations() -> None:
    spec = LengthOptimizationSpec(
        min_length_m=18.0,
        max_length_m=22.0,
        objective=OptimizationObjective.MIN_SWR,
        max_evaluations=3,
    )
    result = optimize_length(_swr_evaluator(), spec)  # type: ignore[arg-type]

    assert result.status is LengthOptimizationStatus.MAX_EVALUATIONS
    assert len(result.evaluations) == 3


def test_swr_search_reports_a_boundary_optimum() -> None:
    spec = LengthOptimizationSpec(
        min_length_m=21.0,
        max_length_m=22.0,
        objective=OptimizationObjective.MIN_SWR,
    )
    result = optimize_length(_swr_evaluator(), spec)  # type: ignore[arg-type]

    assert result.status is LengthOptimizationStatus.CONVERGED
    assert result.best_length_m == pytest.approx(21.0)
