# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Family-driven antenna optimization through the solver port."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, replace

from ...domain.antennas.antenna import AntennaModel
from ...domain.antennas.design import AntennaDesignParameters
from ...domain.antennas.footprint import boom_length_m, turning_radius_m
from ...domain.common.time import utc_now
from ...domain.common.validation import Severity
from ...domain.optimization.constraints import OptimizationMetric, SoftConstraint
from ...domain.optimization.descriptor import (
    AntennaOptimizerDescriptor,
    FamilyOptimizationObjective,
    OptimizationWeights,
)
from ...domain.optimization.engine import (
    BudgetProfile,
    CandidateEvaluation,
    OptimizationBudget,
    OptimizationStatus,
    OptimizerBatchEvaluator,
    OptimizerRunResult,
    SensitivityPoint,
    optimize_design,
)
from ...domain.optimization.length import measure_bandwidth_hz
from ...domain.optimization.pareto import ParetoCandidate, pareto_front
from ...domain.optimization.recommendations import (
    RecommendationContext,
    build_recommendations,
)
from ...domain.optimization.summary import OptimizationMode, OptimizationSummary
from ...domain.optimization.synthesis import swr_for_resistance
from ...domain.optimization.variables import OptimizationVariable, VariableKind
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.pattern import front_to_back_db, max_power_gain_db
from ...domain.simulation.result import SimulationResult, SimulationStatus
from ...domain.simulation.segmentation import SegmentationPolicy, aligned_policy_for_model
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

DEFAULT_BAND_AWARE_SPAN = 0.05
ROBUST_SPREAD_PENALTY = 0.1
ROBUST_DIMENSION_UNITS = frozenset({"m", "radius"})
MAX_SEED_RUNS = 4
SEED_SCORE_RELATIVE_TOLERANCE = 0.02
SEED_SCORE_ABSOLUTE_TOLERANCE = 0.05
SEED_PARAMETER_TOLERANCE = 0.02


@dataclass(frozen=True, slots=True)
class OptimizeAntennaCommand:
    descriptor: AntennaOptimizerDescriptor
    base_spec: SimulationSpec
    objective: FamilyOptimizationObjective
    budget: OptimizationBudget
    weights: OptimizationWeights = field(default_factory=OptimizationWeights)
    target_resistance_ohm: float = 50.0
    target_reactance_ohm: float = 0.0
    soft_constraints: tuple[SoftConstraint, ...] = ()
    locked_variables: frozenset[str] = frozenset()
    seed: int = 0
    seed_runs: int = 1
    parallel_workers: int = 1
    mode: OptimizationMode = OptimizationMode.SINGLE
    band_edges_hz: tuple[float, ...] = ()
    operating_frequencies_hz: tuple[float, ...] = ()
    robust_tolerance: float = 0.0
    max_boom_length_m: float | None = None
    max_turning_radius_m: float | None = None
    budget_profile: BudgetProfile = BudgetProfile.BALANCED
    cancel_token: CancelToken | None = None
    progress: Callable[[int, float | None], None] | None = None

    def __post_init__(self) -> None:
        if self.target_resistance_ohm <= 0.0:
            raise ValueError("target_resistance_ohm must be positive")
        if not math.isfinite(self.target_reactance_ohm):
            raise ValueError("target_reactance_ohm must be finite")
        if not 1 <= self.parallel_workers <= 8:
            raise ValueError("parallel_workers must be between 1 and 8")
        if not 1 <= self.seed_runs <= MAX_SEED_RUNS:
            raise ValueError(f"seed_runs must be between 1 and {MAX_SEED_RUNS}")
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        if self.objective not in self.descriptor.objectives:
            raise ValueError(f"objective {self.objective.value!r} is not supported")
        object.__setattr__(self, "mode", OptimizationMode(self.mode))
        object.__setattr__(self, "band_edges_hz", tuple(self.band_edges_hz))
        for frequency in self.band_edges_hz:
            if not math.isfinite(frequency) or frequency <= 0.0:
                raise ValueError("band edges must be positive and finite")
        object.__setattr__(
            self,
            "operating_frequencies_hz",
            tuple(self.operating_frequencies_hz),
        )
        for frequency in self.operating_frequencies_hz:
            if not math.isfinite(frequency) or frequency <= 0.0:
                raise ValueError("operating frequencies must be positive and finite")
        if (
            self.mode is not OptimizationMode.SINGLE
            and self.band_edges_hz
            and len(set(self.band_edges_hz)) < 2
        ):
            raise ValueError("band-aware modes require at least two distinct edges")
        if not math.isfinite(self.robust_tolerance) or self.robust_tolerance < 0.0:
            raise ValueError("robust_tolerance must be non-negative and finite")
        if self.robust_tolerance >= 1.0:
            raise ValueError("robust_tolerance must be smaller than 1")
        if self.mode is OptimizationMode.ROBUST and self.robust_tolerance == 0.0:
            raise ValueError("robust mode requires a positive tolerance")
        if self.mode is not OptimizationMode.ROBUST and self.robust_tolerance != 0.0:
            raise ValueError("robust_tolerance is only used in robust mode")
        if self.mode is not OptimizationMode.SINGLE and (
            self.objective is FamilyOptimizationObjective.MAX_BANDWIDTH
            or any(
                constraint.metric is OptimizationMetric.BANDWIDTH_HZ
                for constraint in self.soft_constraints
            )
        ):
            raise ValueError("bandwidth optimization requires single-frequency mode")
        for name, value in (
            ("max_boom_length_m", self.max_boom_length_m),
            ("max_turning_radius_m", self.max_turning_radius_m),
        ):
            if value is not None and (not math.isfinite(value) or value <= 0.0):
                raise ValueError(f"{name} must be positive and finite")


