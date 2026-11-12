# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run bounded corner-case and Monte Carlo robustness scenarios."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from ...domain.common.validation import Severity
from ...domain.design.robustness import (
    RobustnessResult,
    RobustnessScenario,
    RobustnessScenarioKind,
    RobustnessSpec,
    corner_value_sets,
    monte_carlo_value_sets,
    robustness_variables,
)
from ...domain.optimization.descriptor import AntennaOptimizerDescriptor
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.result import SimulationStatus
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

RobustnessProgress = Callable[[int, int], None]


@dataclass(frozen=True, slots=True)
class RunRobustnessCommand:
    descriptor: AntennaOptimizerDescriptor
    base_spec: SimulationSpec
    spec: RobustnessSpec
    cancel_token: CancelToken | None = None
    progress: RobustnessProgress | None = None


@dataclass(frozen=True, slots=True)
class RunRobustness:
    solver: AntennaSolver

    def execute(self, command: RunRobustnessCommand) -> RobustnessResult:
        variables = robustness_variables(
            command.descriptor.variables,
            command.spec.variable_names,
        )
        base_values = dict(command.descriptor.initial_values)
        scenarios: list[RobustnessScenario] = []
        nominal_values = tuple((name, base_values[name]) for name in command.spec.variable_names)
        corner_sets = (
            corner_value_sets(base_values, variables, command.spec.tolerance)
            if command.spec.include_corners
            else ()
        )
        monte_carlo_sets = monte_carlo_value_sets(
            base_values,
            variables,
            command.spec.tolerance,
            command.spec.monte_carlo_samples,
            command.spec.seed,
        )
        total = 1 + len(corner_sets) + len(monte_carlo_sets)
        scenarios.append(
            self._evaluate(
                command,
                RobustnessScenarioKind.NOMINAL,
                base_values,
                nominal_values,
            )
        )
        if command.progress is not None:
            command.progress(1, total)

        for values in corner_sets:
            if self._cancelled(command):
                return RobustnessResult(
                    command.spec,
                    tuple(scenarios),
                    cancelled=True,
                    message="robustness analysis cancelled",
                )
            scenarios.append(
                self._evaluate(
                    command,
                    RobustnessScenarioKind.CORNER,
                    values,
                    tuple((name, values[name]) for name in command.spec.variable_names),
                )
            )
            if command.progress is not None:
                command.progress(len(scenarios), total)

        for values in monte_carlo_sets:
            if self._cancelled(command):
                return RobustnessResult(
                    command.spec,
                    tuple(scenarios),
                    cancelled=True,
                    message="robustness analysis cancelled",
                )
            scenarios.append(
                self._evaluate(
                    command,
                    RobustnessScenarioKind.MONTE_CARLO,
                    values,
                    tuple((name, values[name]) for name in command.spec.variable_names),
                )
            )
            if command.progress is not None:
                command.progress(len(scenarios), total)
        return RobustnessResult(command.spec, tuple(scenarios))

    @staticmethod
    def _cancelled(command: RunRobustnessCommand) -> bool:
        return bool(command.cancel_token is not None and command.cancel_token.is_cancelled())

    def _evaluate(
        self,
        command: RunRobustnessCommand,
        kind: RobustnessScenarioKind,
        values: dict[str, float],
        selected_values: tuple[tuple[str, float], ...],
    ) -> RobustnessScenario:
        violations = command.descriptor.validate(values)
        if violations:
            return RobustnessScenario(
                kind=kind,
                values=selected_values,
                error="; ".join(violation.message_key for violation in violations),
            )
        try:
            parameters = command.descriptor.build_parameters(values)
            model = parameters.to_antenna(name="Robustness")
        except Exception as exc:
            return RobustnessScenario(
                kind=kind,
                values=selected_values,
                error=str(exc),
            )
        evaluation_spec = _evaluation_spec(command)
        result = RunSimulation(self.solver).execute(
            RunSimulationCommand(
                model=model,
                spec=evaluation_spec,
                cancel_token=command.cancel_token,
            )
        )
        if result.status is SimulationStatus.CANCELLED:
            return RobustnessScenario(
                kind=kind,
                values=selected_values,
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
            return RobustnessScenario(
                kind=kind,
                values=selected_values,
                error=message,
            )
        frequency = result.frequencies[0]
        impedance = frequency.impedance_ohm
        return RobustnessScenario(
            kind=kind,
            values=selected_values,
            swr=frequency.swr,
            resistance_ohm=impedance.real,
            reactance_ohm=impedance.imag,
            impedance_magnitude_ohm=abs(impedance),
        )


def _evaluation_spec(command: RunRobustnessCommand) -> SimulationSpec:
    return replace(
        command.base_spec,
        frequency_plan=FrequencyPlan.single(command.spec.target_frequency_hz),
        far_field=FarFieldRequest(enabled=False),
        pattern_frequencies_hz=(),
    )
