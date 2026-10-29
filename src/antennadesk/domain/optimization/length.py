# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded one-dimensional dipole length optimization."""

from __future__ import annotations

import itertools
import math
from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import StrEnum

from ..common.units import ensure_finite, ensure_positive


class LengthOptimizationStatus(StrEnum):
    CONVERGED = "converged"
    MAX_EVALUATIONS = "max_evaluations"
    NO_BRACKET = "no_bracket"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class LengthOptimizationSpec:
    min_length_m: float
    max_length_m: float
    target_reactance_ohm: float = 0.0
    max_evaluations: int = 12
    reactance_tolerance_ohm: float = 0.1
    length_tolerance_m: float = 0.001
    sensitivity_offsets_m: tuple[float, ...] = (0.01, 0.025)

    def __post_init__(self) -> None:
        ensure_positive(self.min_length_m, name="min_length_m")
        ensure_positive(self.max_length_m, name="max_length_m")
        if self.max_length_m <= self.min_length_m:
            raise ValueError("max_length_m must be greater than min_length_m")
        ensure_finite(self.target_reactance_ohm, name="target_reactance_ohm")
        if self.max_evaluations < 3:
            raise ValueError("max_evaluations must be at least 3")
        ensure_positive(self.reactance_tolerance_ohm, name="reactance_tolerance_ohm")
        ensure_positive(self.length_tolerance_m, name="length_tolerance_m")
        for offset in self.sensitivity_offsets_m:
            ensure_positive(offset, name="sensitivity offset")


@dataclass(frozen=True, slots=True)
class LengthEvaluation:
    length_m: float
    impedance_ohm: complex | None
    swr: float | None = None
    error: str | None = None
    cancelled: bool = False
    index: int = 0

    @property
    def reactance_ohm(self) -> float | None:
        return None if self.impedance_ohm is None else self.impedance_ohm.imag


@dataclass(frozen=True, slots=True)
class LengthSensitivityPoint:
    length_m: float
    offset_m: float
    impedance_ohm: complex | None
    swr: float | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class LengthOptimizationResult:
    status: LengthOptimizationStatus
    best_length_m: float | None
    best_impedance_ohm: complex | None
    best_swr: float | None
    evaluations: tuple[LengthEvaluation, ...]
    sensitivity: tuple[LengthSensitivityPoint, ...] = ()
    message: str = ""


LengthEvaluator = Callable[[float], LengthEvaluation]
CancelCheck = Callable[[], bool]


def _best_evaluation(
    evaluations: list[LengthEvaluation],
    target_reactance_ohm: float,
) -> LengthEvaluation | None:
    valid = [evaluation for evaluation in evaluations if evaluation.impedance_ohm is not None]
    if not valid:
        return None

    def distance(evaluation: LengthEvaluation) -> float:
        assert evaluation.impedance_ohm is not None
        return abs(evaluation.impedance_ohm.imag - target_reactance_ohm)

    return min(valid, key=distance)


def optimize_length(
    evaluate: LengthEvaluator,
    spec: LengthOptimizationSpec,
    *,
    cancel_check: CancelCheck | None = None,
) -> LengthOptimizationResult:
    evaluations: list[LengthEvaluation] = []

    def cancelled() -> bool:
        return bool(cancel_check is not None and cancel_check())

    def probe(length: float) -> LengthEvaluation:
        raw = evaluate(length)
        evaluation = replace(raw, index=len(evaluations) + 1)
        evaluations.append(evaluation)
        return evaluation

    def finish(status: LengthOptimizationStatus, message: str = "") -> LengthOptimizationResult:
        best = _best_evaluation(evaluations, spec.target_reactance_ohm)
        return LengthOptimizationResult(
            status=status,
            best_length_m=None if best is None else best.length_m,
            best_impedance_ohm=None if best is None else best.impedance_ohm,
            best_swr=None if best is None else best.swr,
            evaluations=tuple(evaluations),
            message=message,
        )

    if cancelled():
        return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")

    low = probe(spec.min_length_m)
    if cancelled() or low.cancelled:
        return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")
    high = probe(spec.max_length_m)
    if high.cancelled:
        return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")

    if low.impedance_ohm is None or high.impedance_ohm is None:
        return finish(
            LengthOptimizationStatus.ERROR,
            low.error or high.error or "solver evaluation failed",
        )

    target = spec.target_reactance_ohm
    if abs(low.impedance_ohm.imag - target) <= spec.reactance_tolerance_ohm:
        return finish(LengthOptimizationStatus.CONVERGED, "lower bound is at the target")
    if abs(high.impedance_ohm.imag - target) <= spec.reactance_tolerance_ohm:
        return finish(LengthOptimizationStatus.CONVERGED, "upper bound is at the target")

    def has_bracket(first: LengthEvaluation, second: LengthEvaluation) -> bool:
        if first.impedance_ohm is None or second.impedance_ohm is None:
            return False
        first_value = first.impedance_ohm.imag - target
        second_value = second.impedance_ohm.imag - target
        return first_value * second_value <= 0.0

    if not has_bracket(low, high):
        # A coarse scan can still find a resonance when the endpoints are on the
        # same side of the target (for example, a non-monotonic reactance).
        for ratio in (0.25, 0.5, 0.75):
            if len(evaluations) >= spec.max_evaluations or cancelled():
                break
            length = spec.min_length_m + (spec.max_length_m - spec.min_length_m) * ratio
            evaluation = probe(length)
            if evaluation.cancelled:
                return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")
        ordered = sorted(evaluations, key=lambda evaluation: evaluation.length_m)
        bracket: tuple[LengthEvaluation, LengthEvaluation] | None = None
        for first, second in itertools.pairwise(ordered):
            if has_bracket(first, second):
                bracket = (first, second)
                break
        if bracket is None:
            return finish(
                LengthOptimizationStatus.NO_BRACKET,
                "target reactance is not bracketed within the length limits",
            )
        low, high = bracket

    if low.length_m > high.length_m:
        low, high = high, low

    while len(evaluations) < spec.max_evaluations:
        if cancelled():
            return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")
        assert low.impedance_ohm is not None
        assert high.impedance_ohm is not None
        low_value = low.impedance_ohm.imag - target
        high_value = high.impedance_ohm.imag - target
        denominator = high_value - low_value
        if denominator == 0.0:
            length = (low.length_m + high.length_m) / 2.0
        else:
            length = low.length_m - low_value * (high.length_m - low.length_m) / denominator
        margin = max(spec.length_tolerance_m * 0.5, 1e-9)
        if not math.isfinite(length):
            length = (low.length_m + high.length_m) / 2.0
        length = min(max(length, low.length_m + margin), high.length_m - margin)

        evaluation = probe(length)
        if evaluation.impedance_ohm is None:
            return finish(
                LengthOptimizationStatus.ERROR,
                evaluation.error or "solver evaluation failed",
            )
        value = evaluation.impedance_ohm.imag - target
        if abs(value) <= spec.reactance_tolerance_ohm:
            return finish(LengthOptimizationStatus.CONVERGED, "reactance target reached")

        if value * low_value <= 0.0:
            high = evaluation
        else:
            low = evaluation

        if high.length_m - low.length_m <= spec.length_tolerance_m:
            return finish(
                LengthOptimizationStatus.CONVERGED,
                "length tolerance reached",
            )

    return finish(
        LengthOptimizationStatus.MAX_EVALUATIONS,
        "maximum number of evaluations reached",
    )
