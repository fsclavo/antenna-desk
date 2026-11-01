# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared bounded optimizer for generated antenna elements."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from enum import StrEnum

from ...domain.antennas.design import AntennaDesignParameters
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
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

BuildParameters = Callable[[Mapping[str, float]], AntennaDesignParameters]


class ElementOptimizationObjective(StrEnum):
    TARGET_IMPEDANCE = "target_impedance"
    MAX_GAIN = "max_gain"
    MAX_FRONT_TO_BACK = "max_front_to_back"


@dataclass(frozen=True, slots=True)
class OptimizeElementsCommand:
    build_parameters: BuildParameters
    variables: tuple[BoundedVariable, ...]
    start_values: Mapping[str, float]
    target: SynthesisTarget
    base_spec: SimulationSpec
    objective: ElementOptimizationObjective = ElementOptimizationObjective.TARGET_IMPEDANCE
    max_evaluations: int = 81
    samples: int = 5
    passes: int = 4
    cancel_token: CancelToken | None = None


@dataclass(frozen=True, slots=True)
class OptimizeElements:
    solver: AntennaSolver

    def execute(self, command: OptimizeElementsCommand) -> BoundedResult:
        needs_pattern = command.objective in {
            ElementOptimizationObjective.MAX_GAIN,
            ElementOptimizationObjective.MAX_FRONT_TO_BACK,
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

        def evaluate(values: Mapping[str, float]) -> BoundedEvaluation:
            try:
                parameters = command.build_parameters(values)
                result = RunSimulation(self.solver).execute(
                    RunSimulationCommand(
                        model=parameters.to_antenna(name="Optimization"),
                        spec=evaluation_spec,
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
                metrics = {
                    "resistance_ohm": impedance.real,
                    "reactance_ohm": impedance.imag,
                    "swr": point.swr,
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
                else:
                    front_to_back = front_to_back_db(point.far_field)
                    if front_to_back is None:
                        return BoundedEvaluation(
                            0, dict(values), None, error="no front-to-back data"
                        )
                    metrics["front_to_back_db"] = front_to_back
                    score = -front_to_back
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
