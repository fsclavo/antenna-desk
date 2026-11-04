# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared models, specs, and segmentation for the nec2c test modules."""

from __future__ import annotations

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.design import AntennaDesignParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.g5rv import G5RV_DIPOLE_ID, g5rv_parameters
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.t2fd import T2FDParameters, t2fd_starting_dimensions
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.design import DesignIntent, LoopShape, estimate_intent
from antennadesk.domain.environment.environment import Environment
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_model,
)
from antennadesk.domain.simulation.spec import SimulationSpec


def manual_example1_model() -> AntennaModel:
    return DipoleParameters(
        frequency_hz=299_800_000.0,
        total_length_m=0.5,
        height_m=0.0,
        wire_radius_m=0.001,
    ).to_antenna(name="NEC-2 manual example 1")


def manual_example1_spec() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(299_800_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=7),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=180.0,
            theta_count=19,
            phi_count=1,
        ),
    )


def vertical_model(ground: GroundModel) -> AntennaModel:
    wire = Wire(
        id="radiator",
        start=Point3D(0.0, 0.0, 2.0),
        end=Point3D(0.0, 0.0, 7.0),
        radius_m=0.3,
        material=COPPER,
    )
    return AntennaModel(
        name="NEC-2 manual example 3",
        design_frequency_hz=30_000_000.0,
        wires=(wire,),
        feed=FeedPoint("radiator", 2.5),
        environment=Environment(ground=ground),
    )


def vertical_spec() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(30_000_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=9),
        extended_thin_wire_kernel=True,
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )


def multi_wire_spec(frequency_hz: float, reference_ohm: float) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=SegmentationPolicy(segments_per_wire=11),
        reference_impedance_ohm=reference_ohm,
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )


def g5rv_model_and_segmentation() -> tuple[AntennaModel, SegmentationPolicy, GroundModel]:
    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    parameters = g5rv_parameters(
        frequency_hz=14_100_000.0,
        ground=ground,
    )
    model = parameters.to_antenna(name="G5RV")
    stop_hz = 30_000_000.0
    base = SegmentationPolicy(min_segments_per_wire=3)
    dipole = model.wire_by_id(G5RV_DIPOLE_ID)
    count = base.segments_for(dipole, stop_hz)
    if count % 2 == 0:
        count += 1
    segmentation = aligned_policy_for_model(
        model,
        stop_hz,
        SegmentationPolicy(
            min_segments_per_wire=3,
            wire_segments=((G5RV_DIPOLE_ID, count),),
        ),
    )
    return model, segmentation, ground


def estimated_family_parameters(
    key: str,
    frequency_hz: float,
) -> AntennaDesignParameters:
    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    if key == "vertical":
        return estimate_intent(
            DesignIntent(
                frequency_hz=frequency_hz,
                antenna_type="vertical",
                vertical_form="quarter_wave",
                radial_count=4,
                ground=ground,
            )
        ).parameters
    if key == "loop":
        return estimate_intent(
            DesignIntent(
                frequency_hz=frequency_hz,
                antenna_type="loop",
                loop_shape=LoopShape.QUAD,
                ground=ground,
            )
        ).parameters
    if key == "fan_dipole":
        return estimate_intent(
            DesignIntent(
                frequency_hz=frequency_hz,
                antenna_type="fan_dipole",
                fan_bands_hz=(frequency_hz, frequency_hz * 2.0),
                ground=ground,
            )
        ).parameters
    if key == "endfed":
        return estimate_intent(
            DesignIntent(
                frequency_hz=frequency_hz,
                antenna_type="endfed",
                end_height_m=2.0,
                ground=ground,
            )
        ).parameters
    if key == "trap_dipole":
        return TrapDipoleParameters(
            frequency_hz=frequency_hz,
            high_band_frequency_hz=min(frequency_hz * 2.0, 60_000_000.0),
            inner_length_m=10.0,
            outer_length_m=5.0,
            trap_frequency_hz=min(frequency_hz * 2.0, 60_000_000.0),
            trap_inductance_h=10e-6,
            height_m=10.0,
            ground=ground,
        )
    if key == "t2fd":
        span_m, spacing_m = t2fd_starting_dimensions(frequency_hz)
        return T2FDParameters(
            frequency_hz=frequency_hz,
            highest_frequency_hz=max(frequency_hz * 2.0, 30_000_000.0),
            length_m=span_m,
            spacing_m=spacing_m,
            height_m=10.0,
            ground=ground,
        )
    return estimate_intent(
        DesignIntent(
            frequency_hz=frequency_hz,
            antenna_type=key,
            ground=ground,
        )
    ).parameters