@dataclass(frozen=True, slots=True)
class OptimizeAntennaResult:
    status: OptimizationStatus
    best_parameters: AntennaDesignParameters | None
    best_values: Mapping[str, float] | None
    best_score: float | None
    best_metrics: Mapping[str, float]
    evaluations: tuple[CandidateEvaluation, ...]
    sensitivity: tuple[SensitivityPoint, ...]
    budget: OptimizationBudget
    seed: int
    summary: OptimizationSummary | None = None
    pareto: tuple[ParetoCandidate, ...] = ()
    message: str = ""


class _EvaluationCancelled(Exception):
    """Internal control flow for a cancelled solver run."""


class _EvaluationFailure(Exception):
    """Internal control flow for an unusable solver result."""


@dataclass(frozen=True, slots=True)
class _PointOutcome:
    result: SimulationResult | None = None
    error: str | None = None
    cancelled: bool = False


@dataclass(frozen=True, slots=True)
class OptimizeAntenna:
    solver: AntennaSolver

    def execute(self, command: OptimizeAntennaCommand) -> OptimizeAntennaResult:
        descriptor = command.descriptor
        active_variables = tuple(
            variable
            for variable in descriptor.variables
            if variable.name not in command.locked_variables
        )
        if not active_variables:
            raise ValueError("at least one variable must remain unlocked")
        initial_values = {
            variable.name: descriptor.initial_values[variable.name] for variable in active_variables
        }
        start_points = tuple(
            {variable.name: point[variable.name] for variable in active_variables}
            for point in descriptor.start_points
        )
        pattern_metrics = {
            OptimizationMetric.GAIN_DB,
            OptimizationMetric.FRONT_TO_BACK_DB,
        }
        needs_pattern = (
            command.objective
            in {
                FamilyOptimizationObjective.MAX_GAIN,
                FamilyOptimizationObjective.MAX_FRONT_TO_BACK,
            }
            or (
                command.objective is FamilyOptimizationObjective.MULTI_OBJECTIVE
                and (command.weights.gain > 0.0 or command.weights.front_to_back > 0.0)
            )
            or any(constraint.metric in pattern_metrics for constraint in command.soft_constraints)
        )
        needs_sweep = command.objective is FamilyOptimizationObjective.MAX_BANDWIDTH or any(
            constraint.metric is OptimizationMetric.BANDWIDTH_HZ
            for constraint in command.soft_constraints
        )
        if needs_pattern and not command.base_spec.far_field.enabled:
            raise ValueError("this objective or constraint requires a far-field request")
        if needs_sweep and command.base_spec.frequency_plan.count < 2:
            raise ValueError("this objective or constraint requires a frequency sweep")
        band_edges = _resolved_band_edges(command)

        def evaluate(values: Mapping[str, float]) -> CandidateEvaluation:
            full_values = dict(descriptor.initial_values)
            full_values.update(values)
            violations = descriptor.validate(full_values)
            if violations:
                return CandidateEvaluation(
                    index=0,
                    values=full_values,
                    score=None,
                    feasible=False,
                    violation=sum(item.amount for item in violations),
                    error="; ".join(item.message_key for item in violations),
                )
            try:
                parameters = descriptor.build_parameters(full_values)
                if command.mode is OptimizationMode.SINGLE:
                    metrics = _single_metrics(
                        command,
                        self.solver,
                        parameters,
                        needs_pattern=needs_pattern,
                        needs_sweep=needs_sweep,
                    )
                else:
                    metrics = _multi_metrics(
                        command,
                        self.solver,
                        descriptor,
                        full_values,
                        parameters,
                        band_edges,
                        active_variables,
                        needs_pattern=needs_pattern,
                    )
                metrics.update(_space_metrics(parameters, command))
                score = _multi_score(command, metrics)
            except _EvaluationCancelled:
                return CandidateEvaluation(
                    index=0,
                    values=full_values,
                    score=None,
                    feasible=False,
                    cancelled=True,
                    error="cancelled",
                )
            except (_EvaluationFailure, ValueError) as exc:
                return CandidateEvaluation(
                    index=0,
                    values=full_values,
                    score=None,
                    feasible=False,
                    violation=1.0,
                    error=str(exc),
                )
            except Exception as exc:
                return CandidateEvaluation(
                    index=0,
                    values=full_values,
                    score=None,
                    feasible=False,
                    violation=1.0,
                    error=str(exc),
                )
            return CandidateEvaluation(
                index=0,
                values=full_values,
                score=score,
                feasible=True,
                metrics=metrics,
            )

        executor: ThreadPoolExecutor | None = None
        batch_evaluator: OptimizerBatchEvaluator | None = None
        if command.parallel_workers > 1:
            worker_executor = ThreadPoolExecutor(max_workers=command.parallel_workers)
            executor = worker_executor

            def batch_evaluator_fn(
                values: Sequence[Mapping[str, float]],
            ) -> list[CandidateEvaluation]:
                futures = [worker_executor.submit(evaluate, dict(item)) for item in values]
                return [future.result() for future in futures]

            batch_evaluator = batch_evaluator_fn

        seeds = tuple(command.seed + offset for offset in range(command.seed_runs))
        runs: list[OptimizerRunResult] = []
        completed_evaluations = 0
        cancelled = False
        best_score_seen: float | None = None
        progress = command.progress

        def seed_progress(count: int, score: float | None) -> None:
            nonlocal best_score_seen
            if score is not None and (best_score_seen is None or score < best_score_seen):
                best_score_seen = score
            if progress is not None:
                progress(completed_evaluations + count, best_score_seen)

        try:
            for seed in seeds:
                if command.cancel_token is not None and command.cancel_token.is_cancelled():
                    cancelled = True
                    break
                run = optimize_design(
                    active_variables,
                    initial_values,
                    evaluate,
                    budget=command.budget,
                    seed=seed,
                    start_points=start_points,
                    cancel_check=(
                        command.cancel_token.is_cancelled
                        if command.cancel_token is not None
                        else None
                    ),
                    progress=seed_progress,
                    batch_evaluate=batch_evaluator,
                )
                runs.append(run)
                completed_evaluations += len(run.evaluations)
                if run.status is OptimizationStatus.CANCELLED:
                    cancelled = True
                    break
        finally:
            if executor is not None:
                executor.shutdown(wait=True, cancel_futures=True)
        engine_result = _merge_seed_runs(
            command,
            runs,
            active_variables,
            cancelled=cancelled,
        )
        best_parameters: AntennaDesignParameters | None = None
        if engine_result.best_values is not None:
            full_values = dict(descriptor.initial_values)
            full_values.update(engine_result.best_values)
            try:
                best_parameters = descriptor.build_parameters(full_values)
            except Exception:
                best_parameters = None
        summary = _summary_for(command, engine_result, band_edges)
        return OptimizeAntennaResult(
            status=engine_result.status,
            best_parameters=best_parameters,
            best_values=engine_result.best_values,
            best_score=engine_result.best_score,
            best_metrics=engine_result.best_metrics,
            evaluations=engine_result.evaluations,
            sensitivity=engine_result.sensitivity,
            budget=command.budget,
            seed=engine_result.seed,
            summary=summary,
            pareto=pareto_front(engine_result.evaluations),
            message=engine_result.message,
        )


