# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Estimated templates and generated families solved with the real engine."""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest
from nec2c_support import (
    estimated_family_parameters,
)

from antennadesk.domain.design import DesignIntent, LoopShape, estimate_intent
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationStatus
from antennadesk.domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_model,
)
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.solver import Nec2cSolver

NEC2C = os.environ.get("NEC2C")
pytestmark = [
    pytest.mark.solver,
    pytest.mark.science,
    pytest.mark.skipif(
        not NEC2C or not Path(NEC2C).is_file(),
        reason="NEC2C must point to a nec2c executable",
    ),
]


@pytest.mark.parametrize(
    ("antenna_type", "frequency_hz", "kwargs"),
    [
        ("wire_dipole", 7_100_000.0, {}),
        ("folded_dipole", 7_100_000.0, {}),
        ("loop", 7_100_000.0, {"loop_shape": LoopShape.QUAD}),
        ("vertical", 146_000_000.0, {"radial_count": 8}),
        ("inverted_v", 7_100_000.0, {"height_m": 20.0}),
        ("fan_dipole", 7_100_000.0, {"height_m": 20.0}),
        ("endfed", 7_100_000.0, {}),
        ("ocfd", 7_100_000.0, {}),
        ("j_pole", 146_000_000.0, {"folded": False}),
        ("j_pole", 146_000_000.0, {"folded": True}),
        ("ringo", 146_000_000.0, {}),
        ("yagi", 146_000_000.0, {"yagi_elements": 5}),
        ("moxon", 14_170_000.0, {}),
    ],
)
def test_every_estimator_produces_a_solvable_model(
    solver: Nec2cSolver,
    antenna_type: str,
    frequency_hz: float,
    kwargs: dict[str, object],
) -> None:
    estimate = estimate_intent(
        DesignIntent(frequency_hz=frequency_hz, antenna_type=antenna_type, **kwargs)
    )
    model = estimate.parameters.to_antenna()
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=FarFieldRequest(enabled=False),
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies
    assert math.isfinite(result.frequencies[0].impedance_ohm.real)
    assert math.isfinite(result.frequencies[0].impedance_ohm.imag)


def test_vertical_generator_produces_a_usable_sweep(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.25,
        radial_count=16,
        radial_length_m=5.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    model = parameters.to_custom_parameters().to_antenna(name="Vertical")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(7_000_000.0, 7_200_000.0, 5),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=19,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=73,
        ),
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 5
    assert all(frequency.impedance_ohm.real > 0.0 for frequency in result.frequencies)
    assert all(frequency.swr is not None for frequency in result.frequencies)
    assert result.max_total_gain_db is not None


