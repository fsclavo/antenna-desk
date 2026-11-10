# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.application.use_cases.optimize_elements import (
    ElementOptimizationObjective,
    ElementOptimizationWeights,
    OptimizeElements,
    OptimizeElementsCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.multi_variable import BoundedStatus, BoundedVariable
from antennadesk.domain.optimization.synthesis import SynthesisTarget
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    PowerBudget,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class AnalyticalPatternSolver:
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

    def validate(self, model: AntennaModel, spec: SimulationSpec) -> tuple[Diagnostic, ...]:
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
        length = model.wires[0].length_m
        forward = 8.0 - abs(length - 20.0)
        rear = -12.0 + abs(length - 20.0)
        far_field = tuple(
            FarFieldPoint(
                theta_deg=90.0,
                phi_deg=phi,
                gain_vertical_db=gain,
                gain_horizontal_db=None,
                gain_total_db=gain,
                axial_ratio=None,
                tilt_deg=None,
                polarization="LINEAR",
                e_theta_magnitude_v_per_m=None,
                e_theta_phase_deg=None,
                e_phi_magnitude_v_per_m=None,
                e_phi_phase_deg=None,
            )
            for phi, gain in ((0.0, forward), (180.0, rear))
        )
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=model.design_frequency_hz,
                    feed_tag=1,
                    feed_segment=1,
                    impedance_ohm=complex(50.0, 0.0),
                    swr=1.0 + abs(length - 20.0),
                    input_power_w=0.001,
                    far_field=far_field,
                    power_budget=PowerBudget(
                        input_w=1.0,
                        radiated_w=0.9,
                        structure_loss_w=0.1,
                        network_loss_w=0.0,
                        efficiency_percent=90.0 - abs(length - 20.0),
                    ),
                ),
            ),
        )


def test_target_impedance_swr_is_relative_to_the_target() -> None:
    target = SynthesisTarget(14_100_000.0, 100.0, 0.0)

    def build(values: dict[str, float]) -> DipoleParameters:
        return DipoleParameters(
            frequency_hz=target.frequency_hz,
            total_length_m=values["length_m"],
            height_m=10.0,
        )

    result = OptimizeElements(AnalyticalPatternSolver()).execute(
        OptimizeElementsCommand(
            build_parameters=build,
            variables=(BoundedVariable("length_m", 19.0, 21.0),),
            start_values={"length_m": 20.0},
            target=target,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.single(14_100_000.0),
            ),
            objective=ElementOptimizationObjective.TARGET_IMPEDANCE,
            max_evaluations=5,
            samples=3,
            passes=1,
        )
    )

    assert result.evaluations
    assert all(
        evaluation.metrics["swr"] == pytest.approx(2.0)
        for evaluation in result.evaluations
        if evaluation.metrics is not None
    )


def test_optimizer_reports_monotonic_evaluation_progress() -> None:
    target = SynthesisTarget(14_100_000.0, 100.0, 0.0)

    def build(values: dict[str, float]) -> DipoleParameters:
        return DipoleParameters(
            frequency_hz=target.frequency_hz,
            total_length_m=values["length_m"],
            height_m=10.0,
        )

    seen: list[int] = []
    result = OptimizeElements(AnalyticalPatternSolver()).execute(
        OptimizeElementsCommand(
            build_parameters=build,
            variables=(BoundedVariable("length_m", 19.0, 21.0),),
            start_values={"length_m": 20.0},
            target=target,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.single(14_100_000.0),
            ),
            objective=ElementOptimizationObjective.TARGET_IMPEDANCE,
            max_evaluations=10,
            samples=3,
            passes=1,
            progress=seen.append,
        )
    )

    assert seen == list(range(1, len(seen) + 1))
    assert seen[-1] == len(result.evaluations)


def test_multi_objective_optimizer_uses_weighted_metrics() -> None:
    target = SynthesisTarget(14_100_000.0, 50.0, 0.0)

    def build(values: dict[str, float]) -> DipoleParameters:
        return DipoleParameters(
            frequency_hz=target.frequency_hz,
            total_length_m=values["length_m"],
            height_m=10.0,
        )

    result = OptimizeElements(AnalyticalPatternSolver()).execute(
        OptimizeElementsCommand(
            build_parameters=build,
            variables=(BoundedVariable("length_m", 19.0, 21.0),),
            start_values={"length_m": 19.5},
            target=target,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.single(14_100_000.0),
                far_field=FarFieldRequest(enabled=True, theta_count=3, phi_count=3),
            ),
            objective=ElementOptimizationObjective.MULTI_OBJECTIVE,
            weights=ElementOptimizationWeights(
                gain=1.0,
                front_to_back=1.0,
                swr=1.0,
                efficiency=0.0,
            ),
            max_evaluations=30,
            samples=5,
            passes=3,
        )
    )

    assert result.status is BoundedStatus.CONVERGED
    assert result.best_values is not None
    assert result.best_values["length_m"] == pytest.approx(20.0, abs=0.05)
    best = next(
        evaluation for evaluation in result.evaluations if evaluation.values == result.best_values
    )
    assert best.metrics["max_gain_db"] == pytest.approx(8.0, abs=0.1)
    assert best.metrics["front_to_back_db"] == pytest.approx(20.0, abs=0.2)