def _merge_seed_runs(
    command: OptimizeAntennaCommand,
    runs: Sequence[OptimizerRunResult],
    active_variables: Sequence[OptimizationVariable],
    *,
    cancelled: bool,
) -> OptimizerRunResult:
    """Choose the best seed run and attach verification metrics."""

    if not runs:
        empty = OptimizerRunResult(
            status=(OptimizationStatus.CANCELLED if cancelled else OptimizationStatus.NO_FEASIBLE),
            best_values=None,
            best_score=None,
            best_metrics={},
            evaluations=(),
            seed=command.seed,
            message="optimization cancelled" if cancelled else "no feasible candidate found",
        )
        if command.seed_runs == 1:
            return empty
        metrics = _seed_verification_metrics(
            command,
            (),
            (),
            empty,
            active_variables,
            cancelled=cancelled,
        )
        return replace(empty, best_metrics=metrics)

    scored = [run for run in runs if run.best_score is not None and math.isfinite(run.best_score)]
    if scored:
        winner = min(
            scored,
            key=lambda run: (
                run.best_score if run.best_score is not None else math.inf,
                run.seed,
            ),
        )
    elif any(run.status is OptimizationStatus.NO_FEASIBLE for run in runs):
        winner = next(run for run in runs if run.status is OptimizationStatus.NO_FEASIBLE)
    else:
        winner = runs[-1]

    if command.seed_runs == 1:
        return winner

    metrics = _seed_verification_metrics(
        command,
        runs,
        scored,
        winner,
        active_variables,
        cancelled=cancelled,
    )
    status = OptimizationStatus.CANCELLED if cancelled else winner.status
    message = "optimization cancelled" if cancelled else winner.message
    return replace(winner, status=status, best_metrics=metrics, message=message)