def test_j_pole_defaults_to_a_ground_clear_base(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.j_pole import JPoleParameters

    parameters = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(145_000_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=19,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=73,
        ),
    )

    result = solver.run(parameters.to_antenna(), spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies
    assert result.max_total_gain_db is not None


def test_slim_jim_runs_with_the_feed_offset_above_the_base(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.antennas.j_pole import JPoleParameters

    parameters = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        base_height_m=0.25,
        folded=True,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(145_000_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
    )

    result = solver.run(parameters.to_antenna(), spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies
    assert result.frequencies[0].impedance_ohm.real > 0.0
    assert result.frequencies[0].swr is not None


def test_dl6wu_yagi_estimator_produces_a_runnable_model(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.design import DesignIntent, estimate_intent

    estimate = estimate_intent(
        DesignIntent(
            frequency_hz=144_000_000.0,
            antenna_type="yagi",
            height_m=10.0,
            yagi_elements=32,
        )
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(144_000_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=7),
        include_conductor_losses=False,
    )

    result = solver.run(estimate.parameters.to_antenna(), spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies
    assert result.frequencies[0].impedance_ohm.real > 0.0


def test_freshly_estimated_ground_mounted_vertical_completes(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.design import DesignIntent, VerticalForm, estimate_intent

    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    parameters = estimate_intent(
        DesignIntent(
            frequency_hz=7_100_000.0,
            antenna_type="vertical",
            vertical_form=VerticalForm.QUARTER_WAVE,
            radial_count=4,
            ground=ground,
        )
    ).parameters
    model = parameters.to_antenna(name="Estimated vertical")
    segmentation = aligned_policy_for_model(
        model,
        parameters.frequency_hz * 1.05,
        SegmentationPolicy(min_segments_per_wire=3),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
        segmentation=segmentation,
        far_field=FarFieldRequest(enabled=False),
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].impedance_ohm.real > 0.0
    assert any(diagnostic.code == "geometry.ground_clearance" for diagnostic in result.diagnostics)
    assert any(
        diagnostic.code == "geometry.ground_mounted_wires" for diagnostic in result.diagnostics
    )


def test_loaded_vertical_with_a_series_coil_solves(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=1.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=12e-6,
        loading_coil_resistance_ohm=0.5,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    model = parameters.to_antenna(name="Loaded vertical")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 1
    assert result.frequencies[0].impedance_ohm.real > 0.0


def test_trap_dipole_with_parallel_traps_solves_both_bands(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    parameters = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=10e-6,
        height_m=12.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    model = parameters.to_antenna(name="Trap dipole")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(7_100_000.0, 14_100_000.0, 2),
        segmentation=SegmentationPolicy(min_segments_per_wire=9),
        include_conductor_losses=False,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 2
    assert all(frequency.impedance_ohm.real > 0.0 for frequency in result.frequencies)


def test_g5rv_preset_with_geometry_line_solves(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.g5rv import g5rv_parameters

    parameters = g5rv_parameters(
        frequency_hz=14_100_000.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    model = parameters.to_antenna(name="G5RV")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(7_100_000.0, 21_100_000.0, 3),
        segmentation=SegmentationPolicy(min_segments_per_wire=9),
        include_conductor_losses=False,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 3
    assert "TL " in result.raw_input
    assert all(frequency.impedance_ohm.real > 0.0 for frequency in result.frequencies)


def test_zepp_preset_with_two_wire_stub_solves(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.zepp import ZEPP_BASE_ID, zepp_parameters

    parameters = zepp_parameters()
    model = parameters.to_antenna(name="Zepp")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(7_000_000.0, 14_300_000.0, 3),
        segmentation=SegmentationPolicy(
            target_segment_length_wavelengths=0.02,
            min_segments_per_wire=1,
            wire_segments=((ZEPP_BASE_ID, 1),),
        ),
        include_conductor_losses=False,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.raw_input.count("GW ") == 4
    assert "TL " not in result.raw_input
    assert len(result.frequencies) == 3
    assert all(frequency.impedance_ohm.real > 0.0 for frequency in result.frequencies)


def test_t2fd_default_design_completes_with_a_broadband_match(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.antennas.t2fd import (
        T2FD_DRIVEN_WIRE_ID,
        T2FD_TERMINATED_WIRE_ID,
        T2FDParameters,
        t2fd_starting_dimensions,
    )

    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    span_m, spacing_m = t2fd_starting_dimensions(3_500_000.0)
    parameters = T2FDParameters(
        frequency_hz=3_500_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=span_m,
        spacing_m=spacing_m,
        height_m=10.0,
        termination_resistance_ohm=800.0,
        transformer_ratio=16.0,
        ground=ground,
    )
    model = parameters.to_antenna(name="T2FD")
    stop_hz = parameters.highest_frequency_hz
    base = aligned_policy_for_model(
        model,
        stop_hz,
        SegmentationPolicy(min_segments_per_wire=3),
    )
    driven_count = base.segments_for(
        model.wire_by_id(T2FD_DRIVEN_WIRE_ID),
        stop_hz,
    )
    if driven_count % 2 == 0:
        driven_count += 1
    segmentation = SegmentationPolicy(
        min_segments_per_wire=3,
        wire_segments=tuple(
            (
                wire.id,
                driven_count
                if wire.id in {T2FD_DRIVEN_WIRE_ID, T2FD_TERMINATED_WIRE_ID}
                else base.segments_for(wire, stop_hz),
            )
            for wire in model.wires
        ),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 31),
        segmentation=segmentation,
        include_conductor_losses=True,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=10,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=37,
        ),
        feed_transformer_ratio=parameters.transformer_ratio,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 31
    assert any(diagnostic.code == "transformer.applied" for diagnostic in result.diagnostics)
    assert all(frequency.impedance_ohm.real > 0.0 for frequency in result.frequencies)
    assert all(frequency.swr is not None for frequency in result.frequencies)
    assert max(frequency.swr for frequency in result.frequencies) < 3.5
    assert all(
        frequency.realized_gain_db is not None and math.isfinite(frequency.realized_gain_db)
        for frequency in result.frequencies
    )
    assert len(result.raw_output) < 10 * 1024 * 1024


@pytest.mark.parametrize(
    ("key", "frequency_hz"),
    [
        ("wire_dipole", 1_800_000.0),
        ("wire_dipole", 28_500_000.0),
        ("folded_dipole", 7_100_000.0),
        ("loop", 1_800_000.0),
        ("vertical", 7_100_000.0),
        ("inverted_v", 1_800_000.0),
        ("inverted_v", 3_500_000.0),
        ("fan_dipole", 1_800_000.0),
        ("fan_dipole", 7_100_000.0),
        ("endfed", 7_100_000.0),
        ("endfed", 28_500_000.0),
        ("ocfd", 7_100_000.0),
        ("j_pole", 50_000_000.0),
        ("ringo", 29_000_000.0),
        ("yagi", 14_100_000.0),
        ("moxon", 14_100_000.0),
        ("trap_dipole", 7_100_000.0),
        ("t2fd", 3_500_000.0),
        ("t2fd", 14_100_000.0),
    ],
)
def test_estimated_families_solve_above_ground(
    solver: Nec2cSolver,
    key: str,
    frequency_hz: float,
) -> None:
    parameters = estimated_family_parameters(key, frequency_hz)
    model = parameters.to_antenna(name=key)
    min_z = min(point.z_m for wire in model.wires for point in (wire.start, wire.end))
    segmentation = aligned_policy_for_model(
        model,
        frequency_hz,
        SegmentationPolicy(min_segments_per_wire=3),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=segmentation,
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )

    result = solver.run(model, spec)

    assert min_z >= -1e-9, f"{key} has a wire below ground"
    assert result.status is SimulationStatus.COMPLETED
    assert math.isfinite(result.frequencies[0].impedance_ohm.real)
