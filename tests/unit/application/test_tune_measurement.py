# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Solver-backed tuning probe use case."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.application.use_cases.tune_measurement import (
    TuneMeasurement,
    TuneMeasurementCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic, Severity
from antennadesk.domain.design.tuning import TuningStatus
from antennadesk.domain.measurement import Measurement, MeasurementPoint
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class ResonanceSolver:
    """A deterministic solver whose resonance moves linearly with length."""

    def __init__(
        self,
        *,
        resonance_at_20_m: float = 7_100_000.0,
        slope_hz_per_m: float = -1_000_000.0,
        reactance_per_hz: float = 50.0,
    ) -> None:
        self.resonance_at_20_m = resonance_at_20_m
        self.slope_hz_per_m = slope_hz_per_m
        self.reactance_per_hz = reactance_per_hz
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
        resonance = self.resonance_at_20_m + self.slope_hz_per_m * (length - 20.0)
        frequencies = []
        for frequency_hz in spec.frequency_plan.frequencies_hz:
            reactance = self.reactance_per_hz * (frequency_hz - resonance) / 1e6
            impedance = complex(50.0, reactance)
            reflection = (impedance - 50.0) / (impedance + 50.0)
            magnitude = abs(reflection)
            swr = (1.0 + magnitude) / (1.0 - magnitude)
            frequencies.append(
                FrequencyResult(
                    frequency_hz=frequency_hz,
                    feed_tag=1,
                    feed_segment=1,
                    impedance_ohm=impedance,
                    swr=swr,
                    input_power_w=0.001,
                )
            )
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=tuple(frequencies),
            duration_s=0.0,
        )


class ConstantReactanceSolver(ResonanceSolver):
    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> SimulationResult:
        result = super().run(
            model,
            spec,
            progress_callback=progress_callback,
            cancel_token=cancel_token,
        )
        frequencies = tuple(
            FrequencyResult(
                frequency_hz=frequency.frequency_hz,
                feed_tag=1,
                feed_segment=1,
                impedance_ohm=complex(50.0, 0.0),
                swr=1.0,
                input_power_w=0.001,
            )
            for frequency in result.frequencies
        )
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=frequencies,
            duration_s=0.0,
        )


class ErrorSolver(ResonanceSolver):
    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> SimulationResult:
        del model, progress_callback, cancel_token
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
                    message="probe failed",
                ),
            ),
            duration_s=0.0,
        )


def _measurement() -> Measurement:
    return Measurement(
        id=UUID("00000000-0000-0000-0000-000000000042"),
        name="Field sweep",
        created_at=datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(
            MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
            MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        ),
    )


def _command(
    *,
    target: float = 7_100_000.0,
    max_adjustment: float = 0.1,
    token: EventCancelToken | None = None,
) -> TuneMeasurementCommand:
    return TuneMeasurementCommand(
        parameters=DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        measurement=_measurement(),
        base_spec=SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
        target_frequency_hz=target,
        max_adjustment_m=max_adjustment,
        cancel_token=token,
    )


def test_tuning_proposes_and_verifies_a_bounded_change() -> None:
    solver = ResonanceSolver()

    result = TuneMeasurement(solver).execute(_command())

    assert result.status is TuningStatus.PROPOSED
    assert result.slope_hz_per_m == pytest.approx(-1_000_000.0)
    assert result.proposed_dimension_m == pytest.approx(19.95)
    assert result.proposed_change_m == pytest.approx(-0.05)
    assert result.predicted_resonance_hz == pytest.approx(7_150_000.0)
    assert result.predicted_swr is not None
    assert result.predicted_swr < 1.1
    assert solver.lengths == pytest.approx([20.0, 19.9, 20.1, 19.95])
    assert all(spec.far_field.enabled is False for spec in solver.specs)
    assert all(spec.frequency_plan.count == 21 for spec in solver.specs)


def test_tuning_reports_no_sensitivity() -> None:
    result = TuneMeasurement(ConstantReactanceSolver()).execute(_command())

    assert result.status is TuningStatus.NO_SENSITIVITY


def test_tuning_reports_no_resonance() -> None:
    solver = ResonanceSolver(resonance_at_20_m=0.0, slope_hz_per_m=0.0)
    result = TuneMeasurement(solver).execute(_command())

    assert result.status is TuningStatus.NO_RESONANCE


def test_tuning_surfaces_solver_errors() -> None:
    result = TuneMeasurement(ErrorSolver()).execute(_command())

    assert result.status is TuningStatus.ERROR
    assert "probe failed" in result.detail


def test_tuning_can_be_cancelled() -> None:
    token = EventCancelToken()

    class CancellingSolver(ResonanceSolver):
        def run(
            self,
            model: AntennaModel,
            spec: SimulationSpec,
            *,
            progress_callback: object = None,
            cancel_token: object = None,
        ) -> SimulationResult:
            result = super().run(
                model,
                spec,
                progress_callback=progress_callback,
                cancel_token=cancel_token,
            )
            token.cancel()
            return result

    result = TuneMeasurement(CancellingSolver()).execute(_command(token=token))

    assert result.status is TuningStatus.CANCELLED