def _seed_verification_metrics(
    command: OptimizeAntennaCommand,
    runs: Sequence[OptimizerRunResult],
    scored: Sequence[OptimizerRunResult],
    winner: OptimizerRunResult,
    active_variables: Sequence[OptimizationVariable],
    *,
    cancelled: bool,
) -> dict[str, float]:
    metrics = dict(winner.best_metrics)
    metrics["seed_base"] = float(command.seed)
    metrics["seed_requested"] = float(command.seed_runs)
    metrics["seed_count"] = float(len(runs))
    metrics["seed_scored_count"] = float(len(scored))
    metrics["seed_evaluations_total"] = float(sum(len(run.evaluations) for run in runs))
    metrics["seed_score_spread"] = 0.0
    metrics["seed_parameter_spread"] = 0.0
    converged = False
    if len(scored) >= 2 and winner.best_score is not None:
        scores = [run.best_score for run in scored if run.best_score is not None]
        score_spread = max(scores) - min(scores)
        parameter_spread = _seed_parameter_spread(scored, active_variables)
        metrics["seed_score_spread"] = score_spread
        metrics["seed_parameter_spread"] = parameter_spread
        if not cancelled and len(runs) == command.seed_runs and len(scored) == command.seed_runs:
            score_threshold = max(
                SEED_SCORE_RELATIVE_TOLERANCE * abs(winner.best_score),
                SEED_SCORE_ABSOLUTE_TOLERANCE,
            )
            converged = (
                score_spread <= score_threshold + 1e-12
                and parameter_spread <= SEED_PARAMETER_TOLERANCE + 1e-12
            )
    metrics["seed_converged"] = 1.0 if converged else 0.0
    return metrics


