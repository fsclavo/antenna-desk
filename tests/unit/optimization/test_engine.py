# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.optimization.engine import (
    BudgetProfile,
    CandidateEvaluation,
    OptimizationBudget,
    OptimizationStatus,
    OptimizerRunResult,
    budget_for,
    optimize_design,
)
from antennadesk.domain.optimization.variables import OptimizationVariable, VariableKind


def _quadratic(values: dict[str, float]) -> CandidateEvaluation:
    score = (values["x"] - 1.2) ** 2 + (values["y"] - 3.1) ** 2
    return CandidateEvaluation(0, values, score, True)


def test_hybrid_engine_finds_a_continuous_optimum() -> None:
    variables = (
        OptimizationVariable("x", "field.length", "g", -5.0, 5.0, step=0.01),
        OptimizationVariable("y", "field.height", "g", -5.0, 5.0, step=0.01),
    )

    result = optimize_design(
        variables,
        {"x": 2.0, "y": -2.0},
        _quadratic,
        budget=OptimizationBudget(80, 80, 10),
        seed=7,
    )

    assert result.status is OptimizationStatus.CONVERGED
    assert result.best_values is not None
    assert result.best_values["x"] == pytest.approx(1.2, abs=0.05)
    assert result.best_values["y"] == pytest.approx(3.1, abs=0.05)
    assert result.best_score is not None
    assert result.best_score < 1e-3


def test_engine_is_deterministic_for_a_fixed_seed() -> None:
    variables = (
        OptimizationVariable("x", "field.length", "g", -5.0, 5.0),
        OptimizationVariable("y", "field.height", "g", -5.0, 5.0),
    )

    first = optimize_design(
        variables,
        {"x": 2.0, "y": -2.0},
        _quadratic,
        budget=OptimizationBudget(40, 40, 8),
        seed=11,
    )
    second = optimize_design(
        variables,
        {"x": 2.0, "y": -2.0},
        _quadratic,
        budget=OptimizationBudget(40, 40, 8),
        seed=11,
    )

    assert first.best_values == second.best_values
    assert first.best_score == second.best_score
    assert [item.values for item in first.evaluations] == [
        item.values for item in second.evaluations
    ]


def test_batch_engine_is_deterministic_and_preserves_order() -> None:
    variables = (
        OptimizationVariable("x", "field.length", "g", -5.0, 5.0, step=0.01),
        OptimizationVariable("y", "field.height", "g", -5.0, 5.0, step=0.01),
    )
    batch_sizes: list[int] = []

    def batch_evaluate(values: list[dict[str, float]]) -> list[CandidateEvaluation]:
        batch_sizes.append(len(values))
        return [_quadratic(dict(item)) for item in values]

    def run() -> OptimizerRunResult:
        return optimize_design(
            variables,
            {"x": 2.0, "y": -2.0},
            _quadratic,
            budget=OptimizationBudget(80, 40, 8),
            seed=17,
            batch_evaluate=batch_evaluate,
        )

    first = run()
    second = run()

    assert first == second
    assert any(size > 1 for size in batch_sizes)
    assert [item.index for item in first.evaluations] == list(range(1, len(first.evaluations) + 1))


def test_batch_engine_falls_back_when_the_batch_evaluator_raises() -> None:
    variables = (
        OptimizationVariable("x", "field.length", "g", -5.0, 5.0, step=0.01),
        OptimizationVariable("y", "field.height", "g", -5.0, 5.0, step=0.01),
    )

    def failing_batch(values: list[dict[str, float]]) -> list[CandidateEvaluation]:
        raise RuntimeError("batch failed")

    result = optimize_design(
        variables,
        {"x": 2.0, "y": -2.0},
        _quadratic,
        budget=OptimizationBudget(40, 20, 6),
        seed=11,
        batch_evaluate=failing_batch,
    )

    assert result.status in {
        OptimizationStatus.CONVERGED,
        OptimizationStatus.MAX_EVALUATIONS,
    }
    assert result.evaluations
    assert result.best_score is not None


