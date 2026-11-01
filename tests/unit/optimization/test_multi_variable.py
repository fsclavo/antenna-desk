# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.optimization.multi_variable import (
    BoundedEvaluation,
    BoundedStatus,
    BoundedVariable,
    optimize_bounded,
    rank_bounded,
)


def _quadratic(values: dict[str, float]) -> BoundedEvaluation:
    score = (values["x"] - 2.0) ** 2 + (values["y"] + 1.0) ** 2
    return BoundedEvaluation(0, dict(values), score)


def test_coordinate_search_finds_a_quadratic_minimum() -> None:
    result = optimize_bounded(
        _quadratic,
        (
            BoundedVariable("x", -5.0, 5.0),
            BoundedVariable("y", -5.0, 5.0),
        ),
        {"x": 0.0, "y": 0.0},
        max_evaluations=60,
        samples=5,
        passes=5,
    )

    assert result.status is BoundedStatus.CONVERGED
    assert result.best_values is not None
    assert result.best_values["x"] == pytest.approx(2.0, abs=0.1)
    assert result.best_values["y"] == pytest.approx(-1.0, abs=0.1)
    assert result.best_score == pytest.approx(0.0, abs=0.02)


def test_coordinate_search_honours_evaluation_budget() -> None:
    result = optimize_bounded(
        _quadratic,
        (
            BoundedVariable("x", -5.0, 5.0),
            BoundedVariable("y", -5.0, 5.0),
        ),
        {"x": 0.0, "y": 0.0},
        max_evaluations=7,
        samples=5,
        passes=4,
    )

    assert result.status is BoundedStatus.MAX_EVALUATIONS
    assert len(result.evaluations) == 7


def test_coordinate_search_honours_cancellation() -> None:
    result = optimize_bounded(
        _quadratic,
        (BoundedVariable("x", -5.0, 5.0),),
        {"x": 0.0},
        max_evaluations=20,
        cancel_check=lambda: True,
    )

    assert result.status is BoundedStatus.CANCELLED
    assert not result.evaluations


def test_rank_bounded_puts_failures_last() -> None:
    evaluations = (
        BoundedEvaluation(1, {"x": 1.0}, 2.0),
        BoundedEvaluation(2, {"x": 2.0}, 1.0),
        BoundedEvaluation(3, {"x": 3.0}, None, error="failed"),
    )

    assert [evaluation.index for evaluation in rank_bounded(evaluations)] == [2, 1, 3]