def _seed_parameter_spread(
    runs: Sequence[OptimizerRunResult],
    active_variables: Sequence[OptimizationVariable],
) -> float:
    """Return the largest normalized range across the seed designs.

    Continuous variables use their search span as the normalization unit.
    Integer and choice variables are treated as categorical: any difference is
    a full-scale spread, so they must match exactly to count as converged.
    """

    worst = 0.0
    for variable in active_variables:
        values = [
            run.best_values[variable.name]
            for run in runs
            if run.best_values is not None and variable.name in run.best_values
        ]
        if len(values) < 2:
            continue
        if variable.kind is VariableKind.CONTINUOUS:
            span = variable.maximum - variable.minimum
            spread = (max(values) - min(values)) / span if span > 0.0 else 0.0
        else:
            reference = values[0]
            spread = (
                0.0
                if all(math.isclose(value, reference, abs_tol=1e-9) for value in values)
                else 1.0
            )
        worst = max(worst, spread)
    return worst


def _space_metrics(
    parameters: AntennaDesignParameters,
    command: OptimizeAntennaCommand,
) -> dict[str, float]:
    model = parameters.to_antenna(name="Space constraint")
    radius = turning_radius_m(parameters, model)
    boom = boom_length_m(parameters)
    metrics = {"turning_radius_m": radius}
    if boom is not None:
        metrics["boom_length_m"] = boom
    if (
        command.max_boom_length_m is not None
        and boom is not None
        and boom > command.max_boom_length_m + 1e-9
    ):
        raise _EvaluationFailure(
            f"optimize.constraint.boom_length ({boom:.3f} m > {command.max_boom_length_m:.3f} m)"
        )
    if command.max_turning_radius_m is not None and radius > command.max_turning_radius_m + 1e-9:
        raise _EvaluationFailure(
            "optimize.constraint.turning_radius "
            f"({radius:.3f} m > {command.max_turning_radius_m:.3f} m)"
        )
    return metrics


def _resolved_band_edges(command: OptimizeAntennaCommand) -> tuple[float, ...]:
    if command.mode is OptimizationMode.SINGLE:
        return ()
    if command.band_edges_hz:
        return tuple(sorted(set(command.band_edges_hz)))
    try:
        parameters = command.descriptor.build_parameters(command.descriptor.initial_values)
        frequency_hz = parameters.frequency_hz
    except Exception:
        frequency_hz = (
            command.base_spec.frequency_plan.start_hz + command.base_spec.frequency_plan.stop_hz
        ) / 2.0
    return (
        frequency_hz * (1.0 - DEFAULT_BAND_AWARE_SPAN),
        frequency_hz,
        frequency_hz * (1.0 + DEFAULT_BAND_AWARE_SPAN),
    )


def _candidate_segmentation_policy(base: SegmentationPolicy) -> SegmentationPolicy:
    """Return a policy that recalculates segment counts from each candidate.

    The UI builds a fully aligned policy for the starting design, which freezes
    explicit per-wire counts. Reusing those counts makes the objective depend on
    the starting geometry and can change the numerical result for an identical
    candidate. Preserve only the target and bounds here.
    """

    return SegmentationPolicy(
        target_segment_length_wavelengths=base.target_segment_length_wavelengths,
        min_segments_per_wire=base.min_segments_per_wire,
        max_segments_per_wire=base.max_segments_per_wire,
    )


def _spec_for_point(
    command: OptimizeAntennaCommand,
    model: AntennaModel,
    frequency_hz: float,
    *,
    needs_pattern: bool,
    needs_sweep: bool,
) -> SimulationSpec:
    if needs_sweep:
        return replace(
            command.base_spec,
            far_field=(
                command.base_spec.far_field if needs_pattern else FarFieldRequest(enabled=False)
            ),
        )
    return replace(
        command.base_spec,
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz,
            _candidate_segmentation_policy(command.base_spec.segmentation),
        ),
        far_field=(
            command.base_spec.far_field if needs_pattern else FarFieldRequest(enabled=False)
        ),
    )


def _run_point(
    command: OptimizeAntennaCommand,
    solver: AntennaSolver,
    model: AntennaModel,
    frequency_hz: float,
    *,
    needs_pattern: bool,
    needs_sweep: bool,
) -> _PointOutcome:
    try:
        result = RunSimulation(solver).execute(
            RunSimulationCommand(
                model=model,
                spec=_spec_for_point(
                    command,
                    model,
                    frequency_hz,
                    needs_pattern=needs_pattern,
                    needs_sweep=needs_sweep,
                ),
                cancel_token=command.cancel_token,
            )
        )
    except Exception as exc:
        return _PointOutcome(error=str(exc))
    if result.status is SimulationStatus.CANCELLED:
        return _PointOutcome(cancelled=True, error="cancelled")
    if result.status is not SimulationStatus.COMPLETED or not result.frequencies:
        message = next(
            (
                diagnostic.message
                for diagnostic in result.diagnostics
                if diagnostic.severity is Severity.ERROR
            ),
            result.status.value,
        )
        return _PointOutcome(error=message)
    return _PointOutcome(result=result)


