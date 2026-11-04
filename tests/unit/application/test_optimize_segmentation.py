# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.application.use_cases.optimize_elements import (
    ElementOptimizationObjective,
    OptimizeElements,
    OptimizeElementsCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.multi_variable import BoundedStatus, BoundedVariable
from antennadesk.domain.optimization.synthesis import SynthesisTarget
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class CapturingSolver:
    def __init__(self) -> None:
        self.specs: list[SimulationSpec] = []

    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="capture",
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
        return SolverMetadata(name="capture", version="1")

    def run(self, model: AntennaModel, spec: SimulationSpec, **kwargs: object) -> SimulationResult:
        self.specs.append(spec)
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
                    impedance_ohm=complex(50.0, 0.0),
                    swr=1.0,
                    input_power_w=1.0,
                ),
            ),
        )


def test_optimizer_recomputes_segmentation_for_the_target_frequency() -> None:
    solver = CapturingSolver()
    base_spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
    )
    command = OptimizeElementsCommand(
        build_parameters=lambda values: DipoleParameters(
            frequency_hz=28_400_000.0,
            total_length_m=values["length_m"],
            height_m=8.0,
        ),
        variables=(BoundedVariable("length_m", 19.0, 21.0),),
        start_values={"length_m": 20.0},
        target=SynthesisTarget(frequency_hz=28_400_000.0, resistance_ohm=50.0),
        base_spec=base_spec,
        objective=ElementOptimizationObjective.TARGET_IMPEDANCE,
        max_evaluations=10,
        samples=3,
        passes=1,
    )

    result = OptimizeElements(solver).execute(command)

    assert result.status is BoundedStatus.CONVERGED
    assert solver.specs
    assert solver.specs[0].frequency_plan.start_hz == 28_400_000.0
    wire_segments = dict(solver.specs[0].segmentation.wire_segments)
    assert wire_segments["radiator"] > 20
