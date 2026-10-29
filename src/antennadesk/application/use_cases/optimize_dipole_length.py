# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimize an antenna primary dimension against a reactance target."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ...domain.antennas.design import (
    AntennaDesignParameters,
    with_primary_dimension,
)
from ...domain.common.validation import Severity
from ...domain.optimization.length import (
    LengthEvaluation,
    LengthOptimizationResult,
    LengthOptimizationSpec,
    LengthOptimizationStatus,
    LengthSensitivityPoint,
    OptimizationObjective,
    measure_bandwidth_hz,
    optimize_length,
)
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.result import SimulationStatus
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand


@dataclass(frozen=True, slots=True)
class OptimizeDipoleLengthCommand:
    parameters: AntennaDesignParameters
    base_spec: SimulationSpec
    optimization_spec: LengthOptimizationSpec
    cancel_token: CancelToken | None = None


@dataclass(frozen=True, slots=True)
class OptimizeDipoleLength:
    solver: AntennaSolver

    def execute(self, command: OptimizeDipoleLengthCommand) -> LengthOptimizationResult:
        optimization_spec = command.optimization_spec
        base_model = command.parameters.to_antenna(name="Optimization")
        if optimization_spec.objective is OptimizationObjective.MAX_BANDWIDTH:
            if command.base_spec.frequency_plan.count < 2:
                raise ValueError("bandwidth optimization requires a frequency sweep")
            evaluation_spec = replace(
                command.base_spec,
                far_field=FarFieldRequest(enabled=False),
            )
        else:
            evaluation_spec = replace(
                command.base_spec,
                frequency_plan=FrequencyPlan.single(command.parameters.frequency_hz),
                far_field=FarFieldRequest(enabled=False),
            )

        def evaluate(length_m: float) -> LengthEvaluation:
            try:
                model = with_primary_dimension(command.parameters, length_m).to_antenna(
                    name=base_model.name
                )
                result = RunSimulation(self.solver).execute(
                    RunSimulationCommand(
                        model=model,
                        spec=evaluation_spec,
                        cancel_token=command.cancel_token,
                    )
                )
            except Exception as exc:
                return LengthEvaluation(length_m, None, error=str(exc))
            if result.status is SimulationStatus.CANCELLED:
                return LengthEvaluation(length_m, None, error="cancelled", cancelled=True)
            if result.status is SimulationStatus.COMPLETED and result.frequencies:
                frequency = min(
                    result.frequencies,
                    key=lambda item: abs(item.frequency_hz - command.parameters.frequency_hz),
                )
                bandwidth_hz = None
                if optimization_spec.objective is OptimizationObjective.MAX_BANDWIDTH:
                    bandwidth_hz = measure_bandwidth_hz(
                        [item.frequency_hz for item in result.frequencies],
                        [item.swr for item in result.frequencies],
                        center_hz=command.parameters.frequency_hz,
                        swr_limit=optimization_spec.swr_limit,
                    )
                return LengthEvaluation(
                    length_m=length_m,
                    impedance_ohm=frequency.impedance_ohm,
                    swr=frequency.swr,
                    bandwidth_hz=bandwidth_hz,
                )
            message = next(
                (
                    diagnostic.message
                    for diagnostic in result.diagnostics
                    if diagnostic.severity is Severity.ERROR
                ),
                result.status.value,
            )
            return LengthEvaluation(length_m, None, error=message)

        cancel_check = (
            command.cancel_token.is_cancelled if command.cancel_token is not None else None
        )
        result = optimize_length(
            evaluate,
            optimization_spec,
            cancel_check=cancel_check,
        )
        if result.best_length_m is None or result.status in {
            LengthOptimizationStatus.ERROR,
            LengthOptimizationStatus.CANCELLED,
        }:
            return result

        sensitivity: list[LengthSensitivityPoint] = []
        for offset in optimization_spec.sensitivity_offsets_m:
            for sign in (-1.0, 1.0):
                length = result.best_length_m + sign * offset
                if (
                    length < optimization_spec.min_length_m
                    or length > optimization_spec.max_length_m
                ):
                    continue
                if cancel_check is not None and cancel_check():
                    break
                evaluation = evaluate(length)
                if evaluation.cancelled:
                    break
                sensitivity.append(
                    LengthSensitivityPoint(
                        length_m=length,
                        offset_m=sign * offset,
                        impedance_ohm=evaluation.impedance_ohm,
                        swr=evaluation.swr,
                        bandwidth_hz=evaluation.bandwidth_hz,
                        error=evaluation.error,
                    )
                )
        return replace(result, sensitivity=tuple(sensitivity))


OptimizeAntennaDimensionCommand = OptimizeDipoleLengthCommand
OptimizeAntennaDimension = OptimizeDipoleLength
