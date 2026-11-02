# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded coordinate search for several antenna parameters."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum


class BoundedStatus(StrEnum):
    CONVERGED = "converged"
    MAX_EVALUATIONS = "max_evaluations"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class BoundedVariable:
    name: str
    minimum: float
    maximum: float
    integer: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("bounded variable name must not be empty")
        if not math.isfinite(self.minimum) or not math.isfinite(self.maximum):
            raise ValueError("bounded variable limits must be finite")
        if self.maximum <= self.minimum:
            raise ValueError("bounded variable maximum must exceed minimum")


@dataclass(frozen=True, slots=True)
class BoundedEvaluation:
    index: int
    values: Mapping[str, float]
    score: float | None
    metrics: Mapping[str, float] = field(default_factory=dict)
    error: str | None = None
    cancelled: bool = False


@dataclass(frozen=True, slots=True)
class BoundedResult:
    status: BoundedStatus
    best_values: Mapping[str, float] | None
    best_score: float | None
    evaluations: tuple[BoundedEvaluation, ...]
    message: str = ""


BoundedEvaluator = Callable[[Mapping[str, float]], BoundedEvaluation]
CancelCheck = Callable[[], bool]


def rank_bounded(
    evaluations: Sequence[BoundedEvaluation],
) -> tuple[BoundedEvaluation, ...]:
    """Order evaluations by ascending score, with failures last."""

    def key(evaluation: BoundedEvaluation) -> tuple[int, float, int]:
        if evaluation.score is None:
            return (1, math.inf, evaluation.index)
        return (0, evaluation.score, evaluation.index)

    return tuple(sorted(evaluations, key=key))


def _sample_values(
    minimum: float,
    maximum: float,
    count: int,
    *,
    integer: bool = False,
) -> tuple[float, ...]:
    if count <= 1:
        value = (minimum + maximum) / 2.0
        return (float(round(value)) if integer else value,)
    step = (maximum - minimum) / (count - 1)
    values = [minimum + index * step for index in range(count)]
    if integer:
        return tuple(sorted({float(round(value)) for value in values}))
    return tuple(values)


def optimize_bounded(
    evaluate: BoundedEvaluator,
    variables: Sequence[BoundedVariable],
    start_values: Mapping[str, float],
    *,
    max_evaluations: int = 81,
    samples: int = 5,
    passes: int = 4,
    cancel_check: CancelCheck | None = None,
) -> BoundedResult:
    """Coordinate search over bounded variables; lower scores are better."""

    if not variables:
        raise ValueError("at least one bounded variable is required")
    if max_evaluations < 1:
        raise ValueError("max_evaluations must be positive")
    if samples < 3:
        raise ValueError("samples must be at least 3")
    if passes < 1:
        raise ValueError("passes must be at least 1")

    names = [variable.name for variable in variables]
    if len(set(names)) != len(names):
        raise ValueError("bounded variable names must be unique")
    limits = {variable.name: (variable.minimum, variable.maximum) for variable in variables}
    current = {}
    for variable in variables:
        value = min(
            max(start_values.get(variable.name, variable.minimum), variable.minimum),
            variable.maximum,
        )
        current[variable.name] = float(round(value)) if variable.integer else value
    bounds = dict(limits)
    evaluations: list[BoundedEvaluation] = []

    def cancelled() -> bool:
        return bool(cancel_check is not None and cancel_check())

    def probe(values: Mapping[str, float]) -> BoundedEvaluation | None:
        if len(evaluations) >= max_evaluations:
            return None
        raw = evaluate(dict(values))
        evaluation = BoundedEvaluation(
            index=len(evaluations) + 1,
            values=dict(values),
            score=raw.score,
            metrics=dict(raw.metrics),
            error=raw.error,
            cancelled=raw.cancelled,
        )
        evaluations.append(evaluation)
        return evaluation

    def result(status: BoundedStatus, message: str = "") -> BoundedResult:
        ranked = rank_bounded(evaluations)
        best = ranked[0] if ranked and ranked[0].score is not None else None
        return BoundedResult(
            status=status,
            best_values=None if best is None else dict(best.values),
            best_score=None if best is None else best.score,
            evaluations=tuple(evaluations),
            message=message,
        )

    if cancelled():
        return result(BoundedStatus.CANCELLED, "optimization cancelled")

    initial = probe(current)
    if initial is None:
        return result(BoundedStatus.ERROR, "no evaluation budget")
    if initial.cancelled:
        return result(BoundedStatus.CANCELLED, "optimization cancelled")
    if initial.score is None:
        return result(BoundedStatus.ERROR, initial.error or "initial evaluation failed")

    for _pass in range(passes):
        if cancelled():
            return result(BoundedStatus.CANCELLED, "optimization cancelled")
        for variable in variables:
            if len(evaluations) >= max_evaluations:
                return result(
                    BoundedStatus.MAX_EVALUATIONS,
                    "maximum number of evaluations reached",
                )
            low, high = bounds[variable.name]
            candidates = _sample_values(low, high, samples, integer=variable.integer)
            best_candidate: tuple[float, float] | None = None
            for value in candidates:
                if cancelled():
                    return result(BoundedStatus.CANCELLED, "optimization cancelled")
                values = dict(current)
                values[variable.name] = value
                evaluation = probe(values)
                if evaluation is None:
                    return result(
                        BoundedStatus.MAX_EVALUATIONS,
                        "maximum number of evaluations reached",
                    )
                if evaluation.cancelled:
                    return result(BoundedStatus.CANCELLED, "optimization cancelled")
                if evaluation.score is not None and (
                    best_candidate is None or evaluation.score < best_candidate[1]
                ):
                    best_candidate = (value, evaluation.score)
            if best_candidate is None:
                continue
            best_value = best_candidate[0]
            current[variable.name] = best_value
            step = (high - low) / (samples - 1)
            original_low, original_high = limits[variable.name]
            bounds[variable.name] = (
                max(original_low, best_value - step),
                min(original_high, best_value + step),
            )

    return result(BoundedStatus.CONVERGED, "coordinate search completed")
