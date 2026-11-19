# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Application convergence ladder with a deterministic fake solver."""

from __future__ import annotations

import pytest

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.application.ports.antenna_solver import ProgressCallback
from antennadesk.application.ports.cancellation import CancelToken
from antennadesk.application.use_cases.run_convergence_study import (
    RunConvergenceStudy,
    RunConvergenceStudyCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class FakeConvergenceSolver:
    def __init__(self, *, status: SimulationStatus = SimulationStatus.COMPLETED) -> None:
        self._status = status
        self.densities: list[float] = []

    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="fake",
            supports_frequency_sweep=True,
            supports_currents=False,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=False,
        )

    def validate(self, model: AntennaModel, spec: SimulationSpec) -> tuple[Diagnostic, ...]:
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
        del model, progress_callback, cancel_token
        density = spec.segmentation.target_segment_length_wavelengths
        self.densities.append(density)
        far_field = (
            (
                FarFieldPoint(
                    theta_deg=80.0,
                    phi_deg=0.0,
                    gain_vertical_db=2.0,
                    gain_horizontal_db=None,
                    gain_total_db=2.0 + density,
                    axial_ratio=1.0,
                    tilt_deg=0.0,
                    polarization="linear",
                    e_theta_magnitude_v_per_m=None,
                    e_theta_phase_deg=None,
                    e_phi_magnitude_v_per_m=None,
                    e_phi_phase_deg=None,
                ),
            )
            if spec.far_field.enabled
            else ()
        )
        return SimulationResult(
            status=self._status,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=7_100_000.0,
                    feed_tag=1,
                    feed_segment=5,
                    impedance_ohm=complex(50.0 + density * 100.0, density * 10.0),
                    swr=1.0 + density,
                    input_power_w=1.0,
                    far_field=far_field,
                ),
            ),
        )


def _spec() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=FarFieldRequest(enabled=False),
    )


def _model() -> AntennaModel:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna()


def test_convergence_ladder_runs_three_densities_and_patterns_at_the_ends() -> None:
    solver = FakeConvergenceSolver()
    progress: list[tuple[int, int]] = []

    result = RunConvergenceStudy(solver).execute(
        RunConvergenceStudyCommand(
            model=_model(),
            base_spec=_spec(),
            densities=(0.1, 0.05, 0.025),
            progress=lambda completed, total: progress.append((completed, total)),
        )
    )

    assert solver.densities == [0.1, 0.05, 0.025]
    assert [point.total_segments for point in result.points] == [5, 10, 19]
    assert result.points[0].max_gain_db is not None
    assert result.points[1].max_gain_db is None
    assert result.points[2].max_gain_db is not None
    assert result.points[0].takeoff_deg == pytest.approx(10.0)
    assert progress == [(1, 3), (2, 3), (3, 3)]


def test_cancelled_convergence_keeps_only_completed_points() -> None:
    token = EventCancelToken()
    token.cancel()

    result = RunConvergenceStudy(FakeConvergenceSolver()).execute(
        RunConvergenceStudyCommand(
            model=_model(),
            base_spec=_spec(),
            densities=(0.1, 0.05, 0.025),
            cancel_token=token,
        )
    )

    assert result.points == ()
    assert result.cancelled is True
    assert result.verdict.value == "incomplete"


def test_cancellation_after_one_density_keeps_the_completed_point() -> None:
    class CancelAfterFirstCheck:
        def __init__(self) -> None:
            self.checks = 0

        def is_cancelled(self) -> bool:
            self.checks += 1
            return self.checks > 1

    result = RunConvergenceStudy(FakeConvergenceSolver()).execute(
        RunConvergenceStudyCommand(
            model=_model(),
            base_spec=_spec(),
            densities=(0.1, 0.05, 0.025),
            cancel_token=CancelAfterFirstCheck(),
        )
    )

    assert len(result.points) == 1
    assert result.cancelled is True
    assert result.verdict.value == "incomplete"


def test_failed_density_is_reported_as_an_invalid_point() -> None:
    result = RunConvergenceStudy(FakeConvergenceSolver(status=SimulationStatus.ERROR)).execute(
        RunConvergenceStudyCommand(
            model=_model(),
            base_spec=_spec(),
            densities=(0.1, 0.05, 0.025),
        )
    )

    assert len(result.points) == 3
    assert all(point.error for point in result.points)
    assert result.verdict.value == "not_converged"


def test_convergence_requires_three_densities() -> None:
    with pytest.raises(ValueError, match="at least three"):
        RunConvergenceStudyCommand(
            model=_model(),
            base_spec=_spec(),
            densities=(0.1, 0.05),
        )
