# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimize a dipole length against a reactance target."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ...domain.antennas.dipole import DipoleParameters
from ...domain.common.validation import Severity
from ...domain.optimization.length import (
    LengthEvaluation,
    LengthOptimizationResult,
    LengthOptimizationSpec,
    LengthOptimizationStatus,
    LengthSensitivityPoint,
    optimize_length,
)
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.result import SimulationStatus
from ...domain.simulation.segmentation import SegmentationPolicy
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand


@dataclass(frozen=True, slots=True)
class OptimizeDipoleLengthCommand:
    parameters: DipoleParameters
    base_spec: SimulationSpec
    optimization_spec: LengthOptimizationSpec
    cancel_token: CancelToken | None = None


@dataclass(frozen=True, slots=True)
class OptimizeDipoleLength:
    solver: AntennaSolver

    def execute(self, command: OptimizeDipoleLengthCommand) -> LengthOptimizationResult:
        optimization_spec = command.optimization_spec
        base_model = command.parameters.to_antenna(name="Optimization")
        segments = command.base_spec.segmentation.segments_for(
            base_model.wires[0],
            command.base_spec.frequency_plan.stop_hz,
        )
        evaluation_spec = replace(
            command.base_spec,
            frequency_plan=FrequencyPlan.single(command.parameters.frequency_hz),
            segmentation=SegmentationPolicy(segments_per_wire=segments),
            far_field=FarFieldRequest(enabled=False),
        )

        def evaluate(length_m: float) -> LengthEvaluation:
            try:
                model = command.parameters.with_length(length_m).to_antenna(name=base_model.name)
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
                frequency = result.frequencies[0]
                return LengthEvaluation(
                    length_m=length_m,
                    impedance_ohm=frequency.impedance_ohm,
                    swr=frequency.swr,
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
                        error=evaluation.error,
                    )
                )
        return replace(result, sensitivity=tuple(sensitivity))