def _single_metrics(
    command: OptimizeAntennaCommand,
    solver: AntennaSolver,
    parameters: AntennaDesignParameters,
    *,
    needs_pattern: bool,
    needs_sweep: bool,
) -> dict[str, float]:
    model = parameters.to_antenna(name="Optimization")
    frequency_hz = parameters.frequency_hz
    outcome = _run_point(
        command,
        solver,
        model,
        frequency_hz,
        needs_pattern=needs_pattern,
        needs_sweep=needs_sweep,
    )
    if outcome.cancelled:
        raise _EvaluationCancelled
    if outcome.error is not None or outcome.result is None:
        raise _EvaluationFailure(outcome.error or "simulation failed")
    return _metrics(
        outcome.result,
        frequency_hz,
        command.target_resistance_ohm,
        command.target_reactance_ohm,
        needs_gain=needs_pattern,
        needs_bandwidth=needs_sweep,
    )


def _scoring_frequencies(
    command: OptimizeAntennaCommand,
    band_edges: tuple[float, ...],
) -> tuple[float, ...]:
    if (
        command.objective is FamilyOptimizationObjective.MIN_SWR_OPERATING
        and command.operating_frequencies_hz
    ):
        return tuple(sorted(set(command.operating_frequencies_hz)))
    return band_edges


def _multi_metrics(
    command: OptimizeAntennaCommand,
    solver: AntennaSolver,
    descriptor: AntennaOptimizerDescriptor,
    full_values: Mapping[str, float],
    parameters: AntennaDesignParameters,
    band_edges: tuple[float, ...],
    active_variables: tuple[OptimizationVariable, ...],
    *,
    needs_pattern: bool,
) -> dict[str, float]:
    factors = (
        (-command.robust_tolerance, 0.0, command.robust_tolerance)
        if command.mode is OptimizationMode.ROBUST
        else (0.0,)
    )
    scoring_frequencies = _scoring_frequencies(command, band_edges)
    scenario_metrics: list[dict[str, float]] = []
    nominal_metrics: dict[str, float] | None = None
    all_points: list[tuple[float, dict[str, float]]] = []
    for factor in factors:
        if factor == 0.0:
            scenario_parameters = parameters
        else:
            scenario_parameters = descriptor.build_parameters(
                _perturbed_values(full_values, active_variables, factor)
            )
        model = scenario_parameters.to_antenna(name="Optimization")
        points: list[tuple[float, dict[str, float]]] = []
        for frequency_hz in scoring_frequencies:
            outcome = _run_point(
                command,
                solver,
                model,
                frequency_hz,
                needs_pattern=needs_pattern,
                needs_sweep=False,
            )
            if outcome.cancelled:
                raise _EvaluationCancelled
            if outcome.error is not None or outcome.result is None:
                raise _EvaluationFailure(outcome.error or "simulation failed")
            points.append(
                (
                    frequency_hz,
                    _metrics(
                        outcome.result,
                        frequency_hz,
                        command.target_resistance_ohm,
                        command.target_reactance_ohm,
                        needs_gain=needs_pattern,
                        needs_bandwidth=False,
                    ),
                )
            )
        aggregated = _aggregate_metrics(
            points,
            parameters.frequency_hz,
            rms_swr=command.objective is FamilyOptimizationObjective.MIN_SWR_OPERATING,
        )
        all_points.extend(points)
        if factor == 0.0:
            nominal_metrics = aggregated
        scenario_metrics.append(aggregated)
    if nominal_metrics is None:
        nominal_metrics = scenario_metrics[0]
    combined = dict(nominal_metrics)
    for name, reducer in (
        ("swr", max),
        ("operating_swr_rms", max),
        ("target_error_ohm", max),
        ("target_swr", max),
        ("max_gain_db", min),
        ("front_to_back_db", min),
        ("efficiency_percent", min),
    ):
        values = [metrics[name] for metrics in scenario_metrics if name in metrics]
        if values:
            combined[name] = reducer(values)
    scenario_scores = [_score(command, metrics) for metrics in scenario_metrics]
    if command.mode is OptimizationMode.ROBUST:
        combined["optimization_score_spread"] = max(scenario_scores) - min(scenario_scores)
    swr_values = [metrics["swr"] for _, metrics in all_points]
    combined["swr_spread"] = max(swr_values) - min(swr_values)
    combined["multi_point_count"] = float(len(scoring_frequencies))
    combined["worst_frequency_hz"] = max(all_points, key=lambda item: item[1]["swr"])[0]
    return combined


