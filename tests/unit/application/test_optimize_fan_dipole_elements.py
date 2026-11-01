# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.application.use_cases.optimize_fan_dipole_elements import (
    OptimizeFanDipoleElements,
    OptimizeFanDipoleElementsCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.multi_variable import BoundedStatus, BoundedVariable
from antennadesk.domain.optimization.synthesis import SynthesisTarget
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import FrequencyResult, SimulationResult, SimulationStatus
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class AnalyticalFanSolver:
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
        first = 2.0 * model.wires[0].length_m
        second = 2.0 * model.wires[2].length_m
        impedance = complex(50.0 + 10.0 * (first - 10.0), 10.0 * (second - 20.0))
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


def test_optimizes_selected_fan_dipole_element_lengths() -> None:
    base = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(FanElement(10.0), FanElement(20.0)),
        apex_height_m=10.0,
    )
    target = SynthesisTarget(7_100_000.0, 50.0, 0.0)

    def build(values: dict[str, float]) -> FanDipoleParameters:
        return FanDipoleParameters(
            frequency_hz=target.frequency_hz,
            elements=(
                FanElement(values["length_0"]),
                FanElement(values["length_1"]),
            ),
            apex_height_m=base.apex_height_m,
        )

    solver = AnalyticalFanSolver()
    result = OptimizeFanDipoleElements(solver).execute(
        OptimizeFanDipoleElementsCommand(
            build_parameters=build,
            variables=(
                BoundedVariable("length_0", 9.0, 11.0),
                BoundedVariable("length_1", 19.0, 21.0),
            ),
            start_values={"length_0": 9.5, "length_1": 19.5},
            target=target,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_300_000.0, 21),
                far_field=FarFieldRequest(enabled=True),
            ),
            max_evaluations=60,
            samples=5,
            passes=4,
        )
    )

    assert result.status is BoundedStatus.CONVERGED
    assert result.best_values is not None
    assert result.best_values["length_0"] == pytest.approx(10.0, abs=0.05)
    assert result.best_values["length_1"] == pytest.approx(20.0, abs=0.05)
    assert result.best_score == pytest.approx(0.0, abs=0.1)
    assert all(spec.frequency_plan.is_single for spec in solver.specs)
    assert all(spec.far_field.enabled is False for spec in solver.specs)
