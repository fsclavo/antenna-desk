# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.application.use_cases.synthesize_antenna import (
    SynthesizeAntenna,
    SynthesizeAntennaCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.synthesis import (
    SynthesisStatus,
    SynthesisTarget,
    SynthesisVariable,
)
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import FrequencyResult, SimulationResult, SimulationStatus
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class AnalyticalOCFDSolver:
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
        length = model.wires[0].length_m
        ratio = model.feed.offset_m / length
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
                    impedance_ohm=complex(50.0 + 100.0 * (ratio - 0.33), 20.0 * (length - 20.0)),
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
        )


def test_synthesis_uses_single_target_frequency_without_far_field() -> None:
    solver = AnalyticalOCFDSolver()
    base = OCFDParameters(frequency_hz=7_100_000.0, total_length_m=20.0, feed_ratio=0.33)
    target = SynthesisTarget(7_100_000.0, 50.0, 0.0)

    def build(values: dict[str, float]) -> OCFDParameters:
        return OCFDParameters(
            frequency_hz=target.frequency_hz,
            total_length_m=values["length_m"],
            feed_ratio=values["feed_ratio"],
            height_m=base.height_m,
        )

    result = SynthesizeAntenna(solver).execute(
        SynthesizeAntennaCommand(
            build_parameters=build,
            variables=(
                SynthesisVariable("length_m", 19.0, 21.0),
                SynthesisVariable("feed_ratio", 0.23, 0.43),
            ),
            target=target,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_300_000.0, 21),
                far_field=FarFieldRequest(enabled=True),
            ),
            max_evaluations=81,
        )
    )

    assert result.status is SynthesisStatus.CONVERGED
    assert result.best_values is not None
    assert result.best_values["length_m"] == pytest.approx(20.0)
    assert result.best_values["feed_ratio"] == pytest.approx(0.33)
    assert all(spec.frequency_plan.is_single for spec in solver.specs)
    assert all(spec.far_field.enabled is False for spec in solver.specs)
    assert all(spec.frequency_plan.start_hz == target.frequency_hz for spec in solver.specs)
