# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimize selected fan-dipole element lengths against an impedance target."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace

from ...domain.antennas.fan_dipole import FanDipoleParameters
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
from ...domain.simulation.result import SimulationStatus
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

BuildFanParameters = Callable[[Mapping[str, float]], FanDipoleParameters]


@dataclass(frozen=True, slots=True)
class OptimizeFanDipoleElementsCommand:
    build_parameters: BuildFanParameters
    variables: tuple[BoundedVariable, ...]
    start_values: Mapping[str, float]
    target: SynthesisTarget
    base_spec: SimulationSpec
    max_evaluations: int = 81
    samples: int = 5
    passes: int = 4
    cancel_token: CancelToken | None = None


@dataclass(frozen=True, slots=True)
class OptimizeFanDipoleElements:
    solver: AntennaSolver

    def execute(self, command: OptimizeFanDipoleElementsCommand) -> BoundedResult:
        evaluation_spec = replace(
            command.base_spec,
            frequency_plan=FrequencyPlan.single(command.target.frequency_hz),
            far_field=FarFieldRequest(enabled=False),
        )

        def evaluate(values: Mapping[str, float]) -> BoundedEvaluation:
            try:
                parameters = command.build_parameters(values)
                result = RunSimulation(self.solver).execute(
                    RunSimulationCommand(
                        model=parameters.to_antenna(name="Fan dipole"),
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
                return BoundedEvaluation(
                    0,
                    dict(values),
                    abs(impedance - command.target.impedance_ohm),
                    metrics={
                        "resistance_ohm": impedance.real,
                        "reactance_ohm": impedance.imag,
                        "swr": point.swr,
                    },
                )
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
