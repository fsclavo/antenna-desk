# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared bounded optimizer for generated antenna elements."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from enum import StrEnum

from ...domain.antennas.design import AntennaDesignParameters
from ...domain.common.units import ensure_non_negative
from ...domain.common.validation import Severity
from ...domain.optimization.multi_variable import (
    BoundedEvaluation,
    BoundedResult,
    BoundedVariable,
    optimize_bounded,
)
from ...domain.optimization.synthesis import SynthesisTarget
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.pattern import front_to_back_db, max_power_gain_db
from ...domain.simulation.result import SimulationStatus
from ...domain.simulation.segmentation import aligned_policy_for_model
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

BuildParameters = Callable[[Mapping[str, float]], AntennaDesignParameters]


class ElementOptimizationObjective(StrEnum):
    TARGET_IMPEDANCE = "target_impedance"
    MAX_GAIN = "max_gain"
    MAX_FRONT_TO_BACK = "max_front_to_back"
    MULTI_OBJECTIVE = "multi_objective"


@dataclass(frozen=True, slots=True)
class ElementOptimizationWeights:
    gain: float = 1.0
    front_to_back: float = 1.0
    swr: float = 1.0
    efficiency: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("gain", self.gain),
            ("front_to_back", self.front_to_back),
            ("swr", self.swr),
            ("efficiency", self.efficiency),
        ):
            ensure_non_negative(value, name=f"weight_{name}")
        if (
            self.gain == 0.0
            and self.front_to_back == 0.0
            and self.swr == 0.0
            and self.efficiency == 0.0
        ):
            raise ValueError("at least one multi-objective weight must be positive")


@dataclass(frozen=True, slots=True)
class OptimizeElementsCommand:
    build_parameters: BuildParameters
    variables: tuple[BoundedVariable, ...]
    start_values: Mapping[str, float]
    target: SynthesisTarget
    base_spec: SimulationSpec
    objective: ElementOptimizationObjective = ElementOptimizationObjective.TARGET_IMPEDANCE
    weights: ElementOptimizationWeights = field(default_factory=ElementOptimizationWeights)
    max_evaluations: int = 81
    samples: int = 5
    passes: int = 4
    cancel_token: CancelToken | None = None
    progress: Callable[[int], None] | None = None


@dataclass(frozen=True, slots=True)
class OptimizeElements:
    solver: AntennaSolver

    def execute(self, command: OptimizeElementsCommand) -> BoundedResult:
        needs_pattern = command.objective in {
            ElementOptimizationObjective.MAX_GAIN,
            ElementOptimizationObjective.MAX_FRONT_TO_BACK,
            ElementOptimizationObjective.MULTI_OBJECTIVE,
        }
        if needs_pattern and not command.base_spec.far_field.enabled:
            raise ValueError("gain and front-to-back optimization require a far-field request")
        evaluation_spec = replace(
            command.base_spec,
            frequency_plan=FrequencyPlan.single(command.target.frequency_hz),
            far_field=(
                command.base_spec.far_field if needs_pattern else FarFieldRequest(enabled=False)
            ),
        )

        def _evaluate(values: Mapping[str, float]) -> BoundedEvaluation:
            try:
                parameters = command.build_parameters(values)
                model = parameters.to_antenna(name="Optimization")
                spec = replace(
                    evaluation_spec,
                    segmentation=aligned_policy_for_model(
                        model,
                        command.target.frequency_hz,
                        command.base_spec.segmentation,
                    ),
                )
                result = RunSimulation(self.solver).execute(
                    RunSimulationCommand(
                        model=model,
                        spec=spec,
                        cancel_token=command.cancel_token,
                    )
                )
            except Exception as exc:
                return BoundedEvaluation(0, dict(values), None, error=str(exc))
            if result.status is SimulationStatus.CANCELLED:
                return BoundedEvaluation(0, dict(values), None, cancelled=True)
            if result.status is SimulationStatus.COMPLETED and result.frequencies:
                point = min(
                    result.frequencies,
                    key=lambda item: abs(item.frequency_hz - command.target.frequency_hz),
                )
                impedance = point.impedance_ohm
                swr = command.target.swr(impedance)
                metrics = {
                    "resistance_ohm": impedance.real,
                    "reactance_ohm": impedance.imag,
                    "swr": swr,
                }
                if command.objective is ElementOptimizationObjective.TARGET_IMPEDANCE:
                    score = abs(impedance - command.target.impedance_ohm)
                elif command.objective is ElementOptimizationObjective.MAX_GAIN:
                    gain = max_power_gain_db(point.far_field)
                    if gain is None:
                        return BoundedEvaluation(
                            0, dict(values), None, error="no far-field gain data"
                        )
                    metrics["max_gain_db"] = gain
                    score = -gain
                elif command.objective is ElementOptimizationObjective.MAX_FRONT_TO_BACK:
                    front_to_back = front_to_back_db(point.far_field)
                    if front_to_back is None:
                        return BoundedEvaluation(
                            0, dict(values), None, error="no front-to-back data"
                        )
                    metrics["front_to_back_db"] = front_to_back
                    score = -front_to_back
                else:
                    weights = command.weights
                    gain = max_power_gain_db(point.far_field)
                    front_to_back = front_to_back_db(point.far_field)
                    if weights.gain > 0.0 and gain is None:
                        return BoundedEvaluation(
                            0, dict(values), None, error="no far-field gain data"
                        )
                    if weights.front_to_back > 0.0 and front_to_back is None:
                        return BoundedEvaluation(
                            0, dict(values), None, error="no front-to-back data"
                        )
                    efficiency = (
                        point.power_budget.efficiency_percent / 100.0
                        if point.power_budget is not None
                        else None
                    )
                    if weights.efficiency > 0.0 and efficiency is None:
                        return BoundedEvaluation(0, dict(values), None, error="no efficiency data")
                    gain_value = gain if gain is not None else 0.0
                    front_to_back_value = front_to_back if front_to_back is not None else 0.0
                    efficiency_value = efficiency if efficiency is not None else 0.0
                    score = -(
                        weights.gain * gain_value
                        + weights.front_to_back * front_to_back_value
                        - weights.swr * max(swr - 1.0, 0.0)
                        + weights.efficiency * efficiency_value
                    )
                    metrics["max_gain_db"] = gain_value
                    metrics["front_to_back_db"] = front_to_back_value
                    if efficiency is not None:
                        metrics["efficiency_percent"] = (
                            point.power_budget.efficiency_percent
                            if point.power_budget is not None
                            else 0.0
                        )
                return BoundedEvaluation(0, dict(values), score, metrics=metrics)
            message = next(
                (
                    diagnostic.message
                    for diagnostic in result.diagnostics
                    if diagnostic.severity is Severity.ERROR
                ),
                result.status.value,
            )
            return BoundedEvaluation(0, dict(values), None, error=message)

        completed_evaluations = 0

        def evaluate(values: Mapping[str, float]) -> BoundedEvaluation:
            nonlocal completed_evaluations
            evaluation = _evaluate(values)
            completed_evaluations += 1
            if command.progress is not None:
                command.progress(completed_evaluations)
            return evaluation

        cancel_check = (
            command.cancel_token.is_cancelled if command.cancel_token is not None else None
        )
        return optimize_bounded(
            evaluate,
            command.variables,
            command.start_values,
            max_evaluations=command.max_evaluations,
            samples=command.samples,
            passes=command.passes,
            cancel_check=cancel_check,
        )
