# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import threading
from dataclasses import replace

import pytest

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.application.ports.antenna_solver import ProgressCallback
from antennadesk.application.ports.cancellation import CancelToken
from antennadesk.application.use_cases.optimize_antenna import (
    OptimizeAntenna,
    OptimizeAntennaCommand,
    OptimizeAntennaResult,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.descriptor import FamilyOptimizationObjective
from antennadesk.domain.optimization.engine import (
    BudgetProfile,
    OptimizationStatus,
    budget_for,
)
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.pattern_resolution import far_field_request


class LengthSolver:
    """A deterministic solver whose resistance depends on total wire length."""

    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="fake",
            supports_frequency_sweep=True,
            supports_currents=True,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )

    def validate(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
    ) -> tuple[Diagnostic, ...]:
        del model, spec
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="fake", version="1.0")

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult:
        del progress_callback, cancel_token
        length_m = model.wires[0].length_m
        resistance = 50.0 + (length_m - 20.0) * 10.0
        point = FrequencyResult(
            frequency_hz=spec.frequency_plan.start_hz,
            feed_tag=1,
            feed_segment=1,
            impedance_ohm=complex(resistance, 0.0),
            swr=1.0,
            input_power_w=0.001,
        )
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(point,),
            duration_s=0.01,
        )


class CancellingSolver(LengthSolver):
    """Cancel the run after a few completed evaluations."""

    def __init__(self, token: EventCancelToken, cancel_after: int = 2) -> None:
        self._token = token
        self._cancel_after = cancel_after
        self._calls = 0
        self._lock = threading.Lock()

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult:
        if self._token.is_cancelled():
            return SimulationResult(
                status=SimulationStatus.CANCELLED,
                spec=spec,
                model_fingerprint="a" * 64,
                solver=self.version(),
                frequencies=(),
                duration_s=0.0,
            )
        result = super().run(
            model,
            spec,
            progress_callback=progress_callback,
            cancel_token=cancel_token,
        )
        with self._lock:
            self._calls += 1
            if self._calls >= self._cancel_after:
                self._token.cancel()
        return result


def _spec(parameters: DipoleParameters) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6.7e6, 7.5e6, 11),
        far_field=far_field_request(5.0, parameters.ground),
    )


def test_optimize_antenna_returns_the_best_parameters() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=18.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor

    result = OptimizeAntenna(LengthSolver()).execute(
        OptimizeAntennaCommand(
            descriptor=descriptor,
            base_spec=_spec(parameters),
            objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
            budget=budget_for(BudgetProfile.FAST, len(descriptor.variables)),
            seed=5,
        )
    )

    assert result.best_parameters is not None
    assert isinstance(result.best_parameters, DipoleParameters)
    assert result.best_parameters.total_length_m == pytest.approx(20.0, abs=0.25)
    assert result.best_score is not None
    assert result.best_score < 2.0
    assert result.evaluations


def test_optimize_antenna_parallel_workers_are_deterministic() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=18.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor

    def run() -> OptimizeAntennaResult:
        return OptimizeAntenna(LengthSolver()).execute(
            OptimizeAntennaCommand(
                descriptor=descriptor,
                base_spec=_spec(parameters),
                objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
                budget=budget_for(BudgetProfile.FAST, len(descriptor.variables)),
                seed=5,
                parallel_workers=3,
            )
        )

    first = run()
    second = run()

    assert first.best_values == second.best_values
    assert first.best_score == second.best_score
    assert [item.values for item in first.evaluations] == [
        item.values for item in second.evaluations
    ]
    assert [item.index for item in first.evaluations] == list(range(1, len(first.evaluations) + 1))


def test_optimize_antenna_parallel_cancellation_stops_the_pool() -> None:
    token = EventCancelToken()
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=18.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor
    budget = budget_for(BudgetProfile.FAST, len(descriptor.variables))

    result = OptimizeAntenna(CancellingSolver(token)).execute(
        OptimizeAntennaCommand(
            descriptor=descriptor,
            base_spec=_spec(parameters),
            objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
            budget=budget,
            seed=5,
            parallel_workers=3,
            cancel_token=token,
        )
    )

    assert result.status is OptimizationStatus.CANCELLED
    assert result.evaluations
    assert len(result.evaluations) < budget.total


def test_optimize_antenna_rejects_an_unsupported_objective() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None

    unsupported = replace(
        availability.descriptor,
        objectives=frozenset({FamilyOptimizationObjective.TARGET_IMPEDANCE}),
    )

    with pytest.raises(ValueError, match="not supported"):
        OptimizeAntennaCommand(
            descriptor=unsupported,
            base_spec=_spec(parameters),
            objective=FamilyOptimizationObjective.MAX_BANDWIDTH,
            budget=budget_for(BudgetProfile.FAST, 3),
        )


@pytest.mark.parametrize("workers", [0, 9])
def test_optimize_antenna_rejects_invalid_worker_counts(workers: int) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None

    with pytest.raises(ValueError, match="parallel_workers"):
        OptimizeAntennaCommand(
            descriptor=availability.descriptor,
            base_spec=_spec(parameters),
            objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
            budget=budget_for(BudgetProfile.FAST, 3),
            parallel_workers=workers,
        )


def test_optimize_antenna_reports_missing_gain_metrics() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    spec = replace(
        _spec(parameters),
        far_field=replace(_spec(parameters).far_field, enabled=False),
    )

    with pytest.raises(ValueError, match="far-field"):
        OptimizeAntenna(LengthSolver()).execute(
            OptimizeAntennaCommand(
                descriptor=availability.descriptor,
                base_spec=spec,
                objective=FamilyOptimizationObjective.MAX_GAIN,
                budget=budget_for(BudgetProfile.FAST, 3),
            )
        )
