# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic post-run guidance derived from optimizer evidence.

The rules are intentionally conservative and only describe the search or the
modeled metrics. They never claim that a physical antenna will behave in a
particular way without validation.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass

from .descriptor import FamilyOptimizationObjective
from .engine import OptimizationStatus, SensitivityPoint
from .summary import (
    OptimizationMode,
    OptimizationRecommendation,
    RecommendationSeverity,
)

HIGH_SWR = 2.0
BAND_SWR_SPREAD = 0.5
SENSITIVITY_FRACTION = 0.25
ROBUST_SPREAD_FRACTION = 0.1


@dataclass(frozen=True, slots=True)
class RecommendationContext:
    status: OptimizationStatus
    mode: OptimizationMode
    objective: FamilyOptimizationObjective
    best_score: float | None
    best_metrics: Mapping[str, float]
    sensitivity: tuple[SensitivityPoint, ...]
    locked_variables: int
    max_swr_constraint: float | None = None
    tolerance: float = 0.0


def _finite(metrics: Mapping[str, float], name: str) -> float | None:
    value = metrics.get(name)
    if value is None or not math.isfinite(value):
        return None
    return value


def _relative_threshold(score: float | None, fraction: float) -> float:
    if score is None or not math.isfinite(score):
        return 0.0
    return abs(score) * fraction


def build_recommendations(
    context: RecommendationContext,
) -> tuple[OptimizationRecommendation, ...]:
    """Return stable, ordered recommendations for one completed run."""

    recommendations: list[OptimizationRecommendation] = []

    if context.status is OptimizationStatus.NO_FEASIBLE:
        recommendations.append(
            OptimizationRecommendation(
                "optimize.recommend.no_feasible",
                RecommendationSeverity.WARNING,
            )
        )
        return tuple(recommendations)

    if context.status is OptimizationStatus.CANCELLED:
        recommendations.append(OptimizationRecommendation("optimize.recommend.cancelled"))
        return tuple(recommendations)

    if context.status is OptimizationStatus.MAX_EVALUATIONS:
        recommendations.append(OptimizationRecommendation("optimize.recommend.budget"))

    if context.locked_variables > 0:
        recommendations.append(OptimizationRecommendation("optimize.recommend.locked"))

    seed_count = _finite(context.best_metrics, "seed_count")
    seed_converged = _finite(context.best_metrics, "seed_converged")
    if (
        seed_count is not None
        and seed_count > 1.0
        and seed_converged is not None
        and seed_converged < 0.5
    ):
        recommendations.append(
            OptimizationRecommendation(
                "optimize.recommend.seed_divergence",
                RecommendationSeverity.WARNING,
            )
        )

    swr = _finite(context.best_metrics, "swr")
    threshold = context.max_swr_constraint
    if threshold is None:
        threshold = HIGH_SWR
    if swr is not None and swr > threshold:
        key = (
            "optimize.recommend.high_swr_constraint"
            if context.max_swr_constraint is not None
            else "optimize.recommend.high_swr"
        )
        recommendations.append(OptimizationRecommendation(key, RecommendationSeverity.WARNING))

    swr_spread = _finite(context.best_metrics, "swr_spread")
    if (
        context.mode is not OptimizationMode.SINGLE
        and swr_spread is not None
        and swr_spread > BAND_SWR_SPREAD
    ):
        recommendations.append(
            OptimizationRecommendation(
                "optimize.recommend.band_spread",
                RecommendationSeverity.WARNING,
            )
        )

    if context.mode is OptimizationMode.ROBUST:
        score_spread = _finite(context.best_metrics, "optimization_score_spread")
        threshold_value = _relative_threshold(
            context.best_score,
            ROBUST_SPREAD_FRACTION,
        )
        if score_spread is not None and score_spread > threshold_value:
            recommendations.append(
                OptimizationRecommendation(
                    "optimize.recommend.robust",
                    RecommendationSeverity.WARNING,
                )
            )

    ranked = sorted(
        (point for point in context.sensitivity if point.delta is not None),
        key=lambda point: point.delta or 0.0,
        reverse=True,
    )
    if ranked:
        strongest = ranked[0]
        threshold_value = _relative_threshold(
            context.best_score,
            SENSITIVITY_FRACTION,
        )
        if (
            strongest.delta is not None
            and strongest.delta > threshold_value
            and strongest.delta > 1e-9
        ):
            recommendations.append(
                OptimizationRecommendation(
                    "optimize.recommend.sensitive",
                    RecommendationSeverity.WARNING,
                    variables=(strongest.name,),
                )
            )

    return tuple(recommendations)
