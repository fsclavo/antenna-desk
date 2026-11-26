# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build solver specifications for typed antenna families.

The builders are Qt-free and do not run the solver. They turn typed family
parameters into the ``SimulationSpec`` the solver adapter receives, including
the default sweep, segmentation, far-field sampling, transformer, and internal
matching context. The basic dipole, folded-dipole, and loop editors keep their
own sweep and reference-impedance controls and use their form spec instead.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..domain.antennas.beverage import BeverageParameters
from ..domain.antennas.biquad import BiquadParameters
from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.discone import DisconeParameters
from ..domain.antennas.endfed import (
    EndFedParameters,
    endfed_design_matching_network,
    endfed_matching_network,
    endfed_segmentation_overrides,
)
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.g5rv import G5RV_DIPOLE_ID
from ..domain.antennas.hexbeam import HexbeamParameters
from ..domain.antennas.inverted_l import InvertedLParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.j_pole import JPoleParameters
from ..domain.antennas.loaded_dipole import LoadedDipoleParameters
from ..domain.antennas.log_periodic import LogPeriodicParameters
from ..domain.antennas.magnetic_loop import MagneticLoopParameters
from ..domain.antennas.matching_network import MatchingNetworkOrigin
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.phased_vertical import PhasedVerticalParameters
from ..domain.antennas.quad_beam import QuadBeamParameters
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.scv import ScvParameters
from ..domain.antennas.stacked_yagi import (
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from ..domain.antennas.t2fd import (
    T2FD_DRIVEN_WIRE_ID,
    T2FD_TERMINATED_WIRE_ID,
    T2FDParameters,
)
from ..domain.antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ..domain.antennas.trap_dipole import TrapDipoleParameters
from ..domain.antennas.trap_yagi import TrapYagiParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters
from ..domain.antennas.zepp import ZEPP_BASE_ID, ZeppParameters
from ..domain.antennas.zs6bkw import ZS6BKW_DIPOLE_ID
from ..domain.simulation.frequency import FrequencyPlan
from ..domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_model,
    aligned_policy_for_wire_centers,
)
from ..domain.simulation.spec import (
    FeedNetworkKind,
    FeedNetworkSpec,
    SimulationSpec,
)
from .pattern_resolution import DEFAULT_PATTERN_STEP_DEG, far_field_request

DEFAULT_GENERATED_SWEEP_POINTS = 100
DEFAULT_TWO_BAND_SWEEP_POINTS = 100


@dataclass(frozen=True, slots=True)
class CustomSweepOptions:
    """The main-window custom sweep applied to a custom-wire design."""

    enabled: bool = False
    start_hz: float = 0.0
    stop_hz: float = 0.0
    points: int = DEFAULT_GENERATED_SWEEP_POINTS


@dataclass(frozen=True, slots=True)
class SimulationSpecContext:
    """User-selected sampling options shared by the family builders."""

    pattern_step_deg: float = DEFAULT_PATTERN_STEP_DEG
    custom_sweep: CustomSweepOptions = field(default_factory=CustomSweepOptions)
    active_hexbeam_band: str | None = None

    def __post_init__(self) -> None:
        if self.pattern_step_deg <= 0.0:
            raise ValueError("pattern step must be positive")


Builder = Callable[[Any, SimulationSpecContext], SimulationSpec]


def _ocfd_spec(parameters: OCFDParameters, context: SimulationSpecContext) -> SimulationSpec:
    model = parameters.to_antenna(name="OCFD")
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
        feed_transformer_ratio=parameters.transformer_ratio,
    )


def _vertical_spec(
    parameters: VerticalParameters, context: SimulationSpecContext
) -> SimulationSpec:
    model = parameters.to_antenna(name="Vertical")
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _inverted_v_spec(
    parameters: InvertedVParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna(name="Inverted V")
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _inverted_l_spec(
    parameters: InvertedLParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna(name="Inverted L")
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _magnetic_loop_spec(
    parameters: MagneticLoopParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna(name="Magnetic loop")
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.90,
            frequency_hz * 1.10,
            101,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.10,
            SegmentationPolicy(min_segments_per_wire=1),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _yagi_spec(parameters: YagiParameters, context: SimulationSpecContext) -> SimulationSpec:
    model = parameters.to_antenna(name="Yagi")
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=1),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
        feed_transformer_ratio=parameters.transformer_ratio,
    )


def _stacked_yagi_spec(
    parameters: StackedYagiParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.yagi.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=1),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.yagi.ground),
        feed_network_loss_db=(
            parameters.feed.splitter_loss_db
            if parameters.feed.mode
            in {StackedYagiFeedMode.PHASE_LINES, StackedYagiFeedMode.NETWORK}
            else 0.0
        ),
        feed_network_line_loss_db_per_100m=(
            parameters.feed.line_loss_db_per_100m
            if parameters.feed.mode is StackedYagiFeedMode.NETWORK
            else 0.0
        ),
        co_simulate_feed_network=(parameters.feed.mode is StackedYagiFeedMode.NETWORK),
        feed_network=(
            FeedNetworkSpec(
                kind=FeedNetworkKind.WILKINSON,
                design_frequency_hz=parameters.splitter_design_frequency_hz,
                port_count=parameters.count,
                feed_line_lengths_m=tuple(
                    parameters.feed.line_length_for_level(index)
                    for index in range(parameters.count)
                ),
                feed_line_impedance_ohm=parameters.feed.characteristic_impedance_ohm,
                velocity_factor=parameters.feed.velocity_factor,
                splitter_excess_loss_db=parameters.feed.splitter_loss_db,
                line_loss_db_per_100m=parameters.feed.line_loss_db_per_100m,
                level_matching_networks=parameters.feed.level_matching_networks,
                level_transformer_ratios=parameters.feed.level_transformer_ratios,
            )
            if parameters.feed.mode is StackedYagiFeedMode.WILKINSON
            else None
        ),
    )


