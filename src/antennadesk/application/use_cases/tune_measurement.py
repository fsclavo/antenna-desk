# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Probe the solver for a bounded tuning change from a measurement."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, replace

from ...domain.antennas.design import (
    AntennaDesignParameters,
    primary_dimension_m,
    with_primary_dimension,
)
from ...domain.common.validation import Severity
from ...domain.design.tuning import (
    MIN_TUNING_DIMENSION_M,
    TuningProbe,
    TuningProposal,
    TuningRequest,
    TuningStatus,
    build_tuning_estimate,
    measurement_tuning_reference,
    target_swr_from_sweep,
    tuning_sweep_bounds,
    with_tuning_verification,
)
from ...domain.measurement import Measurement
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.resonance import find_resonances
from ...domain.simulation.result import SimulationStatus
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

TuningProgress = Callable[[int, int], None]
DEFAULT_SWEEP_POINTS = 21
TOTAL_PROBES = 4


@dataclass(frozen=True, slots=True)
class TuneMeasurementCommand:
    parameters: AntennaDesignParameters
    measurement: Measurement
    base_spec: SimulationSpec
    target_frequency_hz: float
    max_adjustment_m: float
    sweep_points: int = DEFAULT_SWEEP_POINTS
    cancel_token: CancelToken | None = None
    progress: TuningProgress | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("target_frequency_hz", self.target_frequency_hz),
            ("max_adjustment_m", self.max_adjustment_m),
        ):
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be positive and finite")
        if not 5 <= self.sweep_points <= 101:
            raise ValueError("sweep_points must be between 5 and 101")


@dataclass(frozen=True, slots=True)
class TuneMeasurement:
    solver: AntennaSolver

    def execute(self, command: TuneMeasurementCommand) -> TuningProposal:
        current_dimension = primary_dimension_m(command.parameters)
        measured_frequency, measured_kind = measurement_tuning_reference(
            command.measurement,
            command.target_frequency_hz,
        )
        request = TuningRequest(
            target_frequency_hz=command.target_frequency_hz,
            measured_frequency_hz=measured_frequency,
            measured_kind=measured_kind,
            current_dimension_m=current_dimension,
            max_adjustment_m=command.max_adjustment_m,
        )
        bounds_min = max(
            MIN_TUNING_DIMENSION_M,
            current_dimension - command.max_adjustment_m,
        )
        bounds_max = current_dimension + command.max_adjustment_m
        start_hz, stop_hz = tuning_sweep_bounds(
            command.target_frequency_hz,
            measured_frequency,
        )
        evaluation_spec = replace(
            command.base_spec,
            frequency_plan=FrequencyPlan.sweep(
                start_hz,
                stop_hz,
                command.sweep_points,
            ),
            far_field=FarFieldRequest(enabled=False),
        )
        step_m = max(0.001, min(0.01 * current_dimension, 0.1))
        low_dimension = max(MIN_TUNING_DIMENSION_M, current_dimension - step_m)
        high_dimension = current_dimension + step_m
        completed = 0

        def cancelled() -> bool:
            return bool(command.cancel_token is not None and command.cancel_token.is_cancelled())

        def progress() -> None:
            if command.progress is not None:
                command.progress(completed, TOTAL_PROBES)

        def evaluate(dimension_m: float) -> TuningProbe | None:
            nonlocal completed
            if cancelled():
                return None
            try:
                parameters = with_primary_dimension(command.parameters, dimension_m)
                model = parameters.to_antenna(name="Tuning")
                result = RunSimulation(self.solver).execute(
                    RunSimulationCommand(
                        model=model,
                        spec=evaluation_spec,
                        cancel_token=command.cancel_token,
                    )
                )
            except Exception as exc:
                raise _TuningFailure(str(exc)) from exc
            completed += 1
            progress()
            if result.status is SimulationStatus.CANCELLED:
                return None
            if result.status is not SimulationStatus.COMPLETED or not result.frequencies:
                message = next(
                    (
                        diagnostic.message
                        for diagnostic in result.diagnostics
                        if diagnostic.severity is Severity.ERROR
                    ),
                    result.status.value,
                )
                raise _TuningFailure(message)
            frequencies = tuple(item.frequency_hz for item in result.frequencies)
            impedances = tuple(item.impedance_ohm for item in result.frequencies)
            resonances = find_resonances(frequencies, impedances)
            if resonances:
                resonance_hz = min(
                    resonances,
                    key=lambda point: abs(point.frequency_hz - measured_frequency),
                ).frequency_hz
            else:
                resonance_hz = None
            impedance, swr = target_swr_from_sweep(
                frequencies,
                impedances,
                command.target_frequency_hz,
                command.measurement.reference_impedance_ohm,
            )
            return TuningProbe(
                dimension_m=dimension_m,
                resonance_hz=resonance_hz,
                swr_at_target=swr,
                impedance_at_target_ohm=impedance,
            )

        try:
            current = evaluate(current_dimension)
            if current is None:
                return _cancelled(request, bounds_min, bounds_max)
            low = evaluate(low_dimension)
            if low is None:
                return _cancelled(request, bounds_min, bounds_max)
            high = evaluate(high_dimension)
            if high is None:
                return _cancelled(request, bounds_min, bounds_max)
            proposal = build_tuning_estimate(
                request,
                current=current,
                low=low,
                high=high,
            )
            if (
                proposal.status is TuningStatus.PROPOSED
                and proposal.proposed_dimension_m is not None
            ):
                verification = evaluate(proposal.proposed_dimension_m)
                if verification is None:
                    return _cancelled(request, bounds_min, bounds_max)
                proposal = with_tuning_verification(proposal, verification)
            return proposal
        except _TuningFailure as exc:
            return TuningProposal(
                status=TuningStatus.ERROR,
                request=request,
                bounds_min_m=bounds_min,
                bounds_max_m=bounds_max,
                message_key="tuning.message.error",
                detail=str(exc),
            )


class _TuningFailure(Exception):
    """Internal control flow for a solver probe that cannot be used."""


def _cancelled(
    request: TuningRequest,
    bounds_min_m: float,
    bounds_max_m: float,
) -> TuningProposal:
    return TuningProposal(
        status=TuningStatus.CANCELLED,
        request=request,
        bounds_min_m=bounds_min_m,
        bounds_max_m=bounds_max_m,
        message_key="tuning.message.cancelled",
    )
