# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-dominated ranking for pattern optimization metrics."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from .engine import CandidateEvaluation
from .multi_variable import BoundedEvaluation


@dataclass(frozen=True, slots=True)
class ParetoObjectives:
    gain: bool = True
    front_to_back: bool = True
    swr: bool = True
    efficiency: bool = False


def _vector(
    evaluation: BoundedEvaluation,
    objectives: ParetoObjectives,
) -> tuple[float, ...] | None:
    values: list[float] = []
    if objectives.gain:
        value = evaluation.metrics.get("max_gain_db")
        if value is None or not math.isfinite(value):
            return None
        values.append(-value)
    if objectives.front_to_back:
        value = evaluation.metrics.get("front_to_back_db")
        if value is None or not math.isfinite(value):
            return None
        values.append(-value)
    if objectives.swr:
        value = evaluation.metrics.get("swr")
        if value is None or not math.isfinite(value):
            return None
        values.append(value)
    if objectives.efficiency:
        value = evaluation.metrics.get("efficiency_percent")
        if value is None or not math.isfinite(value):
            return None
        values.append(-value)
    return tuple(values) if values else None


def _dominates(first: tuple[float, ...], second: tuple[float, ...]) -> bool:
    return all(a <= b for a, b in zip(first, second, strict=True)) and any(
        a < b for a, b in zip(first, second, strict=True)
    )


def pareto_ranks(
    evaluations: Sequence[BoundedEvaluation],
    objectives: ParetoObjectives,
) -> dict[int, int]:
    """Return rank 1 for the first Pareto front, rank 2 for the next, etc."""

    remaining = {
        evaluation.index: vector
        for evaluation in evaluations
        if (vector := _vector(evaluation, objectives)) is not None
    }
    ranks: dict[int, int] = {}
    rank = 1
    while remaining:
        front = [
            index
            for index, vector in remaining.items()
            if not any(
                _dominates(other, vector)
                for other_index, other in remaining.items()
                if other_index != index
            )
        ]
        if not front:
            break
        for index in front:
            ranks[index] = rank
            del remaining[index]
        rank += 1
    return ranks


@dataclass(frozen=True, slots=True)
class ParetoCandidate:
    """One non-dominated family-optimizer evaluation."""

    index: int
    score: float
    values: Mapping[str, float] = field(default_factory=dict)
    metrics: Mapping[str, float] = field(default_factory=dict)


# Lower is better for every metric after applying its sign.
_CANDIDATE_METRICS: tuple[tuple[str, float], ...] = (
    ("swr", 1.0),
    ("target_error_ohm", 1.0),
    ("max_gain_db", -1.0),
    ("front_to_back_db", -1.0),
    ("efficiency_percent", -1.0),
    ("bandwidth_hz", -1.0),
)


def _candidate_vector(
    evaluation: CandidateEvaluation,
    metrics: Sequence[tuple[str, float]],
) -> tuple[float, ...]:
    values: list[float] = []
    for name, direction in metrics:
        value = evaluation.metrics.get(name)
        if value is None or not math.isfinite(value):
            return ()
        values.append(direction * value)
    return tuple(values)


def pareto_front(
    evaluations: Sequence[CandidateEvaluation],
) -> tuple[ParetoCandidate, ...]:
    """Return the feasible non-dominated evaluations across shared metrics.

    A meaningful front needs at least two common metrics. Runs without gain,
    front-to-back, efficiency, or bandwidth data return an empty front instead
    of a degenerate single-objective list.
    """

    feasible = [
        evaluation
        for evaluation in evaluations
        if evaluation.feasible and evaluation.score is not None and evaluation.metrics
    ]
    if not feasible:
        return ()
    active = tuple(
        (name, direction)
        for name, direction in _CANDIDATE_METRICS
        if all(
            (value := evaluation.metrics.get(name)) is not None and math.isfinite(value)
            for evaluation in feasible
        )
    )
    if len(active) < 2:
        return ()
    vectors = {evaluation.index: _candidate_vector(evaluation, active) for evaluation in feasible}
    front = [
        evaluation
        for evaluation in feasible
        if not any(
            other.index != evaluation.index
            and _dominates(vectors[other.index], vectors[evaluation.index])
            for other in feasible
        )
    ]
    return tuple(
        ParetoCandidate(
            index=evaluation.index,
            score=float(evaluation.score or 0.0),
            values=dict(evaluation.values),
            metrics=dict(evaluation.metrics),
        )
        for evaluation in sorted(front, key=lambda item: (item.score, item.index))
    )
