# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic hybrid optimizer: differential evolution plus local search."""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum

from .variables import OptimizationVariable, VariableKind

OptimizerEvaluator = Callable[[Mapping[str, float]], "CandidateEvaluation"]
OptimizerBatchEvaluator = Callable[
    [Sequence[Mapping[str, float]]],
    Sequence["CandidateEvaluation"],
]
OptimizerCancelCheck = Callable[[], bool]
OptimizerProgress = Callable[[int, float | None], None]


class BudgetProfile(StrEnum):
    FAST = "fast"
    BALANCED = "balanced"
    THOROUGH = "thorough"


class OptimizationStatus(StrEnum):
    CONVERGED = "converged"
    MAX_EVALUATIONS = "max_evaluations"
    NO_FEASIBLE = "no_feasible"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class OptimizationBudget:
    global_evaluations: int
    local_evaluations: int
    patience: int = 10

    def __post_init__(self) -> None:
        if self.global_evaluations < 4:
            raise ValueError("global_evaluations must be at least 4")
        if self.local_evaluations < 4:
            raise ValueError("local_evaluations must be at least 4")
        if self.patience < 2:
            raise ValueError("patience must be at least 2")

    @property
    def total(self) -> int:
        return self.global_evaluations + self.local_evaluations


def budget_for(profile: BudgetProfile, variable_count: int) -> OptimizationBudget:
    """Return the agreed evaluation budget for a profile."""

    if variable_count < 1:
        raise ValueError("variable_count must be positive")
    if profile is BudgetProfile.FAST:
        global_count = max(60, 12 * variable_count)
        local_count = max(40, 8 * variable_count)
    elif profile is BudgetProfile.THOROUGH:
        global_count = max(1_500, 200 * variable_count)
        local_count = max(1_000, 100 * variable_count)
    else:
        global_count = max(120, 30 * variable_count)
        local_count = max(80, 20 * variable_count)
    return OptimizationBudget(
        global_evaluations=global_count,
        local_evaluations=local_count,
        patience=max(8, round(0.2 * global_count / max(8, 4 * variable_count))),
    )


@dataclass(frozen=True, slots=True)
class CandidateEvaluation:
    index: int
    values: Mapping[str, float]
    score: float | None
    feasible: bool
    violation: float = 0.0
    metrics: Mapping[str, float] = field(default_factory=dict)
    error: str | None = None
    cancelled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "metrics", dict(self.metrics))


@dataclass(frozen=True, slots=True)
class SensitivityPoint:
    name: str
    low_value: float | None
    high_value: float | None
    low_score: float | None
    high_score: float | None
    delta: float | None


@dataclass(frozen=True, slots=True)
class OptimizerRunResult:
    status: OptimizationStatus
    best_values: Mapping[str, float] | None
    best_score: float | None
    best_metrics: Mapping[str, float]
    evaluations: tuple[CandidateEvaluation, ...]
    seed: int
    message: str = ""
    sensitivity: tuple[SensitivityPoint, ...] = ()


def _rank_key(evaluation: CandidateEvaluation) -> tuple[int, float, float, int]:
    score = evaluation.score if evaluation.score is not None else math.inf
    if evaluation.feasible:
        return (0, score, 0.0, evaluation.index)
    return (1, evaluation.violation, score, evaluation.index)


def rank_evaluations(
    evaluations: Sequence[CandidateEvaluation],
) -> tuple[CandidateEvaluation, ...]:
    return tuple(sorted(evaluations, key=_rank_key))


def _vector(
    values: Mapping[str, float], variables: Sequence[OptimizationVariable]
) -> tuple[float, ...]:
    return tuple(variable.to_fraction(values[variable.name]) for variable in variables)


def _values(
    vector: Sequence[float],
    variables: Sequence[OptimizationVariable],
) -> dict[str, float]:
    return {
        variable.name: variable.from_fraction(fraction)
        for variable, fraction in zip(variables, vector, strict=True)
    }


