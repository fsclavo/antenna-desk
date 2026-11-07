# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from datetime import UTC, datetime

import pytest

from antennadesk.domain.optimization.descriptor import FamilyOptimizationObjective
from antennadesk.domain.optimization.engine import (
    CandidateEvaluation,
    OptimizationStatus,
    SensitivityPoint,
)
from antennadesk.domain.optimization.pareto import pareto_front
from antennadesk.domain.optimization.recommendations import (
    RecommendationContext,
    build_recommendations,
)
from antennadesk.domain.optimization.summary import (
    OptimizationMode,
    OptimizationRecommendation,
    OptimizationSummary,
    RecommendationSeverity,
)

COMPLETED_AT = datetime(2026, 11, 7, 12, 0, tzinfo=UTC)


def _summary(**overrides: object) -> OptimizationSummary:
    values: dict[str, object] = {
        "mode": OptimizationMode.BAND_AWARE,
        "objective": "min_swr",
        "status": "converged",
        "budget_profile": "balanced",
        "evaluations": 120,
        "seed": 7,
        "best_values": {"height_m": 10.0},
        "best_metrics": {"swr": 1.2},
        "completed_at": COMPLETED_AT,
        "band_edges_hz": (7_200_000.0, 7_000_000.0, 7_100_000.0),
    }
    values.update(overrides)
    return OptimizationSummary(**values)  # type: ignore[arg-type]


def test_summary_normalizes_mode_edges_and_copies_mappings() -> None:
    summary = _summary(mode="robust")

    assert summary.mode is OptimizationMode.ROBUST
    assert summary.band_edges_hz == (7_000_000.0, 7_100_000.0, 7_200_000.0)
    assert summary.best_values == {"height_m": 10.0}


def test_summary_rejects_a_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone"):
        _summary(completed_at=datetime(2026, 11, 7, 12, 0))


def test_summary_rejects_a_non_finite_metric() -> None:
    with pytest.raises(ValueError, match="finite"):
        _summary(best_metrics={"swr": float("nan")})


def test_summary_rejects_an_invalid_tolerance() -> None:
    with pytest.raises(ValueError, match="tolerance"):
        _summary(tolerance=1.0)


def _context(**overrides: object) -> RecommendationContext:
    values: dict[str, object] = {
        "status": OptimizationStatus.CONVERGED,
        "mode": OptimizationMode.SINGLE,
        "objective": FamilyOptimizationObjective.MIN_SWR,
        "best_score": 1.3,
        "best_metrics": {"swr": 1.3},
        "sensitivity": (),
        "locked_variables": 0,
    }
    values.update(overrides)
    return RecommendationContext(**values)  # type: ignore[arg-type]


def test_no_feasible_run_recommends_relaxing_the_problem() -> None:
    recommendations = build_recommendations(
        _context(status=OptimizationStatus.NO_FEASIBLE, best_score=None, best_metrics={})
    )

    assert len(recommendations) == 1
    assert recommendations[0].key == "optimize.recommend.no_feasible"
    assert recommendations[0].severity is RecommendationSeverity.WARNING


def test_cancelled_run_is_reported() -> None:
    recommendations = build_recommendations(_context(status=OptimizationStatus.CANCELLED))

    assert [item.key for item in recommendations] == ["optimize.recommend.cancelled"]


def test_high_swr_and_locked_variables_are_reported() -> None:
    recommendations = build_recommendations(_context(best_metrics={"swr": 3.2}, locked_variables=2))

    keys = [item.key for item in recommendations]
    assert "optimize.recommend.locked" in keys
    assert "optimize.recommend.high_swr" in keys


def test_swr_constraint_violation_uses_the_constraint_message() -> None:
    recommendations = build_recommendations(
        _context(
            best_metrics={"swr": 2.5},
            max_swr_constraint=2.0,
        )
    )

    assert [item.key for item in recommendations] == ["optimize.recommend.high_swr_constraint"]


def test_band_aware_spread_is_reported() -> None:
    recommendations = build_recommendations(
        _context(
            mode=OptimizationMode.BAND_AWARE,
            best_metrics={"swr": 1.5, "swr_spread": 1.2},
        )
    )

    assert "optimize.recommend.band_spread" in [item.key for item in recommendations]


def test_robust_spread_and_sensitivity_are_reported() -> None:
    recommendations = build_recommendations(
        _context(
            mode=OptimizationMode.ROBUST,
            best_score=-10.0,
            best_metrics={"swr": 1.5, "optimization_score_spread": 4.0},
            sensitivity=(
                SensitivityPoint(
                    name="height_m",
                    low_value=9.9,
                    high_value=10.1,
                    low_score=-4.0,
                    high_score=-16.0,
                    delta=12.0,
                ),
            ),
        )
    )

    keys = [item.key for item in recommendations]
    assert "optimize.recommend.robust" in keys
    assert "optimize.recommend.sensitive" in keys
    sensitive = next(item for item in recommendations if item.key == "optimize.recommend.sensitive")
    assert sensitive.variables == ("height_m",)


def _evaluation(
    index: int,
    swr: float,
    gain: float,
    *,
    feasible: bool = True,
) -> CandidateEvaluation:
    return CandidateEvaluation(
        index=index,
        values={"length_m": float(index)},
        score=swr - gain,
        feasible=feasible,
        metrics={"swr": swr, "max_gain_db": gain},
    )


def test_pareto_front_keeps_trade_offs_and_drops_dominated_candidates() -> None:
    evaluations = (
        _evaluation(1, 1.5, 5.0),
        _evaluation(2, 1.2, 4.0),
        _evaluation(3, 2.0, 6.0),
        _evaluation(4, 1.6, 4.5),
        _evaluation(5, 1.0, 2.0, feasible=False),
    )

    front = pareto_front(evaluations)

    assert {candidate.index for candidate in front} == {1, 2, 3}


def test_pareto_front_needs_two_common_metrics() -> None:
    evaluations = (
        CandidateEvaluation(
            index=1,
            values={},
            score=1.0,
            feasible=True,
            metrics={"swr": 1.5},
        ),
        CandidateEvaluation(
            index=2,
            values={},
            score=2.0,
            feasible=True,
            metrics={"swr": 1.2},
        ),
    )

    assert pareto_front(evaluations) == ()


def test_recommendation_requires_a_key() -> None:
    with pytest.raises(ValueError, match="key"):
        OptimizationRecommendation("")
