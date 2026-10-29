# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded one-dimensional dipole length optimization."""

from __future__ import annotations

import itertools
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from enum import StrEnum

from ..common.units import ensure_finite, ensure_positive


class OptimizationObjective(StrEnum):
    REACTANCE = "reactance"
    MIN_SWR = "min_swr"
    MAX_BANDWIDTH = "max_bandwidth"


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
    objective: OptimizationObjective = OptimizationObjective.REACTANCE
    target_reactance_ohm: float = 0.0
    max_evaluations: int = 12
    reactance_tolerance_ohm: float = 0.1
    swr_tolerance: float = 0.05
    swr_limit: float = 2.0
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
        ensure_positive(self.swr_tolerance, name="swr_tolerance")
        if self.swr_limit <= 1.0:
            raise ValueError("swr_limit must be greater than 1")
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
    bandwidth_hz: float | None = None

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
    bandwidth_hz: float | None = None


@dataclass(frozen=True, slots=True)
class LengthOptimizationResult:
    status: LengthOptimizationStatus
    best_length_m: float | None
    best_impedance_ohm: complex | None
    best_swr: float | None
    evaluations: tuple[LengthEvaluation, ...]
    best_bandwidth_hz: float | None = None
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
    if spec.objective is OptimizationObjective.MIN_SWR:
        return optimize_swr(evaluate, spec, cancel_check=cancel_check)
    if spec.objective is OptimizationObjective.MAX_BANDWIDTH:
        return optimize_bandwidth(evaluate, spec, cancel_check=cancel_check)
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
            best_bandwidth_hz=None if best is None else best.bandwidth_hz,
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


def _best_swr_evaluation(evaluations: list[LengthEvaluation]) -> LengthEvaluation | None:
    valid = [
        evaluation
        for evaluation in evaluations
        if evaluation.impedance_ohm is not None
        and evaluation.swr is not None
        and math.isfinite(evaluation.swr)
    ]
    if not valid:
        return None
    return min(valid, key=lambda evaluation: (evaluation.swr or math.inf, evaluation.length_m))


