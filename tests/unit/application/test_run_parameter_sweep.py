# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded parameter sweep use case."""

from __future__ import annotations

from dataclasses import replace

import pytest

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.application.use_cases.run_parameter_sweep import (
    RunParameterSweep,
    RunParameterSweepCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic, Severity
from antennadesk.domain.design.sweep import (
    ParameterSweepResult,
    SweepAxis,
    SweepMetric,
    SweepPlan,
)
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class SweepSolver:
    def __init__(self, error_length_m: float | None = None) -> None:
        self.error_length_m = error_length_m
        self.lengths: list[float] = []
        self.specs: list[SimulationSpec] = []

    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="analytical",
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
        return SolverMetadata(name="analytical", version="1.0")

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> SimulationResult:
        del progress_callback, cancel_token
        length = model.wires[0].length_m
        self.lengths.append(length)
        self.specs.append(spec)
        if self.error_length_m is not None and length == pytest.approx(self.error_length_m):
            return SimulationResult(
                status=SimulationStatus.ERROR,
                spec=spec,
                model_fingerprint="a" * 64,
                solver=self.version(),
                frequencies=(),
                diagnostics=(
                    Diagnostic(
                        code="solver.test",
                        severity=Severity.ERROR,
                        message="sweep probe failed",
                    ),
                ),
                duration_s=0.0,
            )
        resistance = 50.0 + (length - 10.0) * 5.0
        reactance = (length - 10.0) * 10.0
        impedance = complex(resistance, reactance)
        reflection = (impedance - 50.0) / (impedance + 50.0)
        magnitude = abs(reflection)
        swr = (1.0 + magnitude) / (1.0 - magnitude)
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=spec.frequency_plan.start_hz,
                    feed_tag=1,
                    feed_segment=1,
                    impedance_ohm=impedance,
                    swr=swr,
                    input_power_w=0.001,
                ),
            ),
            duration_s=0.0,
        )


def _descriptor(parameters: DipoleParameters):
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    return availability.descriptor


def _plan(
    y_values: tuple[float, ...] | None = None,
    metric: SweepMetric = SweepMetric.SWR,
) -> SweepPlan:
    return SweepPlan(
        x_axis=SweepAxis(
            name="total_length_m",
            label_key="field.length",
            unit="m",
            values=(9.0, 9.5, 10.0, 10.5, 11.0) if y_values is None else (9.0, 10.0, 11.0),
        ),
        y_axis=(
            SweepAxis(
                name="height_m",
                label_key="field.height",
                unit="m",
                values=y_values,
            )
            if y_values is not None
            else None
        ),
        metric=metric,
        target_frequency_hz=7_100_000.0,
    )


def _command(
    plan: SweepPlan,
    token: EventCancelToken | None = None,
) -> RunParameterSweepCommand:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=10.0,
        height_m=8.0,
    )
    return RunParameterSweepCommand(
        descriptor=_descriptor(parameters),
        base_spec=SimulationSpec(
            frequency_plan=FrequencyPlan.single(7_100_000.0),
            far_field=FarFieldRequest(enabled=True),
        ),
        plan=plan,
        cancel_token=token,
    )


def test_1d_sweep_runs_each_point_and_finds_best_swr() -> None:
    solver = SweepSolver()
    progress: list[tuple[int, int]] = []

    command = replace(
        _command(_plan()),
        progress=lambda completed, total: progress.append((completed, total)),
    )
    result = RunParameterSweep(solver).execute(command)

    assert isinstance(result, ParameterSweepResult)
    assert result.completed_count == 5
    assert result.cancelled is False
    best = result.best_swr_point
    assert best is not None
    assert best.x_value == pytest.approx(10.0)
    assert solver.lengths == pytest.approx([9.0, 9.5, 10.0, 10.5, 11.0])
    assert all(spec.far_field.enabled is False for spec in solver.specs)
    assert progress == [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5)]


def test_2d_sweep_uses_y_outer_order() -> None:
    solver = SweepSolver()

    result = RunParameterSweep(solver).execute(_command(_plan((8.0, 9.0))))

    assert result.completed_count == 6
    assert [point.y_value for point in result.points] == [8.0, 8.0, 8.0, 9.0, 9.0, 9.0]
    assert len(solver.lengths) == 6


def test_sweep_records_solver_errors_per_point() -> None:
    solver = SweepSolver(error_length_m=10.5)

    result = RunParameterSweep(solver).execute(_command(_plan()))

    failed = [point for point in result.points if point.error]
    assert len(failed) == 1
    assert failed[0].x_value == pytest.approx(10.5)
    assert "sweep probe failed" in failed[0].error
    assert result.valid_count == 4


def test_sweep_can_be_cancelled() -> None:
    token = EventCancelToken()

    class CancellingSolver(SweepSolver):
        def run(self, model, spec, *, progress_callback=None, cancel_token=None):
            result = super().run(
                model,
                spec,
                progress_callback=progress_callback,
                cancel_token=cancel_token,
            )
            token.cancel()
            return result

    result = RunParameterSweep(CancellingSolver()).execute(_command(_plan(), token=token))

    assert result.cancelled is True
    assert result.completed_count == 1


def test_sweep_rejects_values_outside_variable_bounds() -> None:
    plan = SweepPlan(
        x_axis=SweepAxis(
            name="total_length_m",
            label_key="field.length",
            unit="m",
            values=(0.01, 10.0),
        ),
        y_axis=None,
        metric=SweepMetric.SWR,
        target_frequency_hz=7_100_000.0,
    )

    with pytest.raises(ValueError, match="outside"):
        RunParameterSweep(SweepSolver()).execute(_command(plan))