def _aggregate_metrics(
    points: list[tuple[float, dict[str, float]]],
    nominal_frequency_hz: float,
    *,
    rms_swr: bool = False,
) -> dict[str, float]:
    nearest = min(points, key=lambda item: abs(item[0] - nominal_frequency_hz))[1]
    metrics = dict(nearest)
    swr_values = [item[1]["swr"] for item in points]
    metrics["swr"] = max(swr_values)
    if rms_swr:
        metrics["operating_swr_rms"] = math.sqrt(
            sum(value * value for value in swr_values) / len(swr_values)
        )
    metrics["target_error_ohm"] = max(item[1]["target_error_ohm"] for item in points)
    metrics["target_swr"] = max(item[1]["target_swr"] for item in points)
    for name, reducer in (
        ("max_gain_db", min),
        ("front_to_back_db", min),
        ("efficiency_percent", min),
    ):
        values = [item[1][name] for item in points if name in item[1]]
        if values:
            metrics[name] = reducer(values)
    metrics["swr_spread"] = max(swr_values) - min(swr_values)
    return metrics


def _perturbed_values(
    values: Mapping[str, float],
    variables: tuple[OptimizationVariable, ...],
    factor: float,
) -> dict[str, float]:
    perturbed = dict(values)
    for variable in variables:
        if variable.kind is VariableKind.CONTINUOUS and variable.unit in ROBUST_DIMENSION_UNITS:
            adjusted = values[variable.name] * (1.0 + factor)
            perturbed[variable.name] = variable.clamp(adjusted)
    return perturbed


def _multi_score(
    command: OptimizeAntennaCommand,
    metrics: Mapping[str, float],
) -> float:
    if command.mode is OptimizationMode.SINGLE:
        return _score(command, metrics)
    spread = metrics.get("optimization_score_spread")
    score = _score(command, metrics)
    if command.mode is OptimizationMode.ROBUST and spread is not None:
        score += ROBUST_SPREAD_PENALTY * abs(spread)
    return score


def _max_swr_constraint(constraints: tuple[SoftConstraint, ...]) -> float | None:
    for constraint in constraints:
        if constraint.metric is OptimizationMetric.SWR:
            return constraint.maximum
    return None


def _summary_for(
    command: OptimizeAntennaCommand,
    result: OptimizerRunResult,
    band_edges: tuple[float, ...],
) -> OptimizationSummary:
    recommendations = build_recommendations(
        RecommendationContext(
            status=result.status,
            mode=command.mode,
            objective=command.objective,
            best_score=result.best_score,
            best_metrics=result.best_metrics,
            sensitivity=result.sensitivity,
            locked_variables=len(command.locked_variables),
            max_swr_constraint=_max_swr_constraint(command.soft_constraints),
            tolerance=command.robust_tolerance,
        )
    )
    return OptimizationSummary(
        mode=command.mode,
        objective=command.objective.value,
        status=result.status.value,
        budget_profile=command.budget_profile.value,
        evaluations=len(result.evaluations),
        seed=result.seed,
        best_values=dict(result.best_values or {}),
        best_metrics=dict(result.best_metrics),
        completed_at=utc_now(),
        band_edges_hz=band_edges if command.mode is not OptimizationMode.SINGLE else (),
        tolerance=(command.robust_tolerance if command.mode is OptimizationMode.ROBUST else 0.0),
        weights={
            "gain": command.weights.gain,
            "front_to_back": command.weights.front_to_back,
            "swr": command.weights.swr,
            "efficiency": command.weights.efficiency,
        },
        constraints=(
            *(
                (f"boom_length_m<={command.max_boom_length_m:g}",)
                if command.max_boom_length_m is not None
                else ()
            ),
            *(
                (f"turning_radius_m<={command.max_turning_radius_m:g}",)
                if command.max_turning_radius_m is not None
                else ()
            ),
            *(
                f"{constraint.metric.value}<={constraint.maximum:g}"
                for constraint in command.soft_constraints
            ),
        ),
        recommendations=recommendations,
    )