def optimize_swr(
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
        best = _best_swr_evaluation(evaluations)
        return LengthOptimizationResult(
            status=status,
            best_length_m=None if best is None else best.length_m,
            best_impedance_ohm=None if best is None else best.impedance_ohm,
            best_swr=None if best is None else best.swr,
            evaluations=tuple(evaluations),
            best_bandwidth_hz=None if best is None else best.bandwidth_hz,
            message=message,
        )

    if cancelled():
        return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")

    coarse_count = min(7, max(3, spec.max_evaluations))
    coarse_points = [
        spec.min_length_m + (spec.max_length_m - spec.min_length_m) * index / (coarse_count - 1)
        for index in range(coarse_count)
    ]
    for length in coarse_points:
        if len(evaluations) >= spec.max_evaluations or cancelled():
            break
        evaluation = probe(length)
        if evaluation.cancelled:
            return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")
        if evaluation.impedance_ohm is None or evaluation.swr is None:
            return finish(
                LengthOptimizationStatus.ERROR,
                evaluation.error or "solver evaluation failed",
            )

    ordered = sorted(evaluations, key=lambda evaluation: evaluation.length_m)
    best = _best_swr_evaluation(ordered)
    if best is None:
        return finish(LengthOptimizationStatus.ERROR, "no valid SWR evaluation")
    if best.swr is not None and best.swr <= 1.0 + spec.swr_tolerance:
        return finish(LengthOptimizationStatus.CONVERGED, "SWR target reached")

    best_index = ordered.index(best)
    if best_index == 0 or best_index == len(ordered) - 1:
        return finish(
            LengthOptimizationStatus.CONVERGED,
            "best SWR is at a dimension bound",
        )

    left = ordered[best_index - 1].length_m
    right = ordered[best_index + 1].length_m
    if len(evaluations) >= spec.max_evaluations:
        return finish(
            LengthOptimizationStatus.MAX_EVALUATIONS,
            "maximum number of evaluations reached",
        )
    while len(evaluations) < spec.max_evaluations and right - left > spec.length_tolerance_m:
        if cancelled():
            return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")
        first = left + (right - left) / 3.0
        second = right - (right - left) / 3.0
        first_evaluation = probe(first)
        if first_evaluation.cancelled:
            return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")
        if len(evaluations) >= spec.max_evaluations:
            break
        second_evaluation = probe(second)
        if second_evaluation.cancelled:
            return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")
        if first_evaluation.swr is None or second_evaluation.swr is None:
            return finish(
                LengthOptimizationStatus.ERROR,
                first_evaluation.error or second_evaluation.error or "solver evaluation failed",
            )
        if first_evaluation.swr <= second_evaluation.swr:
            right = second
        else:
            left = first

    final = _best_swr_evaluation(evaluations)
    if final is None:
        return finish(LengthOptimizationStatus.ERROR, "no valid SWR evaluation")
    if final.swr is not None and final.swr <= 1.0 + spec.swr_tolerance:
        return finish(LengthOptimizationStatus.CONVERGED, "SWR target reached")
    if len(evaluations) >= spec.max_evaluations and right - left > spec.length_tolerance_m:
        return finish(
            LengthOptimizationStatus.MAX_EVALUATIONS,
            "maximum number of evaluations reached",
        )
    return finish(LengthOptimizationStatus.CONVERGED, "length tolerance reached")


def measure_bandwidth_hz(
    frequencies_hz: Sequence[float],
    swr_values: Sequence[float],
    *,
    center_hz: float,
    swr_limit: float,
) -> float:
    """Return the contiguous SWR-limited bandwidth around a center frequency."""

    if len(frequencies_hz) != len(swr_values) or not frequencies_hz:
        return 0.0
    ordered = sorted(zip(frequencies_hz, swr_values, strict=True))
    passing = [
        index for index, (_, swr) in enumerate(ordered) if math.isfinite(swr) and swr <= swr_limit
    ]
    if not passing:
        return 0.0
    center_index = min(
        range(len(ordered)),
        key=lambda index: abs(ordered[index][0] - center_hz),
    )
    if center_index not in passing:
        return 0.0
    first = center_index
    while first - 1 in passing:
        first -= 1
    last = center_index
    while last + 1 in passing:
        last += 1

    def boundary(pass_index: int, fail_index: int) -> float:
        pass_frequency, pass_swr = ordered[pass_index]
        fail_frequency, fail_swr = ordered[fail_index]
        if not math.isfinite(fail_swr) or math.isclose(pass_swr, fail_swr):
            return pass_frequency
        ratio = (swr_limit - pass_swr) / (fail_swr - pass_swr)
        return pass_frequency + (fail_frequency - pass_frequency) * min(max(ratio, 0.0), 1.0)

    lower = ordered[first][0] if first == 0 else boundary(first, first - 1)
    upper = ordered[last][0] if last == len(ordered) - 1 else boundary(last, last + 1)
    return max(upper - lower, 0.0)


def _best_bandwidth_evaluation(
    evaluations: list[LengthEvaluation],
) -> LengthEvaluation | None:
    valid = [
        evaluation
        for evaluation in evaluations
        if evaluation.impedance_ohm is not None
        and evaluation.bandwidth_hz is not None
        and math.isfinite(evaluation.bandwidth_hz)
    ]
    if not valid:
        return None
    return max(valid, key=lambda evaluation: (evaluation.bandwidth_hz or 0.0, -evaluation.length_m))


def optimize_bandwidth(
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
        best = _best_bandwidth_evaluation(evaluations)
        return LengthOptimizationResult(
            status=status,
            best_length_m=None if best is None else best.length_m,
            best_impedance_ohm=None if best is None else best.impedance_ohm,
            best_swr=None if best is None else best.swr,
            evaluations=tuple(evaluations),
            best_bandwidth_hz=None if best is None else best.bandwidth_hz,
            message=message,
        )

    if cancelled():
        return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")

    count = spec.max_evaluations
    for index in range(count):
        if cancelled():
            return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")
        ratio = index / (count - 1)
        length = spec.min_length_m + (spec.max_length_m - spec.min_length_m) * ratio
        evaluation = probe(length)
        if evaluation.cancelled:
            return finish(LengthOptimizationStatus.CANCELLED, "optimization cancelled")
        if evaluation.impedance_ohm is None or evaluation.bandwidth_hz is None:
            return finish(
                LengthOptimizationStatus.ERROR,
                evaluation.error or "solver evaluation failed",
            )

    best = _best_bandwidth_evaluation(evaluations)
    if best is None:
        return finish(LengthOptimizationStatus.ERROR, "no valid bandwidth evaluation")
    if (best.bandwidth_hz or 0.0) <= 0.0:
        return finish(
            LengthOptimizationStatus.NO_BRACKET,
            "SWR limit is not met anywhere in the sweep",
        )
    return finish(LengthOptimizationStatus.CONVERGED, "grid search completed")
