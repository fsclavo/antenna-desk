# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Target-frequency scoring, robust scope, and segmentation consistency."""

from __future__ import annotations

from dataclasses import replace

import pytest

from antennadesk.application.ports.antenna_solver import ProgressCallback
from antennadesk.application.ports.cancellation import CancelToken
from antennadesk.application.simulation_specs import build_typed_family_simulation_spec
from antennadesk.application.use_cases.optimize_antenna import (
    OptimizeAntenna,
    OptimizeAntennaCommand,
    _single_metrics,
    _spec_for_point,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.hexbeam import published_hexbeam_multiband_parameters
from antennadesk.domain.antennas.matching_network import design_l_network
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.stacked_yagi import (
    StackedYagiFeed,
    StackedYagiFeedMode,
    stacked_yagi_parameters,
)
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
        self.transformer_ratios: list[float] = []
        self.feed_wire_ids: list[str] = []
        self.wire_ids: list[set[str]] = []
        self.feed_line_lengths: list[tuple[float, ...]] = []

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
        self.transformer_ratios.append(spec.feed_transformer_ratio)
        self.feed_wire_ids.append(model.feed.wire_id)
        self.wire_ids.append({wire.id for wire in model.wires})
        self.feed_line_lengths.append(
            spec.feed_network.feed_line_lengths_m if spec.feed_network is not None else ()
        )
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


def test_single_metrics_applies_the_candidate_transformer_ratio() -> None:
    solver = RecordingSolver()
    parameters = replace(_parameters(), transformer_ratio=6.0)
    command = _command(parameters)

    metrics = _single_metrics(
        command,
        solver,
        parameters,
        needs_pattern=False,
        needs_sweep=False,
    )

    assert solver.transformer_ratios == [6.0]
    assert metrics["target_error_ohm"] == 0.0


def test_single_metrics_uses_the_hexbeam_selected_band_model_and_frequency() -> None:
    parameters = published_hexbeam_multiband_parameters(labels=("20m", "15m", "10m"))
    band = parameters.bands[1]
    availability = optimizer_availability(parameters, hexbeam_band="15m")
    assert availability.descriptor is not None
    solver = RecordingSolver()
    command = OptimizeAntennaCommand(
        descriptor=availability.descriptor,
        base_spec=SimulationSpec(frequency_plan=FrequencyPlan.single(band.frequency_hz)),
        objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
        budget=OptimizationBudget(4, 4, 2),
    )

    _single_metrics(
        command,
        solver,
        parameters,
        needs_pattern=False,
        needs_sweep=False,
    )

    assert solver.frequencies == [pytest.approx(band.frequency_hz)]
    assert solver.feed_wire_ids == ["hexbeam-band2-feed"]
    assert "hexbeam-feed" in solver.wire_ids[0]
    assert "hexbeam-band3-feed" in solver.wire_ids[0]


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


def test_candidate_spec_builder_rebuilds_the_wilkinson_feed_network() -> None:
    matching = design_l_network(100.0 + 0.0j, 14_100_000.0, source_impedance_ohm=50.0)
    assert matching is not None
    parameters = stacked_yagi_parameters(
        frequency_hz=14_100_000.0,
        count=2,
        height_m=10.0,
        spacing_m=10.6,
        max_top_height_m=30.0,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.WILKINSON,
            reference_length_m=2.0,
            line_increment_m=1.0,
            velocity_factor=0.8,
            characteristic_impedance_ohm=50.0,
            splitter_design_frequency_hz=14_100_000.0,
            level_matching_networks=(matching, matching),
        ),
    )
    candidate = replace(
        parameters,
        feed=replace(parameters.feed, line_increment_m=2.0),
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    command = OptimizeAntennaCommand(
        descriptor=availability.descriptor,
        base_spec=build_typed_family_simulation_spec(parameters),
        objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
        budget=OptimizationBudget(4, 4, 2),
        candidate_spec_builder=build_typed_family_simulation_spec,
    )
    solver = RecordingSolver()

    _single_metrics(
        command,
        solver,
        candidate,
        needs_pattern=False,
        needs_sweep=False,
    )

    assert solver.feed_line_lengths == [(2.0, 4.0)]


def test_wilkinson_optimizer_rebuilds_the_feed_network_for_each_candidate() -> None:
    matching = design_l_network(100.0 + 0.0j, 14_100_000.0, source_impedance_ohm=50.0)
    assert matching is not None
    parameters = stacked_yagi_parameters(
        frequency_hz=14_100_000.0,
        count=2,
        height_m=10.0,
        spacing_m=10.6,
        max_top_height_m=30.0,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.WILKINSON,
            reference_length_m=2.0,
            line_increment_m=1.0,
            velocity_factor=0.8,
            characteristic_impedance_ohm=50.0,
            splitter_design_frequency_hz=14_100_000.0,
            level_matching_networks=(matching, matching),
        ),
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    solver = RecordingSolver()
    command = OptimizeAntennaCommand(
        descriptor=availability.descriptor,
        base_spec=build_typed_family_simulation_spec(parameters),
        objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
        budget=OptimizationBudget(4, 4, 2),
        locked_variables=frozenset({"spacing_m", "amplitude_ratio", "count", "max_top_height_m"}),
        candidate_spec_builder=build_typed_family_simulation_spec,
    )

    result = OptimizeAntenna(solver).execute(command)

    assert result.status is not OptimizationStatus.ERROR
    assert solver.feed_line_lengths
    assert len(set(solver.feed_line_lengths)) > 1