def _metrics(
    result: SimulationResult,
    frequency_hz: float,
    target_resistance_ohm: float,
    target_reactance_ohm: float,
    *,
    needs_gain: bool,
    needs_bandwidth: bool,
) -> dict[str, float]:
    point = min(
        result.frequencies,
        key=lambda item: abs(item.frequency_hz - frequency_hz),
    )
    impedance = point.impedance_ohm
    target = complex(target_resistance_ohm, target_reactance_ohm)
    metrics: dict[str, float] = {
        "resistance_ohm": impedance.real,
        "reactance_ohm": impedance.imag,
        "swr": point.swr,
        "operating_swr_rms": point.swr,
        "target_error_ohm": abs(impedance - target),
        "target_swr": swr_for_resistance(impedance, target_resistance_ohm),
    }
    if needs_gain:
        gain = max_power_gain_db(point.far_field)
        front_to_back = front_to_back_db(point.far_field)
        if gain is not None:
            metrics["max_gain_db"] = gain
        if front_to_back is not None:
            metrics["front_to_back_db"] = front_to_back
    efficiency = point.power_budget.efficiency_percent if point.power_budget is not None else None
    if efficiency is not None:
        metrics["efficiency_percent"] = efficiency
    if needs_bandwidth:
        bandwidth = measure_bandwidth_hz(
            [frequency.frequency_hz for frequency in result.frequencies],
            [frequency.swr for frequency in result.frequencies],
            center_hz=frequency_hz,
            swr_limit=2.0,
        )
        if bandwidth is not None:
            metrics["bandwidth_hz"] = bandwidth
    return metrics


def _score(
    command: OptimizeAntennaCommand,
    metrics: Mapping[str, float],
) -> float:
    objective = command.objective
    if objective is FamilyOptimizationObjective.TARGET_IMPEDANCE:
        score = _required(metrics, "target_error_ohm")
    elif objective is FamilyOptimizationObjective.MIN_SWR_OPERATING:
        score = _required(metrics, "operating_swr_rms")
    elif objective is FamilyOptimizationObjective.MIN_SWR:
        score = _required(metrics, "swr")
    elif objective is FamilyOptimizationObjective.MAX_GAIN:
        score = -_required(metrics, "max_gain_db")
    elif objective is FamilyOptimizationObjective.MAX_FRONT_TO_BACK:
        score = -_required(metrics, "front_to_back_db")
    elif objective is FamilyOptimizationObjective.MAX_EFFICIENCY:
        score = -_required(metrics, "efficiency_percent")
    elif objective is FamilyOptimizationObjective.MAX_BANDWIDTH:
        score = -_required(metrics, "bandwidth_hz")
    else:
        gain = _required(metrics, "max_gain_db") if command.weights.gain > 0.0 else 0.0
        front_to_back = (
            _required(metrics, "front_to_back_db") if command.weights.front_to_back > 0.0 else 0.0
        )
        efficiency = (
            _required(metrics, "efficiency_percent") / 100.0
            if command.weights.efficiency > 0.0
            else 0.0
        )
        swr = _required(metrics, "swr")
        # Normalize the terms so the weights are comparable: 3 dB of gain and
        # 10 dB of front-to-back ratio are one unit; SWR is already a ratio and
        # efficiency is a fraction.
        score = -(
            command.weights.gain * gain / 3.0
            + command.weights.front_to_back * front_to_back / 10.0
            - command.weights.swr * max(swr - 1.0, 0.0)
            + command.weights.efficiency * efficiency
        )
    penalty = sum(
        constraint.normalized_violation(dict(metrics)) for constraint in command.soft_constraints
    )
    return score + penalty


def _required(metrics: Mapping[str, float], name: str) -> float:
    value = metrics.get(name)
    if value is None or not math.isfinite(value):
        raise ValueError(f"the solver did not provide the {name!r} metric")
    return value