def test_batch_engine_falls_back_on_a_wrong_batch_size() -> None:
    variables = (
        OptimizationVariable("x", "field.length", "g", -5.0, 5.0, step=0.01),
        OptimizationVariable("y", "field.height", "g", -5.0, 5.0, step=0.01),
    )

    def short_batch(values: list[dict[str, float]]) -> list[CandidateEvaluation]:
        return [_quadratic(dict(values[0]))] if values else []

    result = optimize_design(
        variables,
        {"x": 2.0, "y": -2.0},
        _quadratic,
        budget=OptimizationBudget(40, 20, 6),
        seed=11,
        batch_evaluate=short_batch,
    )

    assert result.status in {
        OptimizationStatus.CONVERGED,
        OptimizationStatus.MAX_EVALUATIONS,
    }
    assert result.evaluations
    assert result.best_score is not None


def test_batch_engine_reports_cancellation_before_a_batch() -> None:
    variables = (
        OptimizationVariable("x", "field.length", "g", -5.0, 5.0, step=0.01),
        OptimizationVariable("y", "field.height", "g", -5.0, 5.0, step=0.01),
    )
    cancel_calls = 0

    def cancel_check() -> bool:
        nonlocal cancel_calls
        cancel_calls += 1
        return cancel_calls > 1

    def batch_evaluate(values: list[dict[str, float]]) -> list[CandidateEvaluation]:
        return [_quadratic(dict(item)) for item in values]

    result = optimize_design(
        variables,
        {"x": 2.0, "y": -2.0},
        _quadratic,
        budget=OptimizationBudget(40, 20, 6),
        seed=11,
        cancel_check=cancel_check,
        batch_evaluate=batch_evaluate,
    )

    assert result.status is OptimizationStatus.CANCELLED
    assert len(result.evaluations) == 1


def test_engine_prefers_a_feasible_candidate() -> None:
    variables = (OptimizationVariable("x", "field.length", "g", 0.0, 1.0),)

    def evaluate(values: dict[str, float]) -> CandidateEvaluation:
        x = values["x"]
        feasible = x >= 0.5
        return CandidateEvaluation(
            index=0,
            values=values,
            score=abs(x - 0.8),
            feasible=feasible,
            violation=0.0 if feasible else 0.5 - x,
        )

    result = optimize_design(
        variables,
        {"x": 0.1},
        evaluate,
        budget=OptimizationBudget(60, 60, 8),
        seed=3,
    )

    assert result.best_values is not None
    assert result.best_values["x"] >= 0.5
    assert result.best_values["x"] == pytest.approx(0.8, abs=0.05)


def test_engine_handles_integer_variables() -> None:
    variables = (
        OptimizationVariable(
            "count",
            "vertical.radial_count",
            "g",
            1.0,
            20.0,
            kind=VariableKind.INTEGER,
            unit="count",
            step=1.0,
        ),
    )

    def evaluate(values: dict[str, float]) -> CandidateEvaluation:
        return CandidateEvaluation(0, values, abs(values["count"] - 7.0), True)

    result = optimize_design(
        variables,
        {"count": 2.0},
        evaluate,
        budget=OptimizationBudget(40, 40, 8),
        seed=4,
    )

    assert result.best_values is not None
    assert result.best_values["count"] == pytest.approx(7.0)
    assert result.best_values["count"].is_integer()


def test_engine_handles_choice_variables() -> None:
    variables = (
        OptimizationVariable(
            "ratio",
            "field.family",
            "g",
            1.0,
            49.0,
            kind=VariableKind.CHOICE,
            choices=(1.0, 4.0, 9.0, 49.0),
        ),
    )

    def evaluate(values: dict[str, float]) -> CandidateEvaluation:
        return CandidateEvaluation(0, values, abs(values["ratio"] - 9.0), True)

    result = optimize_design(
        variables,
        {"ratio": 1.0},
        evaluate,
        budget=OptimizationBudget(40, 40, 8),
        seed=8,
    )

    assert result.best_values is not None
    assert result.best_values["ratio"] == pytest.approx(9.0)