def _clip_fraction(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def _better(first: CandidateEvaluation, second: CandidateEvaluation) -> bool:
    return _rank_key(first) < _rank_key(second)


def optimize_design(
    variables: Sequence[OptimizationVariable],
    initial_values: Mapping[str, float],
    evaluate: OptimizerEvaluator,
    *,
    budget: OptimizationBudget,
    seed: int = 0,
    start_points: Sequence[Mapping[str, float]] = (),
    cancel_check: OptimizerCancelCheck | None = None,
    progress: OptimizerProgress | None = None,
    batch_evaluate: OptimizerBatchEvaluator | None = None,
) -> OptimizerRunResult:
    """Optimize all active variables jointly.

    The caller is responsible for filtering locked variables and for including
    every active variable in ``initial_values``. Inactive variables must be
    preserved by the family parameter builder.

    ``batch_evaluate`` is an optional optimization for independent candidate
    vectors. Results are collected and recorded in submission order, so a
    deterministic batch evaluator yields the same search order regardless of
    worker scheduling. When it is absent, every evaluation runs through
    ``evaluate`` sequentially.
    """

    if not variables:
        raise ValueError("at least one optimization variable is required")
    names = [variable.name for variable in variables]
    if len(names) != len(set(names)):
        raise ValueError("optimization variable names must be unique")
    for variable in variables:
        if variable.name not in initial_values:
            raise ValueError(f"missing initial value for {variable.name!r}")
        variable.clamp(initial_values[variable.name])

    rng = random.Random(seed)  # noqa: S311 — deterministic search, not cryptography
    evaluations: list[CandidateEvaluation] = []
    cache: dict[tuple[float, ...], CandidateEvaluation] = {}
    cancelled = False
    last_improvement = 0
    best: CandidateEvaluation | None = None

    def is_cancelled() -> bool:
        return bool(cancel_check is not None and cancel_check())

    def evaluate_values(
        values: Mapping[str, float],
    ) -> CandidateEvaluation | None:
        nonlocal cancelled
        if is_cancelled():
            cancelled = True
            return None
        key = tuple(round(float(values[name]), 9) for name in names)
        if key in cache:
            return cache[key]
        raw = evaluate(dict(values))
        evaluation = CandidateEvaluation(
            index=len(evaluations) + 1,
            values=dict(values),
            score=raw.score,
            feasible=raw.feasible,
            violation=raw.violation,
            metrics=dict(raw.metrics),
            error=raw.error,
            cancelled=raw.cancelled,
        )
        evaluations.append(evaluation)
        cache[key] = evaluation
        if evaluation.cancelled:
            cancelled = True
        if progress is not None and not cancelled:
            progress(len(evaluations), evaluation.score if evaluation.feasible else None)
        return evaluation

    def evaluate_batch(
        vectors: Sequence[Mapping[str, float]],
    ) -> list[CandidateEvaluation | None]:
        nonlocal cancelled
        results: list[CandidateEvaluation | None] = [None] * len(vectors)
        if not vectors:
            return results
        if is_cancelled():
            cancelled = True
            return results

        keys = [tuple(round(float(vector[name]), 9) for name in names) for vector in vectors]
        unique_vectors: list[Mapping[str, float]] = []
        unique_positions: list[int] = []
        seen: set[tuple[float, ...]] = set()
        for position, key in enumerate(keys):
            if key in cache:
                results[position] = cache[key]
                continue
            if key in seen:
                continue
            seen.add(key)
            unique_positions.append(position)
            unique_vectors.append(vectors[position])

        if not unique_vectors:
            return results

        if batch_evaluate is not None and len(unique_vectors) > 1:
            try:
                raw_results = list(batch_evaluate([dict(vector) for vector in unique_vectors]))
            except Exception:
                raw_results = [evaluate(dict(vector)) for vector in unique_vectors]
            if len(raw_results) != len(unique_vectors):
                raw_results = [evaluate(dict(vector)) for vector in unique_vectors]
        else:
            raw_results = [evaluate(dict(vector)) for vector in unique_vectors]

        for position, vector, raw in zip(
            unique_positions,
            unique_vectors,
            raw_results,
            strict=True,
        ):
            evaluation = CandidateEvaluation(
                index=len(evaluations) + 1,
                values=dict(vector),
                score=raw.score,
                feasible=raw.feasible,
                violation=raw.violation,
                metrics=dict(raw.metrics),
                error=raw.error,
                cancelled=raw.cancelled,
            )
            evaluations.append(evaluation)
            cache[keys[position]] = evaluation
            results[position] = evaluation
            if evaluation.cancelled:
                cancelled = True
            if progress is not None and not cancelled:
                progress(len(evaluations), evaluation.score if evaluation.feasible else None)

        for position, key in enumerate(keys):
            if results[position] is None and key in cache:
                results[position] = cache[key]
        return results

    def update_best(evaluation: CandidateEvaluation) -> None:
        nonlocal best, last_improvement
        if best is None or _better(evaluation, best):
            best = evaluation
            last_improvement = len(evaluations)

    def initial_vector(values: Mapping[str, float]) -> tuple[float, ...]:
        return tuple(
            variable.to_fraction(values.get(variable.name, initial_values[variable.name]))
            for variable in variables
        )

    # The current design is always the first candidate.
    current_vector = initial_vector(initial_values)
    current = evaluate_values(_values(current_vector, variables))
    if current is None:
        return _result(
            OptimizationStatus.CANCELLED,
            None,
            evaluations,
            seed,
            "optimization cancelled",
        )
    update_best(current)

    population: list[tuple[tuple[float, ...], CandidateEvaluation]] = [(current_vector, current)]
    population_size = min(
        max(8, 4 * len(variables)),
        40,
        max(4, budget.global_evaluations),
    )
    start_vectors = [initial_vector(point) for point in start_points]
    if batch_evaluate is not None:
        initial_vectors = start_vectors[: population_size - 1]
        while (
            len(initial_vectors) < population_size - 1
            and len(evaluations) + len(initial_vectors) < budget.global_evaluations
        ):
            initial_vectors.append(tuple(rng.random() for _ in variables))
        batch_results = evaluate_batch([_values(vector, variables) for vector in initial_vectors])
        for vector, evaluation in zip(initial_vectors, batch_results, strict=True):
            if evaluation is None:
                break
            update_best(evaluation)
            population.append((vector, evaluation))
    else:
        for vector in start_vectors:
            if len(population) >= population_size:
                break
            evaluation = evaluate_values(_values(vector, variables))
            if evaluation is None:
                break
            update_best(evaluation)
            population.append((vector, evaluation))
        while len(population) < population_size and len(evaluations) < budget.global_evaluations:
            vector = tuple(rng.random() for _ in variables)
            evaluation = evaluate_values(_values(vector, variables))
            if evaluation is None:
                break
            update_best(evaluation)
            population.append((vector, evaluation))

    if cancelled:
        return _result(
            OptimizationStatus.CANCELLED,
            best,
            evaluations,
            seed,
            "optimization cancelled",
        )
    if not evaluations:
        return _result(OptimizationStatus.ERROR, None, evaluations, seed, "no evaluation")

    base_total = budget.total
    max_total = 2 * base_total
    global_limit = budget.global_evaluations
    stagnation = 0
    generation = 0

    def trial_vector(index: int) -> tuple[float, ...]:
        choices = list(range(len(population)))
        choices.remove(index)
        r1, r2, r3 = rng.sample(choices, 3)
        first = population[r1][0]
        second = population[r2][0]
        third = population[r3][0]
        mutant = tuple(
            _clip_fraction(first[position] + 0.7 * (second[position] - third[position]))
            for position in range(len(variables))
        )
        return tuple(
            mutant[position] if rng.random() < 0.9 else population[index][0][position]
            for position in range(len(variables))
        )

    while len(evaluations) < global_limit and not cancelled:
        generation += 1
        improved_generation = False
        if batch_evaluate is not None:
            trial_vectors: list[tuple[float, ...]] = []
            trial_indices: list[int] = []
            for index in range(len(population)):
                if len(evaluations) + len(trial_vectors) >= global_limit or cancelled:
                    break
                trial = trial_vector(index)
                if trial == population[index][0]:
                    continue
                trial_indices.append(index)
                trial_vectors.append(trial)
            batch_results = evaluate_batch([_values(vector, variables) for vector in trial_vectors])
            for index, trial, evaluation in zip(
                trial_indices,
                trial_vectors,
                batch_results,
                strict=True,
            ):
                if evaluation is None:
                    break
                if _better(evaluation, population[index][1]):
                    population[index] = (trial, evaluation)
                    improved_generation = True
                    update_best(evaluation)
        else:
            for index in range(len(population)):
                if len(evaluations) >= global_limit or cancelled:
                    break
                trial = trial_vector(index)
                if trial == population[index][0]:
                    continue
                evaluation = evaluate_values(_values(trial, variables))
                if evaluation is None:
                    break
                if _better(evaluation, population[index][1]):
                    population[index] = (trial, evaluation)
                    improved_generation = True
                    update_best(evaluation)
        if improved_generation:
            stagnation = 0
        else:
            stagnation += 1
        if stagnation >= budget.patience:
            break
        if len(evaluations) >= global_limit:
            recent = max(global_limit - max(8, global_limit // 5), 0)
            if last_improvement >= recent and global_limit < max_total - budget.local_evaluations:
                global_limit = min(
                    max_total - budget.local_evaluations,
                    global_limit + max(1, base_total // 4),
                )
                stagnation = 0
                continue
            break

    if is_cancelled():
        return _result(
            OptimizationStatus.CANCELLED,
            best,
            evaluations,
            seed,
            "optimization cancelled",
        )

    best = _local_search(
        variables,
        best or rank_evaluations(evaluations)[0],
        evaluate_values,
        budget.local_evaluations,
        cancel_check=is_cancelled,
    )
    if is_cancelled():
        return _result(
            OptimizationStatus.CANCELLED,
            best,
            evaluations,
            seed,
            "optimization cancelled",
        )

    feasible = [
        evaluation
        for evaluation in evaluations
        if evaluation.feasible and evaluation.score is not None
    ]
    if not feasible:
        return _result(
            OptimizationStatus.NO_FEASIBLE,
            None,
            evaluations,
            seed,
            "no feasible design found",
        )

    sensitivity = _sensitivity(
        variables,
        best,
        evaluate_values,
        cancel_check=is_cancelled,
    )
    status = (
        OptimizationStatus.MAX_EVALUATIONS
        if len(evaluations) >= global_limit + budget.local_evaluations
        else OptimizationStatus.CONVERGED
    )
    return _result(status, best, evaluations, seed, "optimization completed", sensitivity)


def _local_search(
    variables: Sequence[OptimizationVariable],
    start: CandidateEvaluation,
    evaluate_values: Callable[[Mapping[str, float]], CandidateEvaluation | None],
    budget: int,
    *,
    cancel_check: OptimizerCancelCheck,
) -> CandidateEvaluation:
    current = start
    step = 0.1
    spent = 0
    while spent < budget and step >= 1e-4:
        if cancel_check():
            return current
        improved = False
        for variable in variables:
            if spent >= budget:
                break
            direction = -1
            while direction <= 1:
                candidate = dict(current.values)
                if variable.kind is VariableKind.CONTINUOUS:
                    candidate[variable.name] = variable.clamp(
                        current.values[variable.name]
                        + direction * step * (variable.maximum - variable.minimum)
                    )
                else:
                    candidate[variable.name] = variable.next_value(
                        current.values[variable.name],
                        direction,
                    )
                if candidate[variable.name] == current.values[variable.name]:
                    direction += 2
                    continue
                evaluation = evaluate_values(candidate)
                if evaluation is None:
                    return current
                spent += 1
                if _better(evaluation, current):
                    current = evaluation
                    improved = True
                direction += 2
        if not improved:
            step *= 0.5
    return current


def _sensitivity(
    variables: Sequence[OptimizationVariable],
    best: CandidateEvaluation,
    evaluate_values: Callable[[Mapping[str, float]], CandidateEvaluation | None],
    *,
    cancel_check: OptimizerCancelCheck,
) -> tuple[SensitivityPoint, ...]:
    points: list[SensitivityPoint] = []
    for variable in variables:
        if cancel_check():
            break
        low_value: float | None = None
        high_value: float | None = None
        low_score: float | None = None
        high_score: float | None = None
        for direction, setter in ((-1, "low"), (1, "high")):
            candidate = dict(best.values)
            if variable.kind is VariableKind.CONTINUOUS:
                candidate[variable.name] = variable.clamp(
                    best.values[variable.name]
                    + direction * max(0.02, variable.step) * (variable.maximum - variable.minimum)
                )
            else:
                candidate[variable.name] = variable.next_value(
                    best.values[variable.name],
                    direction,
                )
            if candidate[variable.name] == best.values[variable.name]:
                continue
            evaluation = evaluate_values(candidate)
            if evaluation is None:
                break
            if setter == "low":
                low_value = candidate[variable.name]
                low_score = evaluation.score if evaluation.feasible else None
            else:
                high_value = candidate[variable.name]
                high_score = evaluation.score if evaluation.feasible else None
        delta = None
        if low_score is not None and high_score is not None:
            delta = abs(high_score - low_score)
        points.append(
            SensitivityPoint(
                name=variable.name,
                low_value=low_value,
                high_value=high_value,
                low_score=low_score,
                high_score=high_score,
                delta=delta,
            )
        )
    return tuple(points)


def _result(
    status: OptimizationStatus,
    best: CandidateEvaluation | None,
    evaluations: Sequence[CandidateEvaluation],
    seed: int,
    message: str,
    sensitivity: tuple[SensitivityPoint, ...] = (),
) -> OptimizerRunResult:
    return OptimizerRunResult(
        status=status,
        best_values=None if best is None or not best.feasible else dict(best.values),
        best_score=None if best is None or not best.feasible else best.score,
        best_metrics={} if best is None else dict(best.metrics),
        evaluations=tuple(evaluations),
        seed=seed,
        message=message,
        sensitivity=sensitivity,
    )
