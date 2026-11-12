# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Corner-case and Monte Carlo robustness use case."""

from __future__ import annotations

from dataclasses import replace

import pytest

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.application.use_cases.run_robustness import (
    RunRobustness,
    RunRobustnessCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.design.robustness import RobustnessSpec
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


class _RobustnessSolver:
    def __init__(self) -> None:
        self.calls = 0
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
        self.calls += 1
        self.specs.append(spec)
        length = model.wires[0].length_m
        height = min(point.z_m for wire in model.wires for point in (wire.start, wire.end))
        swr = 1.0 + abs(length - 10.0) * 2.0 + abs(height - 8.0) * 0.5
        impedance = complex(50.0 * swr, 0.0)
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


def _spec(**overrides: object) -> RobustnessSpec:
    values: dict[str, object] = {
        "target_frequency_hz": 7_100_000.0,
        "tolerance": 0.05,
        "variable_names": ("total_length_m", "height_m"),
        "include_corners": True,
        "monte_carlo_samples": 10,
        "seed": 0,
        "swr_limit": 2.0,
    }
    values.update(overrides)
    return RobustnessSpec(**values)  # type: ignore[arg-type]


def _command(spec: RobustnessSpec, token: EventCancelToken | None = None) -> RunRobustnessCommand:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=10.0,
        height_m=8.0,
    )
    return RunRobustnessCommand(
        descriptor=_descriptor(parameters),
        base_spec=SimulationSpec(
            frequency_plan=FrequencyPlan.single(7_100_000.0),
            far_field=FarFieldRequest(enabled=True),
        ),
        spec=spec,
        cancel_token=token,
    )


def test_robustness_runs_nominal_corners_and_monte_carlo() -> None:
    solver = _RobustnessSolver()
    progress: list[tuple[int, int]] = []
    command = replace(
        _command(_spec()),
        progress=lambda completed, total: progress.append((completed, total)),
    )

    result = RunRobustness(solver).execute(command)

    assert len(result.scenarios) == 15
    assert result.nominal is not None
    assert result.nominal.swr == pytest.approx(1.0)
    assert len(result.corners) == 4
    assert len(result.monte_carlo) == 10
    assert result.worst_corner is not None
    assert result.worst_corner.swr is not None
    assert result.worst_corner.swr > 1.0
    assert result.statistics.count == 10
    assert solver.calls == 15
    assert progress == [(index, 15) for index in range(1, 16)]
    assert all(
        spec.frequency_plan.start_hz == 7_100_000.0
        and spec.frequency_plan.count == 1
        and spec.far_field.enabled is False
        for spec in solver.specs
    )


def test_robustness_can_skip_corners_and_samples() -> None:
    solver = _RobustnessSolver()

    result = RunRobustness(solver).execute(
        _command(
            _spec(
                include_corners=False,
                monte_carlo_samples=0,
            )
        )
    )

    assert len(result.scenarios) == 1
    assert result.nominal is not None
    assert solver.calls == 1


def test_robustness_can_be_cancelled() -> None:
    token = EventCancelToken()

    class CancellingSolver(_RobustnessSolver):
        def run(self, model, spec, *, progress_callback=None, cancel_token=None):
            result = super().run(
                model,
                spec,
                progress_callback=progress_callback,
                cancel_token=cancel_token,
            )
            token.cancel()
            return result

    result = RunRobustness(CancellingSolver()).execute(_command(_spec(), token=token))

    assert result.cancelled is True
    assert len(result.scenarios) == 1


def test_robustness_rejects_invalid_dimension_names() -> None:
    with pytest.raises(ValueError, match="unknown robustness variable"):
        RunRobustness(_RobustnessSolver()).execute(_command(_spec(variable_names=("missing",))))
