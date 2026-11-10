# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Target-frequency scoring, robust scope, and segmentation consistency."""

from __future__ import annotations

from dataclasses import replace

from antennadesk.application.ports.antenna_solver import ProgressCallback
from antennadesk.application.ports.cancellation import CancelToken
from antennadesk.application.use_cases.optimize_antenna import (
    OptimizeAntenna,
    OptimizeAntennaCommand,
    _spec_for_point,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.descriptor import FamilyOptimizationObjective
from antennadesk.domain.optimization.engine import (
    OptimizationBudget,
    OptimizationStatus,
)
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.optimization.summary import OptimizationMode
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_model,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec

BAND_EDGES = (
    7_000_000.0,
    7_150_000.0,
    7_300_000.0,
    14_000_000.0,
    14_175_000.0,
    14_350_000.0,
    28_000_000.0,
    28_850_000.0,
    29_700_000.0,
)
OPERATING = (7_100_000.0, 14_200_000.0, 28_400_000.0)


class RecordingSolver:
    def __init__(self) -> None:
        self.frequencies: list[float] = []
        self.radii: list[float] = []
        self.heights: list[float] = []
        self.lengths: list[float] = []

    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="recording",
            supports_frequency_sweep=True,
            supports_currents=True,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )

    def validate(self, model: AntennaModel, spec: SimulationSpec) -> tuple[Diagnostic, ...]:
        del model, spec
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="recording", version="1.0")

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult:
        del progress_callback, cancel_token
        self.frequencies.append(spec.frequency_plan.start_hz)
        self.radii.append(model.wires[0].radius_m)
        self.heights.append(model.wires[0].start.z_m)
        self.lengths.append(model.wires[0].length_m)
        frequency_hz = spec.frequency_plan.start_hz
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=frequency_hz,
                    feed_tag=1,
                    feed_segment=1,
                    impedance_ohm=complex(50.0, 0.0),
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
            duration_s=0.01,
        )


def _parameters() -> OCFDParameters:
    return OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.4,
        feed_ratio=1.0 / 3.0,
        height_m=10.0,
        transformer_ratio=4.0,
    )


def _spec(parameters: OCFDParameters) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(parameters.frequency_hz * 0.98, 7_300_000.0, 11),
    )


def _command(
    parameters: OCFDParameters,
    *,
    mode: OptimizationMode = OptimizationMode.SINGLE,
    objective: FamilyOptimizationObjective = FamilyOptimizationObjective.MIN_SWR,
    budget: OptimizationBudget | None = None,
    base_spec: SimulationSpec | None = None,
    locked: frozenset[str] = frozenset(),
    operating: tuple[float, ...] = (),
    tolerance: float = 0.0,
) -> OptimizeAntennaCommand:
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    return OptimizeAntennaCommand(
        descriptor=availability.descriptor,
        base_spec=base_spec or _spec(parameters),
        objective=objective,
        budget=budget or OptimizationBudget(4, 4, 2),
        mode=mode,
        band_edges_hz=BAND_EDGES if mode is not OptimizationMode.SINGLE else (),
        operating_frequencies_hz=operating,
        robust_tolerance=tolerance,
        locked_variables=locked,
    )


def test_operating_objective_scores_only_operating_frequencies() -> None:
    solver = RecordingSolver()
    result = OptimizeAntenna(solver).execute(
        _command(
            _parameters(),
            mode=OptimizationMode.BAND_AWARE,
            objective=FamilyOptimizationObjective.MIN_SWR_OPERATING,
            operating=OPERATING,
        )
    )

    assert result.status is not OptimizationStatus.ERROR
    assert set(solver.frequencies) <= set(OPERATING)
    assert result.best_metrics["multi_point_count"] == len(OPERATING)


def test_robust_does_not_perturb_locked_variables() -> None:
    solver = RecordingSolver()
    parameters = _parameters()
    result = OptimizeAntenna(solver).execute(
        _command(
            parameters,
            mode=OptimizationMode.ROBUST,
            objective=FamilyOptimizationObjective.MIN_SWR_OPERATING,
            operating=OPERATING,
            tolerance=0.05,
            locked=frozenset({"feed_ratio", "height_m", "wire_radius_m", "transformer_ratio"}),
        )
    )

    assert result.status is not OptimizationStatus.ERROR
    assert set(solver.radii) == {parameters.wire_radius_m}
    assert set(solver.heights) == {parameters.height_m}
    assert len(set(solver.lengths)) > 1


def test_candidate_segmentation_is_independent_of_the_start_geometry() -> None:
    parameters = _parameters()
    candidate = replace(parameters, total_length_m=20.4)
    candidate_model = candidate.to_antenna()
    starts = (
        replace(parameters, total_length_m=18.0),
        replace(parameters, total_length_m=22.0),
    )
    specs = []
    for start in starts:
        base = aligned_policy_for_model(
            start.to_antenna(),
            parameters.frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        )
        command = _command(parameters, base_spec=replace(_spec(parameters), segmentation=base))
        specs.append(
            _spec_for_point(
                command,
                candidate_model,
                parameters.frequency_hz,
                needs_pattern=False,
                needs_sweep=False,
            )
        )

    assert specs[0].segmentation == specs[1].segmentation
    expected = aligned_policy_for_model(
        candidate_model,
        parameters.frequency_hz,
        SegmentationPolicy(min_segments_per_wire=3),
    )
    assert specs[0].segmentation == expected
