# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Synthesize bounded antenna dimensions against a feed-point impedance target."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace

from ...domain.antennas.design import AntennaDesignParameters
from ...domain.common.validation import Severity
from ...domain.optimization.synthesis import (
    SynthesisEvaluation,
    SynthesisResult,
    SynthesisTarget,
    SynthesisVariable,
    synthesize_grid,
)
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.result import SimulationStatus
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

BuildParameters = Callable[[Mapping[str, float]], AntennaDesignParameters]


@dataclass(frozen=True, slots=True)
class SynthesizeAntennaCommand:
    build_parameters: BuildParameters
    variables: tuple[SynthesisVariable, ...]
    target: SynthesisTarget
    base_spec: SimulationSpec
    max_evaluations: int = 81
    cancel_token: CancelToken | None = None
    progress: Callable[[int], None] | None = None


@dataclass(frozen=True, slots=True)
class SynthesizeAntenna:
    solver: AntennaSolver

    def execute(self, command: SynthesizeAntennaCommand) -> SynthesisResult:
        evaluation_spec = replace(
            command.base_spec,
            frequency_plan=FrequencyPlan.single(command.target.frequency_hz),
            far_field=FarFieldRequest(enabled=False),
        )

        def _evaluate(values: Mapping[str, float]) -> SynthesisEvaluation:
            try:
                parameters = command.build_parameters(values)
                model = parameters.to_antenna(name="Synthesis")
                result = RunSimulation(self.solver).execute(
                    RunSimulationCommand(
                        model=model,
                        spec=evaluation_spec,
                        cancel_token=command.cancel_token,
                    )
                )
            except Exception as exc:
                return SynthesisEvaluation(0, dict(values), None, error=str(exc))
            if result.status is SimulationStatus.CANCELLED:
                return SynthesisEvaluation(0, dict(values), None, cancelled=True)
            if result.status is SimulationStatus.COMPLETED and result.frequencies:
                point = min(
                    result.frequencies,
                    key=lambda item: abs(item.frequency_hz - command.target.frequency_hz),
                )
                return SynthesisEvaluation(
                    0,
                    dict(values),
                    point.impedance_ohm,
                    swr=point.swr,
                )
            message = next(
                (
                    diagnostic.message
                    for diagnostic in result.diagnostics
                    if diagnostic.severity is Severity.ERROR
                ),
                result.status.value,
            )
            return SynthesisEvaluation(0, dict(values), None, error=message)

        completed_evaluations = 0

        def evaluate(values: Mapping[str, float]) -> SynthesisEvaluation:
            nonlocal completed_evaluations
            evaluation = _evaluate(values)
            completed_evaluations += 1
            if command.progress is not None:
                command.progress(completed_evaluations)
            return evaluation

        cancel_check = (
            command.cancel_token.is_cancelled if command.cancel_token is not None else None
        )
        return synthesize_grid(
            evaluate,
            command.variables,
            command.target,
            max_evaluations=command.max_evaluations,
            cancel_check=cancel_check,
        )