def test_engine_extends_the_budget_after_a_late_improvement() -> None:
    variables = (
        OptimizationVariable("x", "field.length", "g", 0.0, 1.0),
        OptimizationVariable("y", "field.height", "g", 0.0, 1.0),
    )
    calls = {"count": 0}

    def evaluate(values: dict[str, float]) -> CandidateEvaluation:
        calls["count"] += 1
        score = 1.0 if calls["count"] < 35 else 0.0
        return CandidateEvaluation(0, values, score, True)

    budget = OptimizationBudget(40, 40, 8)
    result = optimize_design(
        variables,
        {"x": 0.1, "y": 0.1},
        evaluate,
        budget=budget,
        seed=1,
    )

    assert len(result.evaluations) > budget.total
    assert result.best_score == pytest.approx(0.0)


def test_engine_reports_no_feasible_design() -> None:
    variables = (OptimizationVariable("x", "field.length", "g", 0.0, 1.0),)

    def evaluate(values: dict[str, float]) -> CandidateEvaluation:
        return CandidateEvaluation(0, values, None, False, violation=1.0)

    result = optimize_design(
        variables,
        {"x": 0.5},
        evaluate,
        budget=OptimizationBudget(20, 20, 5),
        seed=1,
    )

    assert result.status is OptimizationStatus.NO_FEASIBLE
    assert result.best_values is None


def test_engine_cancellation_is_reported() -> None:
    variables = (OptimizationVariable("x", "field.length", "g", 0.0, 1.0),)

    def evaluate(values: dict[str, float]) -> CandidateEvaluation:
        return CandidateEvaluation(0, values, values["x"], True)

    result = optimize_design(
        variables,
        {"x": 0.5},
        evaluate,
        budget=OptimizationBudget(20, 20, 5),
        seed=1,
        cancel_check=lambda: True,
    )

    assert result.status is OptimizationStatus.CANCELLED


def test_budget_profiles_follow_the_agreed_formulas() -> None:
    fast = budget_for(BudgetProfile.FAST, 3)
    balanced = budget_for(BudgetProfile.BALANCED, 3)
    thorough = budget_for(BudgetProfile.THOROUGH, 3)

    assert fast.global_evaluations == max(60, 12 * 3)
    assert fast.local_evaluations == max(40, 8 * 3)
    assert balanced.global_evaluations == max(120, 30 * 3)
    assert balanced.local_evaluations == max(80, 20 * 3)
    assert thorough.global_evaluations == max(1_500, 200 * 3)
    assert thorough.local_evaluations == max(1_000, 100 * 3)


def test_variable_validation_and_fraction_round_trip() -> None:
    variable = OptimizationVariable("x", "field.length", "g", 1.0, 3.0)
    assert variable.from_fraction(0.5) == pytest.approx(2.0)
    assert variable.to_fraction(2.0) == pytest.approx(0.5)
    assert variable.clamp(10.0) == pytest.approx(3.0)

    count = OptimizationVariable(
        "count",
        "vertical.radial_count",
        "g",
        1.0,
        10.0,
        kind=VariableKind.INTEGER,
        unit="count",
    )
    assert count.from_fraction(0.5) == pytest.approx(6.0)
    assert count.next_value(5.0, 1) == pytest.approx(6.0)
    assert count.next_value(5.0, -1) == pytest.approx(4.0)

    with pytest.raises(ValueError, match="maximum"):
        OptimizationVariable("bad", "field.length", "g", 2.0, 2.0)


def test_choice_variable_selects_declared_values() -> None:
    variable = OptimizationVariable(
        "ratio",
        "field.family",
        "g",
        1.0,
        49.0,
        kind=VariableKind.CHOICE,
        choices=(1.0, 4.0, 9.0, 49.0),
    )

    assert variable.from_fraction(0.0) == pytest.approx(1.0)
    assert variable.from_fraction(0.5) == pytest.approx(9.0)
    assert variable.from_fraction(1.0) == pytest.approx(49.0)
    assert math.isclose(variable.to_fraction(9.0), 2.0 / 3.0)
