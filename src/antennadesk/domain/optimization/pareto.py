# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-dominated ranking for pattern optimization metrics."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

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