def _moxon_spec(parameters: MoxonParameters, context: SimulationSpecContext) -> SimulationSpec:
    model = parameters.to_antenna(name="Moxon")
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _fan_dipole_spec(
    parameters: FanDipoleParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna(name="Fan dipole")
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _trap_dipole_spec(
    parameters: TrapDipoleParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna(name="Trap dipole")
    low_band_hz = parameters.frequency_hz
    high_band_hz = parameters.high_band_frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            low_band_hz * 0.95,
            high_band_hz * 1.05,
            DEFAULT_TWO_BAND_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            high_band_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _t2fd_spec(parameters: T2FDParameters, context: SimulationSpecContext) -> SimulationSpec:
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
    wire_segments = tuple(
        (
            wire.id,
            driven_count
            if wire.id in {T2FD_DRIVEN_WIRE_ID, T2FD_TERMINATED_WIRE_ID}
            else base.segments_for(wire, stop_hz),
        )
        for wire in model.wires
    )
    segmentation = SegmentationPolicy(
        min_segments_per_wire=3,
        wire_segments=wire_segments,
    )
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            parameters.frequency_hz,
            parameters.highest_frequency_hz,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=segmentation,
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
        feed_transformer_ratio=parameters.transformer_ratio,
    )


def _endfed_spec(parameters: EndFedParameters, context: SimulationSpecContext) -> SimulationSpec:
    model = parameters.to_antenna(name="End-fed")
    frequency_hz = parameters.frequency_hz
    matching_network = endfed_matching_network(parameters)
    design_matching = endfed_design_matching_network(parameters)
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(
                min_segments_per_wire=3,
                wire_segments=endfed_segmentation_overrides(parameters),
            ),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
        feed_transformer_ratio=parameters.transformer_ratio,
        transformer_loss=parameters.transformer_loss,
        matching_network=matching_network,
        matching_network_origin=(
            MatchingNetworkOrigin.DESIGN_ENDFED
            if design_matching is not None
            else (
                MatchingNetworkOrigin.INTERNAL_ENDFED
                if matching_network is not None
                else MatchingNetworkOrigin.NONE
            )
        ),
    )


def _j_pole_spec(parameters: JPoleParameters, context: SimulationSpecContext) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _ringo_spec(parameters: RingoParameters, context: SimulationSpecContext) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _scv_spec(parameters: ScvParameters, context: SimulationSpecContext) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _biquad_spec(parameters: BiquadParameters, context: SimulationSpecContext) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.9,
            frequency_hz * 1.1,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.1,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
        feed_transformer_ratio=parameters.transformer_ratio,
    )


def _beverage_spec(
    parameters: BeverageParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.9,
            frequency_hz * 1.1,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.1,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
        feed_transformer_ratio=parameters.transformer_ratio,
    )


