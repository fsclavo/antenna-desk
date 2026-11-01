# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.application.use_cases.optimize_moxon_elements import (
    OptimizeMoxonElements,
    OptimizeMoxonElementsCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.multi_variable import BoundedStatus, BoundedVariable
from antennadesk.domain.optimization.synthesis import SynthesisTarget
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import FrequencyResult, SimulationResult, SimulationStatus
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class AnalyticalMoxonSolver:
    def __init__(self) -> None:
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
        self.specs.append(spec)
        widths = [wire.length_m for wire in model.wires]
        depth = model.wires[3].start.x_m
        impedance = complex(
            50.0
            + 10.0 * (widths[0] - 10.0)
            + 5.0 * (depth - 3.0)
            + 2.0 * (widths[1] - 1.0)
            + 2.0 * (widths[4] - 1.0),
            0.0,
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
                    impedance_ohm=impedance,
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
        )


def test_optimizes_moxon_dimensions_for_impedance() -> None:
    base = MoxonParameters(
        frequency_hz=14_170_000.0,
        width_m=10.0,
        depth_m=3.0,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
    )
    target = SynthesisTarget(14_170_000.0, 50.0, 0.0)

    def build(values: dict[str, float]) -> MoxonParameters:
        return MoxonParameters(
            frequency_hz=target.frequency_hz,
            width_m=values["width_m"],
            depth_m=values["depth_m"],
            reflector_tip_m=values["reflector_tip_m"],
            driven_tip_m=values["driven_tip_m"],
            height_m=base.height_m,
        )

    solver = AnalyticalMoxonSolver()
    result = OptimizeMoxonElements(solver).execute(
        OptimizeMoxonElementsCommand(
            build_parameters=build,
            variables=(
                BoundedVariable("width_m", 9.0, 11.0),
                BoundedVariable("depth_m", 2.5, 3.5),
                BoundedVariable("reflector_tip_m", 0.8, 1.2),
                BoundedVariable("driven_tip_m", 0.8, 1.2),
            ),
            start_values={
                "width_m": 9.5,
                "depth_m": 2.8,
                "reflector_tip_m": 0.9,
                "driven_tip_m": 0.9,
            },
            target=target,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.single(14_170_000.0),
                far_field=FarFieldRequest(enabled=False),
            ),
            max_evaluations=250,
            samples=5,
            passes=5,
        )
    )

    assert result.status is BoundedStatus.CONVERGED
    assert result.best_values is not None
    assert result.best_values["width_m"] == pytest.approx(10.0, abs=0.05)
    assert result.best_values["depth_m"] == pytest.approx(3.0, abs=0.05)
    assert result.best_values["reflector_tip_m"] == pytest.approx(1.0, abs=0.15)
    assert result.best_values["driven_tip_m"] == pytest.approx(1.0, abs=0.15)
    assert result.best_score == pytest.approx(0.0, abs=0.5)
