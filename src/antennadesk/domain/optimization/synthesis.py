# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded multi-variable synthesis against a feed-point impedance target."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from ..common.units import ensure_positive


@dataclass(frozen=True, slots=True)
class SynthesisVariable:
    name: str
    minimum: float
    maximum: float

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("synthesis variable name must not be empty")
        if not math.isfinite(self.minimum) or not math.isfinite(self.maximum):
            raise ValueError("synthesis variable bounds must be finite")
        if self.maximum <= self.minimum:
            raise ValueError("synthesis variable maximum must exceed minimum")


@dataclass(frozen=True, slots=True)
class SynthesisTarget:
    frequency_hz: float
    resistance_ohm: float
    reactance_ohm: float = 0.0

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        if not math.isfinite(self.resistance_ohm) or not math.isfinite(self.reactance_ohm):
            raise ValueError("target impedance must be finite")
        if self.resistance_ohm <= 0.0:
            raise ValueError("target resistance must be positive")

    @property
    def impedance_ohm(self) -> complex:
        return complex(self.resistance_ohm, self.reactance_ohm)


class SynthesisStatus(StrEnum):
    CONVERGED = "converged"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class SynthesisEvaluation:
    index: int
    values: Mapping[str, float]
    impedance_ohm: complex | None
    swr: float | None = None
    error: str | None = None
    cancelled: bool = False


@dataclass(frozen=True, slots=True)
class SynthesisResult:
    status: SynthesisStatus
    best_values: Mapping[str, float] | None
    best_impedance_ohm: complex | None
    best_swr: float | None
    best_error_ohm: float | None
    evaluations: tuple[SynthesisEvaluation, ...]
    message: str = ""


SynthesisEvaluator = Callable[[Mapping[str, float]], SynthesisEvaluation]
CancelCheck = Callable[[], bool]


def _grid_values(variable: SynthesisVariable, count: int) -> tuple[float, ...]:
    if count == 1:
        return ((variable.minimum + variable.maximum) / 2.0,)
    step = (variable.maximum - variable.minimum) / (count - 1)
    return tuple(variable.minimum + index * step for index in range(count))


def _score(impedance: complex | None, target: SynthesisTarget) -> float | None:
    if impedance is None:
        return None
    return abs(impedance - target.impedance_ohm)


def rank_evaluations(
    evaluations: Sequence[SynthesisEvaluation],
    target: SynthesisTarget,
) -> tuple[SynthesisEvaluation, ...]:
    """Return evaluations ordered by complex impedance error."""

    def key(evaluation: SynthesisEvaluation) -> tuple[int, float, int]:
        if evaluation.impedance_ohm is None:
            return (1, math.inf, evaluation.index)
        return (
            0,
            abs(evaluation.impedance_ohm - target.impedance_ohm),
            evaluation.index,
        )

    return tuple(sorted(evaluations, key=key))


def synthesize_grid(
    evaluate: SynthesisEvaluator,
    variables: tuple[SynthesisVariable, ...],
    target: SynthesisTarget,
    *,
    max_evaluations: int = 81,
    cancel_check: CancelCheck | None = None,
) -> SynthesisResult:
    if not variables:
        raise ValueError("at least one synthesis variable is required")
    if max_evaluations < 1:
        raise ValueError("max_evaluations must be positive")
    side = max(2, int(max_evaluations ** (1.0 / len(variables))))
    grids = tuple(_grid_values(variable, side) for variable in variables)
    evaluations: list[SynthesisEvaluation] = []

    def combinations(index: int, values: dict[str, float]) -> tuple[dict[str, float], ...]:
        if index == len(variables):
            return (dict(values),)
        result: list[dict[str, float]] = []
        for value in grids[index]:
            values[variables[index].name] = value
            result.extend(combinations(index + 1, values))
        return tuple(result)

    best: tuple[dict[str, float], SynthesisEvaluation, float] | None = None
    for values in combinations(0, {}):
        if cancel_check is not None and cancel_check():
            return SynthesisResult(
                status=SynthesisStatus.CANCELLED,
                best_values=None,
                best_impedance_ohm=None,
                best_swr=None,
                best_error_ohm=None,
                evaluations=tuple(evaluations),
                message="synthesis cancelled",
            )
        raw = evaluate(values)
        evaluation = SynthesisEvaluation(
            index=len(evaluations) + 1,
            values=values,
            impedance_ohm=raw.impedance_ohm,
            swr=raw.swr,
            error=raw.error,
            cancelled=raw.cancelled,
        )
        evaluations.append(evaluation)
        if evaluation.cancelled:
            return SynthesisResult(
                status=SynthesisStatus.CANCELLED,
                best_values=None,
                best_impedance_ohm=None,
                best_swr=None,
                best_error_ohm=None,
                evaluations=tuple(evaluations),
                message="synthesis cancelled",
            )
        score = _score(evaluation.impedance_ohm, target)
        if score is not None and (best is None or score < best[2]):
            best = (dict(values), evaluation, score)
    if best is None:
        return SynthesisResult(
            status=SynthesisStatus.ERROR,
            best_values=None,
            best_impedance_ohm=None,
            best_swr=None,
            best_error_ohm=None,
            evaluations=tuple(evaluations),
            message="no valid synthesis evaluation",
        )
    values, evaluation, error = best
    return SynthesisResult(
        status=SynthesisStatus.CONVERGED,
        best_values=values,
        best_impedance_ohm=evaluation.impedance_ohm,
        best_swr=evaluation.swr,
        best_error_ohm=error,
        evaluations=tuple(evaluations),
        message="grid search completed",
    )