def _loaded_dipole_spec(
    parameters: LoadedDipoleParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.85,
            frequency_hz * 1.15,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.15,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _phased_vertical_spec(
    parameters: PhasedVerticalParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.9,
            frequency_hz * 1.1,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.1,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _quad_beam_spec(
    parameters: QuadBeamParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.9,
            frequency_hz * 1.1,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.1,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
        feed_transformer_ratio=parameters.transformer_ratio,
    )


def _log_periodic_spec(
    parameters: LogPeriodicParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna()
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            parameters.frequency_low_hz,
            parameters.frequency_high_hz,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_wire_centers(
            model,
            parameters.frequency_high_hz,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        feed_transformer_ratio=parameters.feed_transformer_ratio,
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _discone_spec(parameters: DisconeParameters, context: SimulationSpecContext) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.5,
            frequency_hz * 1.5,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.5,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _trap_yagi_spec(
    parameters: TrapYagiParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.9,
            frequency_hz * 1.1,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.1,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _hexbeam_spec(parameters: HexbeamParameters, context: SimulationSpecContext) -> SimulationSpec:
    band = parameters.resolved_bands[0]
    active_band = context.active_hexbeam_band
    if active_band is not None:
        key = active_band.casefold()
        band = next(
            (item for item in parameters.resolved_bands if item.label.casefold() == key),
            band,
        )
    model = parameters.to_antenna(active_band=active_band)
    frequency_hz = band.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _doublet_spec(
    parameters: TransmissionLineDoubletParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _zepp_spec(parameters: ZeppParameters, context: SimulationSpecContext) -> SimulationSpec:
    model = parameters.to_antenna()
    frequency_hz = parameters.frequency_hz
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            frequency_hz * 0.95,
            frequency_hz * 1.05,
            DEFAULT_GENERATED_SWEEP_POINTS,
        ),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz * 1.05,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
    )


def _custom_spec(
    parameters: CustomAntennaParameters,
    context: SimulationSpecContext,
) -> SimulationSpec:
    model = parameters.to_antenna(name="Custom")
    sweep = context.custom_sweep
    if sweep.enabled:
        frequency_plan = FrequencyPlan.sweep(
            sweep.start_hz,
            sweep.stop_hz,
            sweep.points,
        )
    else:
        frequency_plan = FrequencyPlan.single(parameters.frequency_hz)
    segmentation = SegmentationPolicy(min_segments_per_wire=3)
    if parameters.generator_id in {"g5rv", "zs6bkw"}:
        dipole_id = G5RV_DIPOLE_ID if parameters.generator_id == "g5rv" else ZS6BKW_DIPOLE_ID
        dipole = model.wire_by_id(dipole_id)
        count = segmentation.segments_for(dipole, frequency_plan.stop_hz)
        if count % 2 == 0:
            count += 1
        segmentation = SegmentationPolicy(
            min_segments_per_wire=3,
            wire_segments=((dipole_id, count),),
        )
    elif parameters.generator_id == "zepp":
        # The base connector is a short source jumper; one segment keeps the
        # delta gap centered and avoids a spurious too-short warning.
        segmentation = SegmentationPolicy(
            min_segments_per_wire=1,
            wire_segments=((ZEPP_BASE_ID, 1),),
        )
    segmentation = aligned_policy_for_model(
        model,
        frequency_plan.stop_hz,
        segmentation,
    )
    return SimulationSpec(
        frequency_plan=frequency_plan,
        segmentation=segmentation,
        far_field=far_field_request(context.pattern_step_deg, parameters.ground),
        feed_transformer_ratio=parameters.feed_transformer_ratio,
    )


_BUILDERS: dict[type[object], Builder] = {
    OCFDParameters: _ocfd_spec,
    VerticalParameters: _vertical_spec,
    InvertedVParameters: _inverted_v_spec,
    InvertedLParameters: _inverted_l_spec,
    MagneticLoopParameters: _magnetic_loop_spec,
    YagiParameters: _yagi_spec,
    StackedYagiParameters: _stacked_yagi_spec,
    MoxonParameters: _moxon_spec,
    FanDipoleParameters: _fan_dipole_spec,
    TrapDipoleParameters: _trap_dipole_spec,
    T2FDParameters: _t2fd_spec,
    EndFedParameters: _endfed_spec,
    JPoleParameters: _j_pole_spec,
    RingoParameters: _ringo_spec,
    ScvParameters: _scv_spec,
    BiquadParameters: _biquad_spec,
    BeverageParameters: _beverage_spec,
    LoadedDipoleParameters: _loaded_dipole_spec,
    PhasedVerticalParameters: _phased_vertical_spec,
    QuadBeamParameters: _quad_beam_spec,
    LogPeriodicParameters: _log_periodic_spec,
    DisconeParameters: _discone_spec,
    TrapYagiParameters: _trap_yagi_spec,
    HexbeamParameters: _hexbeam_spec,
    TransmissionLineDoubletParameters: _doublet_spec,
    ZeppParameters: _zepp_spec,
    CustomAntennaParameters: _custom_spec,
}


def build_typed_family_simulation_spec(
    parameters: AntennaDesignParameters,
    *,
    pattern_step_deg: float = DEFAULT_PATTERN_STEP_DEG,
    custom_sweep: CustomSweepOptions | None = None,
    active_hexbeam_band: str | None = None,
) -> SimulationSpec:
    """Build the spec for a typed family outside the basic dipole forms."""

    builder = _BUILDERS.get(type(parameters))
    if builder is None:
        raise TypeError(
            f"no typed simulation-spec builder for {type(parameters).__name__}; "
            "use the basic form spec"
        )
    context = SimulationSpecContext(
        pattern_step_deg=pattern_step_deg,
        custom_sweep=custom_sweep if custom_sweep is not None else CustomSweepOptions(),
        active_hexbeam_band=active_hexbeam_band,
    )
    return builder(parameters, context)
