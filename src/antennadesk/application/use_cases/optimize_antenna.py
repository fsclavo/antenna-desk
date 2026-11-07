# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Family-driven antenna optimization through the solver port."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace

from ...domain.antennas.design import AntennaDesignParameters
from ...domain.common.validation import Severity
from ...domain.optimization.constraints import OptimizationMetric, SoftConstraint
from ...domain.optimization.descriptor import (
    AntennaOptimizerDescriptor,
    FamilyOptimizationObjective,
    OptimizationWeights,
)
from ...domain.optimization.engine import (
    CandidateEvaluation,
    OptimizationBudget,
    OptimizationStatus,
    SensitivityPoint,
    optimize_design,
)
from ...domain.optimization.length import measure_bandwidth_hz
from ...domain.optimization.synthesis import swr_for_resistance
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.pattern import front_to_back_db, max_power_gain_db
from ...domain.simulation.result import SimulationResult, SimulationStatus
from ...domain.simulation.segmentation import aligned_policy_for_model
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand


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
    cancel_token: CancelToken | None = None
    progress: Callable[[int, float | None], None] | None = None

    def __post_init__(self) -> None:
        if self.target_resistance_ohm <= 0.0:
            raise ValueError("target_resistance_ohm must be positive")
        if not math.isfinite(self.target_reactance_ohm):
            raise ValueError("target_reactance_ohm must be finite")
        if self.objective not in self.descriptor.objectives:
            raise ValueError(f"objective {self.objective.value!r} is not supported")


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
    message: str = ""


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
                model = parameters.to_antenna(name="Optimization")
                frequency_hz = parameters.frequency_hz
                frequency_plan = (
                    command.base_spec.frequency_plan
                    if needs_sweep
                    else FrequencyPlan.single(frequency_hz)
                )
                far_field = (
                    command.base_spec.far_field if needs_pattern else FarFieldRequest(enabled=False)
                )
                segmentation = (
                    command.base_spec.segmentation
                    if needs_sweep
                    else aligned_policy_for_model(
                        model,
                        frequency_hz,
                        command.base_spec.segmentation,
                    )
                )
                result = RunSimulation(self.solver).execute(
                    RunSimulationCommand(
                        model=model,
                        spec=replace(
                            command.base_spec,
                            frequency_plan=frequency_plan,
                            segmentation=segmentation,
                            far_field=far_field,
                        ),
                        cancel_token=command.cancel_token,
                    )
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
            if result.status is SimulationStatus.CANCELLED:
                return CandidateEvaluation(
                    index=0,
                    values=full_values,
                    score=None,
                    feasible=False,
                    cancelled=True,
                    error="cancelled",
                )
            if result.status is not SimulationStatus.COMPLETED or not result.frequencies:
                message = next(
                    (
                        diagnostic.message
                        for diagnostic in result.diagnostics
                        if diagnostic.severity is Severity.ERROR
                    ),
                    result.status.value,
                )
                return CandidateEvaluation(
                    index=0,
                    values=full_values,
                    score=None,
                    feasible=False,
                    violation=1.0,
                    error=message,
                )
            try:
                metrics = _metrics(
                    result,
                    frequency_hz,
                    command.target_resistance_ohm,
                    command.target_reactance_ohm,
                    needs_gain=needs_pattern,
                    needs_bandwidth=needs_sweep,
                )
                score = _score(command, metrics)
            except ValueError as exc:
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

        engine_result = optimize_design(
            active_variables,
            initial_values,
            evaluate,
            budget=command.budget,
            seed=command.seed,
            start_points=start_points,
            cancel_check=(
                command.cancel_token.is_cancelled if command.cancel_token is not None else None
            ),
            progress=command.progress,
        )
        best_parameters: AntennaDesignParameters | None = None
        if engine_result.best_values is not None:
            full_values = dict(descriptor.initial_values)
            full_values.update(engine_result.best_values)
            try:
                best_parameters = descriptor.build_parameters(full_values)
            except Exception:
                best_parameters = None
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
            message=engine_result.message,
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
