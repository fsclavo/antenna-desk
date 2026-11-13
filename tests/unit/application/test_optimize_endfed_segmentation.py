# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Callable

import pytest

from antennadesk.application.use_cases.optimize_antenna import (
    OptimizeAntenna,
    OptimizeAntennaCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.endfed import (
    ENDFED_FEED_SECTION_SEGMENTS,
    ENDFED_LOADING_COIL_SECTION_SEGMENTS,
    FEED_SECTION_ID,
    LOADING_COIL_SECTION_ID,
    EndFedParameters,
    EndFedPreset,
    endfed_matching_network,
    shortened_efhw_40_10_parameters,
    shortened_efhw_80_10_parameters,
)
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.descriptor import FamilyOptimizationObjective
from antennadesk.domain.optimization.engine import OptimizationBudget
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import FarFieldRequest, SimulationSpec


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
        del model, spec
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="capture", version="1")

    def run(self, model: AntennaModel, spec: SimulationSpec, **kwargs: object) -> SimulationResult:
        del model, kwargs
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


def _base_spec(parameters: EndFedParameters) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=FarFieldRequest(enabled=False),
        feed_transformer_ratio=parameters.transformer_ratio,
        matching_network=endfed_matching_network(parameters),
    )


@pytest.mark.parametrize(
    "factory",
    [shortened_efhw_80_10_parameters, shortened_efhw_40_10_parameters],
)
def test_shortened_endfed_optimizer_keeps_fixed_wire_partitions(
    factory: Callable[[], EndFedParameters],
) -> None:
    parameters = factory()
    descriptor = optimizer_availability(parameters).descriptor
    assert descriptor is not None
    assert descriptor.structural_segmentation is not None

    solver = CapturingSolver()
    locked = frozenset(
        {
            "feed_height_m",
            "end_height_m",
            "wire_radius_m",
            "transformer_ratio",
            "loading_coil_offset_m",
            "loading_coil_inductance_h",
        }
    )
    result = OptimizeAntenna(solver).execute(
        OptimizeAntennaCommand(
            descriptor=descriptor,
            base_spec=_base_spec(parameters),
            objective=FamilyOptimizationObjective.MIN_SWR,
            budget=OptimizationBudget(4, 4, patience=2),
            locked_variables=locked,
            seed=1,
        )
    )

    assert result.best_parameters is not None
    assert solver.specs
    for spec in solver.specs:
        counts = dict(spec.segmentation.wire_segments)
        assert counts[FEED_SECTION_ID] == ENDFED_FEED_SECTION_SEGMENTS
        assert counts[LOADING_COIL_SECTION_ID] == ENDFED_LOADING_COIL_SECTION_SEGMENTS


def test_standard_endfed_does_not_opt_into_structural_segmentation() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_section_length_m=0.5,
        transformer_ratio=49.0,
        preset=EndFedPreset.STANDARD,
    )
    descriptor = optimizer_availability(parameters).descriptor
    assert descriptor is not None
    assert descriptor.structural_segmentation is None


def test_other_families_do_not_opt_into_structural_segmentation() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=10.0,
    )
    descriptor = optimizer_availability(parameters).descriptor
    assert descriptor is not None
    assert descriptor.structural_segmentation is None
