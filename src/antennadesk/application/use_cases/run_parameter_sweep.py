# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Evaluate a bounded 1D/2D parameter sweep through the solver."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, replace

from ...domain.common.validation import Severity
from ...domain.design.sweep import (
    ParameterSweepResult,
    SweepAxis,
    SweepPlan,
    SweepPoint,
)
from ...domain.optimization.descriptor import AntennaOptimizerDescriptor
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.result import SimulationStatus
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

SweepProgress = Callable[[int, int], None]


@dataclass(frozen=True, slots=True)
class RunParameterSweepCommand:
    descriptor: AntennaOptimizerDescriptor
    base_spec: SimulationSpec
    plan: SweepPlan
    cancel_token: CancelToken | None = None
    progress: SweepProgress | None = None


@dataclass(frozen=True, slots=True)
class RunParameterSweep:
    solver: AntennaSolver

    def execute(self, command: RunParameterSweepCommand) -> ParameterSweepResult:
        variables = {variable.name: variable for variable in command.descriptor.variables}
        for axis in self._axes(command.plan):
            variable = variables.get(axis.name)
            if variable is None:
                raise ValueError(f"unknown sweep variable: {axis.name}")
            for value in axis.values:
                if not math.isfinite(value):
                    raise ValueError(f"sweep value for {axis.name} must be finite")
                if value < variable.minimum - 1e-9 or value > variable.maximum + 1e-9:
                    raise ValueError(
                        f"sweep value {value} for {axis.name} is outside "
                        f"[{variable.minimum}, {variable.maximum}]"
                    )
        evaluation_spec = replace(
            command.base_spec,
            frequency_plan=FrequencyPlan.single(command.plan.target_frequency_hz),
            far_field=FarFieldRequest(enabled=False),
            pattern_frequencies_hz=(),
        )
        points: list[SweepPoint] = []
        total = command.plan.point_count
        y_values: tuple[float | None, ...] = (
            command.plan.y_axis.values if command.plan.y_axis is not None else (None,)
        )
        for y_value in y_values:
            for x_value in command.plan.x_axis.values:
                if self._cancelled(command):
                    return ParameterSweepResult(
                        plan=command.plan,
                        points=tuple(points),
                        cancelled=True,
                        message="sweep cancelled",
                    )
                values = dict(command.descriptor.initial_values)
                values[command.plan.x_axis.name] = x_value
                if command.plan.y_axis is not None and y_value is not None:
                    values[command.plan.y_axis.name] = y_value
                point = self._evaluate_point(
                    command,
                    values,
                    x_value,
                    y_value,
                    evaluation_spec,
                )
                points.append(point)
                if command.progress is not None:
                    command.progress(len(points), total)
        return ParameterSweepResult(plan=command.plan, points=tuple(points))

    @staticmethod
    def _axes(plan: SweepPlan) -> tuple[SweepAxis, ...]:
        if plan.y_axis is None:
            return (plan.x_axis,)
        return (plan.x_axis, plan.y_axis)

    @staticmethod
    def _cancelled(command: RunParameterSweepCommand) -> bool:
        return bool(command.cancel_token is not None and command.cancel_token.is_cancelled())

    def _evaluate_point(
        self,
        command: RunParameterSweepCommand,
        values: dict[str, float],
        x_value: float,
        y_value: float | None,
        evaluation_spec: SimulationSpec,
    ) -> SweepPoint:
        violations = command.descriptor.validate(values)
        if violations:
            return SweepPoint(
                x_value=x_value,
                y_value=y_value,
                error="; ".join(violation.message_key for violation in violations),
            )
        try:
            parameters = command.descriptor.build_parameters(values)
            model = parameters.to_antenna(name="Parameter sweep")
        except Exception as exc:
            return SweepPoint(x_value=x_value, y_value=y_value, error=str(exc))
        result = RunSimulation(self.solver).execute(
            RunSimulationCommand(
                model=model,
                spec=evaluation_spec,
                cancel_token=command.cancel_token,
            )
        )
        if result.status is SimulationStatus.CANCELLED:
            return SweepPoint(x_value=x_value, y_value=y_value, error="cancelled")
        if result.status is not SimulationStatus.COMPLETED or not result.frequencies:
            message = next(
                (
                    diagnostic.message
                    for diagnostic in result.diagnostics
                    if diagnostic.severity is Severity.ERROR
                ),
                result.status.value,
            )
            return SweepPoint(x_value=x_value, y_value=y_value, error=message)
        frequency = result.frequencies[0]
        impedance = frequency.impedance_ohm
        return SweepPoint(
            x_value=x_value,
            y_value=y_value,
            swr=frequency.swr,
            resistance_ohm=impedance.real,
            reactance_ohm=impedance.imag,
            impedance_magnitude_ohm=abs(impedance),
        )
