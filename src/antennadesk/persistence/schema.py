# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pydantic schema and domain mapping for native project files."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.balun import BalunLoss
from ..domain.antennas.beverage import ANTENNA_TYPE_BEVERAGE, BeverageParameters
from ..domain.antennas.biquad import (
    ANTENNA_TYPE_BIQUAD,
    ANTENNA_TYPE_DOUBLE_BIQUAD,
    BiquadKind,
    BiquadParameters,
)
from ..domain.antennas.custom import ANTENNA_TYPE_CUSTOM, CustomAntennaParameters
from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.dipole import (
    ANTENNA_TYPE_WIRE_DIPOLE,
    DipoleOrientation,
    DipoleParameters,
)
from ..domain.antennas.discone import ANTENNA_TYPE_DISCONE, DisconeParameters
from ..domain.antennas.endfed import (
    ANTENNA_TYPE_ENDFED,
    EndFedParameters,
    EndFedPreset,
)
from ..domain.antennas.fan_dipole import (
    ANTENNA_TYPE_FAN_DIPOLE,
    FanDipoleParameters,
    FanElement,
)
from ..domain.antennas.feed import FeedPoint, Source
from ..domain.antennas.feed_line import FeedLine
from ..domain.antennas.folded_dipole import (
    ANTENNA_TYPE_FOLDED_DIPOLE,
    FoldedDipoleParameters,
)
from ..domain.antennas.geometry import Point3D
from ..domain.antennas.hexbeam import ANTENNA_TYPE_HEXBEAM, HexbeamParameters
from ..domain.antennas.inverted_l import ANTENNA_TYPE_INVERTED_L, InvertedLParameters
from ..domain.antennas.inverted_v import ANTENNA_TYPE_INVERTED_V, InvertedVParameters
from ..domain.antennas.j_pole import ANTENNA_TYPE_J_POLE, JPoleParameters
from ..domain.antennas.load import LoadKind, LumpedLoad, ParallelLoad, SeriesLoad
from ..domain.antennas.loaded_dipole import (
    ANTENNA_TYPE_LOADED_DIPOLE,
    LoadedDipoleParameters,
)
from ..domain.antennas.loop import (
    ANTENNA_TYPE_LOOP,
    MAX_SIDES,
    MIN_SIDES,
    LoopOrientation,
    LoopParameters,
)
from ..domain.antennas.magnetic_loop import (
    ANTENNA_TYPE_MAGNETIC_LOOP,
    MagneticLoopParameters,
)
from ..domain.antennas.matching_network import LNetwork, MatchingNetwork, PiNetwork, TNetwork
from ..domain.antennas.materials import ConductorMaterial
from ..domain.antennas.moxon import ANTENNA_TYPE_MOXON, MoxonParameters
from ..domain.antennas.ocfd import ANTENNA_TYPE_OCFD, OCFDParameters
from ..domain.antennas.phased_vertical import (
    ANTENNA_TYPE_PHASED_VERTICAL,
    PhasedVerticalParameters,
)
from ..domain.antennas.polarization import Polarization
from ..domain.antennas.quad_beam import ANTENNA_TYPE_QUAD_BEAM, QuadBeamParameters
from ..domain.antennas.ringo import ANTENNA_TYPE_RINGO, RingoParameters
from ..domain.antennas.scv import (
    ANTENNA_TYPE_BOBTAIL_CURTAIN,
    ANTENNA_TYPE_HALF_SQUARE,
    ScvKind,
    ScvParameters,
)
from ..domain.antennas.t2fd import ANTENNA_TYPE_T2FD, T2FDParameters
from ..domain.antennas.transmission_line import TransmissionLine
from ..domain.antennas.transmission_line_doublet import (
    ANTENNA_TYPE_G5RV,
    ANTENNA_TYPE_ZS6BKW,
    DoubletPreset,
    TransmissionLineDoubletParameters,
)
from ..domain.antennas.trap_dipole import (
    ANTENNA_TYPE_TRAP_DIPOLE,
    TrapDipoleParameters,
)
from ..domain.antennas.trap_yagi import (
    ANTENNA_TYPE_TRAP_YAGI,
    TrapYagiParameters,
)
from ..domain.antennas.vertical import ANTENNA_TYPE_VERTICAL, VerticalParameters
from ..domain.antennas.wire import Wire
from ..domain.antennas.yagi import (
    ANTENNA_TYPE_YAGI,
    YagiElement,
    YagiMatchType,
    YagiParameters,
)
from ..domain.antennas.zepp import ANTENNA_TYPE_ZEPP, ZeppParameters
from ..domain.common.validation import Diagnostic, Severity
from ..domain.design.band_plan import BandPlan, BandSelection
from ..domain.environment.environment import Environment
from ..domain.environment.ground import GroundKind, GroundModel
from ..domain.measurement import Measurement, MeasurementPoint
from ..domain.optimization.summary import (
    OptimizationMode,
    OptimizationRecommendation,
    OptimizationSummary,
    RecommendationSeverity,
)
from ..domain.projects.project import DesignProvenance, DesignVariant, Project
from ..domain.simulation.bands import amateur_band_by_id
from ..domain.simulation.far_field import FarFieldRequest
from ..domain.simulation.frequency import FrequencyPlan
from ..domain.simulation.result import (
    CurrentSample,
    FarFieldPoint,
    FrequencyResult,
    PowerBudget,
    SimulationResult,
    SimulationStatus,
    SourceResult,
)
from ..domain.simulation.run import SimulationRun
from ..domain.simulation.segmentation import SegmentationPolicy
from ..domain.simulation.solver import SolverMetadata
from ..domain.simulation.spec import SimulationSpec
from .constants import PROJECT_FORMAT, SCHEMA_VERSION


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


class PointPayload(StrictModel):
    x_m: float
    y_m: float
    z_m: float


class MaterialPayload(StrictModel):
    name: str = Field(min_length=1)
    conductivity_s_per_m: float = Field(gt=0.0)
    relative_permeability: float = Field(default=1.0, gt=0.0)


class WirePayload(StrictModel):
    id: str = Field(min_length=1)
    start: PointPayload
    end: PointPayload
    radius_m: float = Field(gt=0.0)
    material: MaterialPayload


class FeedPayload(StrictModel):
    wire_id: str = Field(min_length=1)
    offset_m: float = Field(ge=0.0)


class SourcePayload(StrictModel):
    wire_id: str = Field(min_length=1)
    offset_m: float = Field(ge=0.0)
    amplitude: float = Field(default=1.0, gt=0.0)
    phase_deg: float = Field(default=0.0)


class GroundPayload(StrictModel):
    kind: GroundKind
    relative_permittivity: float | None = Field(default=None, ge=1.0)
    conductivity_s_per_m: float | None = Field(default=None, gt=0.0)

    @model_validator(mode="after")
    def _validate_parameters(self) -> Self:
        if self.kind is GroundKind.FINITE:
            if self.relative_permittivity is None or self.conductivity_s_per_m is None:
                raise ValueError(
                    "finite ground requires relative_permittivity and conductivity_s_per_m"
                )
        elif self.relative_permittivity is not None or self.conductivity_s_per_m is not None:
            raise ValueError(f"{self.kind.value} ground does not accept electrical parameters")
        return self


class EnvironmentPayload(StrictModel):
    ground: GroundPayload


class LoadPayload(StrictModel):
    id: str = Field(min_length=1)
    wire_id: str = Field(min_length=1)
    offset_m: float = Field(ge=0.0)
    kind: LoadKind = LoadKind.SERIES
    resistance_ohm: float = Field(default=0.0, ge=0.0)
    inductance_h: float = Field(default=0.0, ge=0.0)
    capacitance_f: float = Field(default=0.0, ge=0.0)


class TransmissionLinePayload(StrictModel):
    id: str = Field(min_length=1)
    start_wire_id: str = Field(min_length=1)
    start_offset_m: float = Field(ge=0.0)
    end_wire_id: str = Field(min_length=1)
    end_offset_m: float = Field(ge=0.0)
    characteristic_impedance_ohm: float = Field(gt=0.0)
    length_m: float = Field(gt=0.0)
    velocity_factor: float = Field(default=1.0, gt=0.0, le=1.0)


class AntennaPayload(StrictModel):
    name: str = Field(min_length=1)
    design_frequency_hz: float = Field(gt=0.0)
    wires: list[WirePayload] = Field(min_length=1)
    feed: FeedPayload
    environment: EnvironmentPayload
    loads: list[LoadPayload] = Field(default_factory=list)
    transmission_lines: list[TransmissionLinePayload] = Field(default_factory=list)
    sources: list[SourcePayload] = Field(default_factory=list)


class DipoleParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    total_length_m: float = Field(gt=0.0)
    height_m: float = Field(ge=0.0)
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    sag_m: float = Field(default=0.0, ge=0.0)
    material: MaterialPayload
    ground: GroundPayload


class FoldedDipoleParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    total_length_m: float = Field(gt=0.0)
    height_m: float = Field(ge=0.0)
    spacing_m: float = Field(gt=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class LoopParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    circumference_m: float = Field(gt=0.0)
    height_m: float = Field(ge=0.0)
    sides: int = Field(default=16, ge=MIN_SIDES, le=MAX_SIDES)
    orientation: LoopOrientation = LoopOrientation.VERTICAL
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class MagneticLoopParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    diameter_m: float = Field(gt=0.0)
    tuning_capacitance_f: float = Field(default=200e-12, gt=0.0)
    height_m: float = Field(default=1.0, ge=0.0)
    sides: int = Field(default=36, ge=8, le=128, multiple_of=2)
    gap_length_m: float = Field(default=0.05, gt=0.0)
    capacitor_esr_ohm: float = Field(default=0.0, ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.005, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class OCFDParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    total_length_m: float = Field(gt=0.0)
    feed_ratio: float = Field(default=1.0 / 3.0, gt=0.0, lt=1.0)
    height_m: float = Field(default=10.0, ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload
    transformer_ratio: float = Field(default=1.0, gt=0.0)


class RingoParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    radiator_height_m: float = Field(gt=0.0)
    ring_diameter_m: float = Field(gt=0.0)
    ring_height_m: float = Field(default=0.0, ge=0.0)
    ring_sides: int = Field(default=16, ge=3, le=128)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class BiquadParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    loop_side_m: float = Field(gt=0.0)
    reflector_spacing_m: float = Field(gt=0.0)
    kind: BiquadKind = BiquadKind.SINGLE
    base_height_m: float = Field(default=1.0, ge=0.0)
    reflector_enabled: bool = True
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class BeverageParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    length_m: float = Field(gt=0.0)
    height_m: float = Field(default=3.0, gt=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    termination_enabled: bool = True
    termination_resistance_ohm: float = Field(default=500.0, gt=0.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class ScvParametersPayload(StrictModel):
    kind: ScvKind
    frequency_hz: float = Field(gt=0.0)
    horizontal_length_m: float = Field(gt=0.0)
    vertical_height_m: float = Field(gt=0.0)
    base_height_m: float = Field(default=2.5, ge=0.0)
    feed_offset_m: float = Field(default=0.0, ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class TrapDipoleParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    high_band_frequency_hz: float = Field(gt=0.0)
    inner_length_m: float = Field(gt=0.0)
    outer_length_m: float = Field(gt=0.0)
    trap_frequency_hz: float = Field(gt=0.0)
    trap_inductance_h: float = Field(gt=0.0)
    height_m: float = Field(default=10.0, ge=0.0)
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class TrapYagiParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    high_band_frequency_hz: float = Field(gt=0.0)
    driven_length_m: float = Field(gt=0.0)
    reflector_spacing_m: float = Field(gt=0.0)
    trap_inset_m: float = Field(gt=0.0)
    trap_frequency_hz: float = Field(gt=0.0)
    trap_inductance_h: float = Field(gt=0.0)
    element_count: int = Field(default=3, ge=2, le=3)
    director_spacing_m: float = Field(default=0.0, ge=0.0)
    reflector_scale: float = Field(default=1.05, ge=1.0, le=1.2)
    director_scale: float = Field(default=0.95, ge=0.8, le=1.0)
    height_m: float = Field(default=10.0, ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class T2FDParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    highest_frequency_hz: float = Field(gt=0.0)
    length_m: float = Field(gt=0.0)
    spacing_m: float = Field(gt=0.0)
    height_m: float = Field(default=10.0, ge=0.0)
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL
    termination_resistance_ohm: float = Field(default=800.0, gt=0.0)
    transformer_ratio: float = Field(default=16.0, gt=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class TransmissionLineDoubletParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    preset: DoubletPreset
    dipole_total_length_m: float = Field(gt=0.0)
    height_m: float = Field(default=10.0, ge=0.0)
    feed_height_m: float = Field(default=1.0, ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    line_impedance_ohm: float = Field(default=450.0, gt=0.0)
    line_length_m: float = Field(default=10.36, gt=0.0)
    line_velocity_factor: float = Field(default=1.0, gt=0.0, le=1.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class ZeppParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    radiator_length_m: float = Field(gt=0.0)
    matching_section_length_m: float = Field(gt=0.0)
    spacing_m: float = Field(default=0.05, gt=0.0)
    base_height_m: float = Field(default=1.0, ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class HexbeamParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    driver_half_length_m: float = Field(gt=0.0)
    reflector_half_length_m: float = Field(gt=0.0)
    turning_radius_m: float = Field(gt=0.0)
    tip_gap_m: float = Field(gt=0.0)
    height_m: float = Field(default=10.0, ge=0.0)
    feed_gap_m: float = Field(default=0.03175, gt=0.0)
    element_separation_m: float = Field(default=0.05, ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class DisconeParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    cone_height_m: float = Field(gt=0.0)
    cone_radius_m: float = Field(gt=0.0)
    disc_radius_m: float = Field(gt=0.0)
    base_height_m: float = Field(default=0.5, ge=0.0)
    disc_gap_m: float = Field(default=0.01, gt=0.0)
    wire_count: int = Field(default=12, ge=4, le=32)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class PhasedVerticalParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    height_m: float = Field(gt=0.0)
    spacing_m: float = Field(gt=0.0)
    element_count: int = Field(default=2, ge=2, le=4)
    base_height_m: float = Field(default=0.25, ge=0.0)
    phase_step_deg: float = Field(default=0.0, ge=-360.0, le=360.0)
    amplitude_taper: float = Field(default=0.0, ge=0.0, le=0.9)
    radial_count: int = Field(default=4, ge=0, le=36)
    radial_length_m: float = Field(default=0.0, ge=0.0)
    radial_angle_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class QuadBeamParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    loop_side_m: float = Field(gt=0.0)
    reflector_spacing_m: float = Field(gt=0.0)
    height_m: float = Field(ge=0.0)
    element_count: int = Field(default=2, ge=2, le=3)
    director_spacing_m: float = Field(default=0.0, ge=0.0)
    reflector_scale: float = Field(default=1.05, ge=1.0, le=1.2)
    director_scale: float = Field(default=0.95, ge=0.8, le=1.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class LoadedDipoleParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    total_length_m: float = Field(gt=0.0)
    height_m: float = Field(default=10.0, ge=0.0)
    link_offset_m: float = Field(default=2.0, gt=0.0)
    link_open: bool = False
    loading_coil_enabled: bool = True
    loading_coil_inductance_h: float = Field(default=10e-6, ge=0.0)
    loading_coil_resistance_ohm: float = Field(default=0.5, ge=0.0)
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class JPoleParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    radiator_height_m: float = Field(gt=0.0)
    stub_length_m: float = Field(gt=0.0)
    spacing_m: float = Field(gt=0.0)
    feed_offset_m: float = Field(default=0.1, ge=0.0)
    gap_m: float = Field(default=0.01, ge=0.0)
    base_height_m: float = Field(default=0.25, ge=0.0)
    folded: bool = False
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class InvertedVParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    leg_length_m: float = Field(gt=0.0)
    apex_height_m: float = Field(ge=0.0)
    included_angle_deg: float = Field(default=120.0, gt=0.0, lt=180.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class InvertedLParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    vertical_height_m: float = Field(gt=0.0)
    horizontal_length_m: float = Field(gt=0.0)
    base_height_m: float = Field(default=0.0, ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class VerticalParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    height_m: float = Field(gt=0.0)
    base_height_m: float = Field(default=0.0, ge=0.0)
    radial_count: int = Field(default=0, ge=0, le=128)
    radial_length_m: float = Field(default=0.0, ge=0.0)
    radial_angle_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload
    loading_coil_enabled: bool = False
    loading_coil_offset_m: float = Field(default=0.0, ge=0.0)
    loading_coil_inductance_h: float = Field(default=0.0, ge=0.0)
    loading_coil_resistance_ohm: float = Field(default=0.0, ge=0.0)
    top_hat_enabled: bool = False
    top_hat_radius_m: float = Field(default=0.0, ge=0.0)
    top_hat_wire_count: int = Field(default=0, ge=0, le=32)


class EndFedParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    length_m: float = Field(gt=0.0)
    feed_height_m: float = Field(default=10.0, ge=0.0)
    end_height_m: float = Field(default=10.0, ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload
    transformer_ratio: float = Field(default=1.0, gt=0.0)
    counterpoise_length_m: float = Field(default=0.0, ge=0.0)
    counterpoise_height_m: float = Field(default=0.1, ge=0.0)
    counterpoise_azimuth_deg: float | None = Field(default=None, ge=0.0, lt=360.0)
    loading_coil_enabled: bool = False
    loading_coil_offset_m: float = Field(default=0.0, ge=0.0)
    loading_coil_inductance_h: float = Field(default=0.0, ge=0.0)
    loading_coil_resistance_ohm: float = Field(default=0.0, ge=0.0)
    preset: EndFedPreset = EndFedPreset.STANDARD


class FanElementPayload(StrictModel):
    length_m: float = Field(gt=0.0)
    included_angle_deg: float = Field(default=120.0, gt=0.0, le=180.0)


class FanDipoleParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    elements: list[FanElementPayload] = Field(min_length=1)
    apex_height_m: float = Field(ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class MoxonParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    width_m: float = Field(gt=0.0)
    depth_m: float = Field(gt=0.0)
    reflector_tip_m: float = Field(gt=0.0)
    driven_tip_m: float = Field(gt=0.0)
    height_m: float = Field(default=10.0, ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    polarization: Polarization = Polarization.HORIZONTAL
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class YagiElementPayload(StrictModel):
    position_m: float = Field(ge=0.0)
    length_m: float = Field(gt=0.0)
    radius_m: float = Field(gt=0.0)


class YagiParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    elements: list[YagiElementPayload] = Field(min_length=2)
    height_m: float = Field(ge=0.0)
    taper_tip_length_m: float = Field(default=0.0, ge=0.0)
    taper_tip_radius_m: float = Field(default=0.0, ge=0.0)
    driven_index: int = Field(default=1, ge=0)
    driven_folded: bool = False
    driven_fold_spacing_m: float = Field(default=0.1, ge=0.0)
    match_type: YagiMatchType = YagiMatchType.NONE
    match_length_m: float = Field(default=0.2, gt=0.0)
    match_spacing_m: float = Field(default=0.1, gt=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    polarization: Polarization = Polarization.HORIZONTAL
    material: MaterialPayload
    ground: GroundPayload


class CustomParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    wires: list[WirePayload] = Field(min_length=1)
    feed: FeedPayload
    ground: GroundPayload
    loads: list[LoadPayload] = Field(default_factory=list)
    transmission_lines: list[TransmissionLinePayload] = Field(default_factory=list)
    generator_id: str | None = Field(default=None, min_length=1)
    generator_name: str | None = Field(default=None, min_length=1)
    feed_transformer_ratio: float = Field(default=1.0, gt=0.0)


class FrequencyPlanPayload(StrictModel):
    start_hz: float = Field(gt=0.0)
    stop_hz: float = Field(gt=0.0)
    count: int = Field(ge=1, le=10_000)


class WireSegmentsPayload(StrictModel):
    wire_id: str = Field(min_length=1)
    segments: int = Field(ge=1)


class SegmentationPolicyPayload(StrictModel):
    segments_per_wire: int | None = Field(default=None, ge=1)
    target_segment_length_wavelengths: float = Field(default=0.02, gt=0.0)
    min_segments_per_wire: int = Field(default=1, ge=1)
    max_segments_per_wire: int = Field(default=1_000, ge=1)
    wire_segments: list[WireSegmentsPayload] = Field(default_factory=list)


class FeedLinePayload(StrictModel):
    characteristic_impedance_ohm: float = Field(default=50.0, gt=0.0)
    length_m: float = Field(default=0.0, ge=0.0)
    velocity_factor: float = Field(default=1.0, gt=0.0, le=1.0)
    matched_loss_db_per_100m: float = Field(default=0.0, ge=0.0)


class BalunLossPayload(StrictModel):
    enabled: bool = True
    reference_frequency_hz: float = Field(default=7_000_000.0, gt=0.0)
    reference_loss_db: float = Field(default=0.5, ge=0.0)
    exponent: float = Field(default=0.5, ge=0.0)


class LNetworkPayload(StrictModel):
    topology: Literal["l", "pi", "t"] = "l"
    series_inductance_h: float = Field(default=0.0, ge=0.0)
    series_capacitance_f: float = Field(default=0.0, ge=0.0)
    shunt_inductance_h: float = Field(default=0.0, ge=0.0)
    shunt_capacitance_f: float = Field(default=0.0, ge=0.0)
    shunt_at_input: bool = False
    input_shunt_inductance_h: float = Field(default=0.0, ge=0.0)
    input_shunt_capacitance_f: float = Field(default=0.0, ge=0.0)
    output_shunt_inductance_h: float = Field(default=0.0, ge=0.0)
    output_shunt_capacitance_f: float = Field(default=0.0, ge=0.0)
    input_series_inductance_h: float = Field(default=0.0, ge=0.0)
    input_series_capacitance_f: float = Field(default=0.0, ge=0.0)
    output_series_inductance_h: float = Field(default=0.0, ge=0.0)
    output_series_capacitance_f: float = Field(default=0.0, ge=0.0)
    q_factor: float | None = Field(default=None, gt=0.0)


class FarFieldRequestPayload(StrictModel):
    enabled: bool = True
    theta_start_deg: float = 0.0
    theta_stop_deg: float = 180.0
    theta_count: int = Field(default=19, ge=1, le=1_000)
    phi_start_deg: float = 0.0
    phi_stop_deg: float = 0.0
    phi_count: int = Field(default=1, ge=1, le=1_000)


class SimulationSpecPayload(StrictModel):
    frequency_plan: FrequencyPlanPayload
    segmentation: SegmentationPolicyPayload = Field(default_factory=SegmentationPolicyPayload)
    reference_impedance_ohm: float = Field(default=50.0, gt=0.0)
    extended_thin_wire_kernel: bool = False
    include_conductor_losses: bool = True
    far_field: FarFieldRequestPayload = Field(default_factory=FarFieldRequestPayload)
    pattern_frequencies_hz: list[float] = Field(default_factory=list)
    feed_line: FeedLinePayload | None = None
    matching_network: LNetworkPayload | None = None
    balun_loss: BalunLossPayload | None = None
    feed_transformer_ratio: float = Field(default=1.0, gt=0.0)
    timeout_s: float = Field(default=60.0, gt=0.0)


class SolverMetadataPayload(StrictModel):
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    executable: str | None = None


class DiagnosticPayload(StrictModel):
    code: str = Field(min_length=1)
    severity: Severity
    message: str = Field(min_length=1)
    field: str | None = None


class PowerBudgetPayload(StrictModel):
    input_w: float
    radiated_w: float
    structure_loss_w: float
    network_loss_w: float
    efficiency_percent: float


class CurrentSamplePayload(StrictModel):
    segment: int
    tag: int
    x_m: float
    y_m: float
    z_m: float
    length_m: float
    current_real_a: float
    current_imag_a: float
    magnitude_a: float
    phase_deg: float


class FarFieldPointPayload(StrictModel):
    theta_deg: float
    phi_deg: float
    gain_vertical_db: float | None = None
    gain_horizontal_db: float | None = None
    gain_total_db: float | None = None
    axial_ratio: float
    tilt_deg: float
    polarization: str | None = None
    e_theta_magnitude_v_per_m: float | None = None
    e_theta_phase_deg: float | None = None
    e_phi_magnitude_v_per_m: float | None = None
    e_phi_phase_deg: float | None = None


class SourceResultPayload(StrictModel):
    wire_id: str = Field(min_length=1)
    offset_m: float = Field(ge=0.0)
    tag: int = Field(ge=1)
    segment: int = Field(ge=1)
    amplitude: float = Field(gt=0.0)
    phase_deg: float
    voltage_real_v: float
    voltage_imag_v: float
    current_real_a: float
    current_imag_a: float
    impedance_real_ohm: float
    impedance_imag_ohm: float
    power_w: float


class FrequencyResultPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    feed_tag: int
    feed_segment: int
    impedance_real_ohm: float
    impedance_imag_ohm: float
    swr: float | None = None
    input_power_w: float
    currents: list[CurrentSamplePayload] = Field(default_factory=list)
    far_field: list[FarFieldPointPayload] = Field(default_factory=list)
    source_results: list[SourceResultPayload] = Field(default_factory=list)
    power_budget: PowerBudgetPayload | None = None
    directivity_db: float | None = None
    realized_gain_db: float | None = None
    mismatch_loss_db: float | None = None
    feed_line_loss_db: float | None = None
    network_loss_db: float | None = None
    balun_loss_db: float | None = None


class SimulationResultPayload(StrictModel):
    status: SimulationStatus
    spec: SimulationSpecPayload
    model_fingerprint: str = Field(min_length=1)
    solver: SolverMetadataPayload
    frequencies: list[FrequencyResultPayload] = Field(default_factory=list)
    diagnostics: list[DiagnosticPayload] = Field(default_factory=list)
    raw_input: str = ""
    raw_output: str = ""
    stderr: str = ""
    duration_s: float = 0.0
    started_at: datetime | None = None
    finished_at: datetime | None = None


class MeasurementPointPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    impedance_real_ohm: float
    impedance_imag_ohm: float


class MeasurementPayload(StrictModel):
    id: UUID
    name: str = Field(min_length=1)
    created_at: datetime
    reference_impedance_ohm: float = Field(gt=0.0)
    points: list[MeasurementPointPayload] = Field(min_length=1)
    source: str = ""
    calibration: str = ""
    reference_plane: str = ""
    feed_line: str = ""
    notes: str = ""


class SimulationRunPayload(StrictModel):
    id: UUID
    design_id: UUID
    created_at: datetime
    result: SimulationResultPayload
    band_id: str | None = None
    batch_id: UUID | None = None


ParameterPayload = (
    DipoleParametersPayload
    | FoldedDipoleParametersPayload
    | LoopParametersPayload
    | MagneticLoopParametersPayload
    | OCFDParametersPayload
    | VerticalParametersPayload
    | InvertedVParametersPayload
    | InvertedLParametersPayload
    | YagiParametersPayload
    | MoxonParametersPayload
    | FanDipoleParametersPayload
    | DisconeParametersPayload
    | HexbeamParametersPayload
    | EndFedParametersPayload
    | LoadedDipoleParametersPayload
    | PhasedVerticalParametersPayload
    | QuadBeamParametersPayload
    | JPoleParametersPayload
    | RingoParametersPayload
    | ScvParametersPayload
    | BiquadParametersPayload
    | BeverageParametersPayload
    | T2FDParametersPayload
    | TransmissionLineDoubletParametersPayload
    | TrapDipoleParametersPayload
    | TrapYagiParametersPayload
    | ZeppParametersPayload
    | CustomParametersPayload
)


def _payload_antenna_type(value: ParameterPayload) -> str:
    if isinstance(value, DipoleParametersPayload):
        return ANTENNA_TYPE_WIRE_DIPOLE
    if isinstance(value, FoldedDipoleParametersPayload):
        return ANTENNA_TYPE_FOLDED_DIPOLE
    if isinstance(value, OCFDParametersPayload):
        return ANTENNA_TYPE_OCFD
    if isinstance(value, VerticalParametersPayload):
        return ANTENNA_TYPE_VERTICAL
    if isinstance(value, InvertedVParametersPayload):
        return ANTENNA_TYPE_INVERTED_V
    if isinstance(value, InvertedLParametersPayload):
        return ANTENNA_TYPE_INVERTED_L
    if isinstance(value, YagiParametersPayload):
        return ANTENNA_TYPE_YAGI
    if isinstance(value, MoxonParametersPayload):
        return ANTENNA_TYPE_MOXON
    if isinstance(value, FanDipoleParametersPayload):
        return ANTENNA_TYPE_FAN_DIPOLE
    if isinstance(value, DisconeParametersPayload):
        return ANTENNA_TYPE_DISCONE
    if isinstance(value, HexbeamParametersPayload):
        return ANTENNA_TYPE_HEXBEAM
    if isinstance(value, EndFedParametersPayload):
        return ANTENNA_TYPE_ENDFED
    if isinstance(value, LoadedDipoleParametersPayload):
        return ANTENNA_TYPE_LOADED_DIPOLE
    if isinstance(value, PhasedVerticalParametersPayload):
        return ANTENNA_TYPE_PHASED_VERTICAL
    if isinstance(value, QuadBeamParametersPayload):
        return ANTENNA_TYPE_QUAD_BEAM
    if isinstance(value, JPoleParametersPayload):
        return ANTENNA_TYPE_J_POLE
    if isinstance(value, RingoParametersPayload):
        return ANTENNA_TYPE_RINGO
    if isinstance(value, ScvParametersPayload):
        return (
            ANTENNA_TYPE_HALF_SQUARE
            if value.kind is ScvKind.HALF_SQUARE
            else ANTENNA_TYPE_BOBTAIL_CURTAIN
        )
    if isinstance(value, BiquadParametersPayload):
        return (
            ANTENNA_TYPE_BIQUAD if value.kind is BiquadKind.SINGLE else ANTENNA_TYPE_DOUBLE_BIQUAD
        )
    if isinstance(value, BeverageParametersPayload):
        return ANTENNA_TYPE_BEVERAGE
    if isinstance(value, TrapDipoleParametersPayload):
        return ANTENNA_TYPE_TRAP_DIPOLE
    if isinstance(value, TrapYagiParametersPayload):
        return ANTENNA_TYPE_TRAP_YAGI
    if isinstance(value, T2FDParametersPayload):
        return ANTENNA_TYPE_T2FD
    if isinstance(value, TransmissionLineDoubletParametersPayload):
        return ANTENNA_TYPE_G5RV if value.preset is DoubletPreset.G5RV else ANTENNA_TYPE_ZS6BKW
    if isinstance(value, ZeppParametersPayload):
        return ANTENNA_TYPE_ZEPP
    if isinstance(value, MagneticLoopParametersPayload):
        return ANTENNA_TYPE_MAGNETIC_LOOP
    if isinstance(value, CustomParametersPayload):
        return ANTENNA_TYPE_CUSTOM
    return ANTENNA_TYPE_LOOP


def _parameters_payload_class(antenna_type: str) -> type[ParameterPayload] | None:
    if antenna_type == ANTENNA_TYPE_WIRE_DIPOLE:
        return DipoleParametersPayload
    if antenna_type == ANTENNA_TYPE_FOLDED_DIPOLE:
        return FoldedDipoleParametersPayload
    if antenna_type == ANTENNA_TYPE_LOOP:
        return LoopParametersPayload
    if antenna_type == ANTENNA_TYPE_MAGNETIC_LOOP:
        return MagneticLoopParametersPayload
    if antenna_type == ANTENNA_TYPE_OCFD:
        return OCFDParametersPayload
    if antenna_type == ANTENNA_TYPE_VERTICAL:
        return VerticalParametersPayload
    if antenna_type == ANTENNA_TYPE_INVERTED_V:
        return InvertedVParametersPayload
    if antenna_type == ANTENNA_TYPE_INVERTED_L:
        return InvertedLParametersPayload
    if antenna_type == ANTENNA_TYPE_YAGI:
        return YagiParametersPayload
    if antenna_type == ANTENNA_TYPE_MOXON:
        return MoxonParametersPayload
    if antenna_type == ANTENNA_TYPE_FAN_DIPOLE:
        return FanDipoleParametersPayload
    if antenna_type == ANTENNA_TYPE_DISCONE:
        return DisconeParametersPayload
    if antenna_type == ANTENNA_TYPE_HEXBEAM:
        return HexbeamParametersPayload
    if antenna_type == ANTENNA_TYPE_ENDFED:
        return EndFedParametersPayload
    if antenna_type == ANTENNA_TYPE_LOADED_DIPOLE:
        return LoadedDipoleParametersPayload
    if antenna_type == ANTENNA_TYPE_PHASED_VERTICAL:
        return PhasedVerticalParametersPayload
    if antenna_type == ANTENNA_TYPE_QUAD_BEAM:
        return QuadBeamParametersPayload
    if antenna_type == ANTENNA_TYPE_J_POLE:
        return JPoleParametersPayload
    if antenna_type == ANTENNA_TYPE_RINGO:
        return RingoParametersPayload
    if antenna_type in {ANTENNA_TYPE_HALF_SQUARE, ANTENNA_TYPE_BOBTAIL_CURTAIN}:
        return ScvParametersPayload
    if antenna_type in {ANTENNA_TYPE_BIQUAD, ANTENNA_TYPE_DOUBLE_BIQUAD}:
        return BiquadParametersPayload
    if antenna_type == ANTENNA_TYPE_BEVERAGE:
        return BeverageParametersPayload
    if antenna_type == ANTENNA_TYPE_TRAP_DIPOLE:
        return TrapDipoleParametersPayload
    if antenna_type == ANTENNA_TYPE_TRAP_YAGI:
        return TrapYagiParametersPayload
    if antenna_type == ANTENNA_TYPE_T2FD:
        return T2FDParametersPayload
    if antenna_type in {ANTENNA_TYPE_G5RV, ANTENNA_TYPE_ZS6BKW}:
        return TransmissionLineDoubletParametersPayload
    if antenna_type == ANTENNA_TYPE_ZEPP:
        return ZeppParametersPayload
    if antenna_type == ANTENNA_TYPE_CUSTOM:
        return CustomParametersPayload
    return None


class DesignProvenancePayload(StrictModel):
    method_id: str = Field(min_length=1)
    confidence: str = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    tolerance_m: float = Field(ge=0.0)
    source_ids: list[str] = Field(default_factory=list)


class BandSelectionPayload(StrictModel):
    band_id: str = Field(min_length=1)
    points: int = Field(default=15, ge=2, le=1_000)


class BandPlanPayload(StrictModel):
    selections: list[BandSelectionPayload] = Field(default_factory=list)


class OptimizationRecommendationPayload(StrictModel):
    key: str = Field(min_length=1)
    severity: str = Field(default="info", pattern="^(info|warning)$")
    variables: list[str] = Field(default_factory=list)


class OptimizationSummaryPayload(StrictModel):
    method: str = Field(min_length=1)
    version: int = Field(default=1, ge=1)
    mode: str = Field(pattern="^(single|band_aware|robust)$")
    objective: str = Field(min_length=1)
    status: str = Field(min_length=1)
    budget_profile: str = Field(min_length=1)
    evaluations: int = Field(ge=0)
    seed: int = Field(ge=0)
    best_values: dict[str, float] = Field(default_factory=dict)
    best_metrics: dict[str, float] = Field(default_factory=dict)
    band_edges_hz: list[float] = Field(default_factory=list)
    tolerance: float = Field(default=0.0, ge=0.0, lt=1.0)
    weights: dict[str, float] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)
    recommendations: list[OptimizationRecommendationPayload] = Field(default_factory=list)
    completed_at: datetime

    @model_validator(mode="after")
    def _validate_completed_at(self) -> Self:
        if self.completed_at.tzinfo is None or self.completed_at.utcoffset() is None:
            raise ValueError("completed_at must be timezone-aware")
        return self


class DesignPayload(StrictModel):
    id: UUID
    name: str = Field(min_length=1)
    antenna_type: str = Field(min_length=1)
    parameters: ParameterPayload
    antenna: AntennaPayload
    provenance: DesignProvenancePayload | None = None
    band_plan: BandPlanPayload | None = None
    optimization_summary: OptimizationSummaryPayload | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_parameters(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        antenna_type = data.get("antenna_type")
        if not isinstance(antenna_type, str):
            return data
        payload_class = _parameters_payload_class(antenna_type)
        if payload_class is None:
            raise ValueError(f"unsupported antenna type: {antenna_type}")
        parameters = data.get("parameters")
        if not isinstance(parameters, dict):
            return data
        coerced = dict(data)
        coerced["parameters"] = payload_class.model_validate(parameters)
        return coerced

    @model_validator(mode="after")
    def _validate_antenna_type(self) -> Self:
        payload_type = _payload_antenna_type(self.parameters)
        if payload_type != self.antenna_type:
            raise ValueError(
                f"antenna_type {self.antenna_type!r} does not match "
                f"the parameter type {payload_type!r}"
            )
        return self


class ProjectPayload(StrictModel):
    id: UUID
    name: str = Field(min_length=1)
    description: str = ""
    created_at: datetime
    updated_at: datetime
    designs: list[DesignPayload] = Field(default_factory=list)
    simulation_runs: list[SimulationRunPayload] = Field(default_factory=list)
    measurements: list[MeasurementPayload] = Field(default_factory=list)
    feed_line: FeedLinePayload | None = None
    matching_network: LNetworkPayload | None = None
    balun_loss: BalunLossPayload | None = None

    @model_validator(mode="after")
    def _validate_timestamps(self) -> Self:
        for name, value in (
            ("created_at", self.created_at),
            ("updated_at", self.updated_at),
        ):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be earlier than created_at")
        return self


class ProjectDocument(StrictModel):
    format: str = Field(min_length=1)
    schema_version: int = Field(ge=1)
    project: ProjectPayload

    @model_validator(mode="after")
    def _validate_format(self) -> Self:
        if self.format != PROJECT_FORMAT:
            raise ValueError(f"unsupported project format: {self.format!r}")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported project schema version: {self.schema_version}")
        return self


# Domain -> payload ---------------------------------------------------------


def _material_from_domain(value: ConductorMaterial) -> MaterialPayload:
    return MaterialPayload(
        name=value.name,
        conductivity_s_per_m=value.conductivity_s_per_m,
        relative_permeability=value.relative_permeability,
    )


def _point_from_domain(value: Point3D) -> PointPayload:
    return PointPayload(x_m=value.x_m, y_m=value.y_m, z_m=value.z_m)


def _wire_from_domain(value: Wire) -> WirePayload:
    return WirePayload(
        id=value.id,
        start=_point_from_domain(value.start),
        end=_point_from_domain(value.end),
        radius_m=value.radius_m,
        material=_material_from_domain(value.material),
    )


def _feed_from_domain(value: FeedPoint) -> FeedPayload:
    return FeedPayload(wire_id=value.wire_id, offset_m=value.offset_m)


def _ground_from_domain(value: GroundModel) -> GroundPayload:
    return GroundPayload(
        kind=value.kind,
        relative_permittivity=value.relative_permittivity,
        conductivity_s_per_m=value.conductivity_s_per_m,
    )


def _environment_from_domain(value: Environment) -> EnvironmentPayload:
    return EnvironmentPayload(ground=_ground_from_domain(value.ground))


def _load_from_domain(value: LumpedLoad) -> LoadPayload:
    return LoadPayload(
        id=value.id,
        wire_id=value.wire_id,
        offset_m=value.offset_m,
        kind=(LoadKind.PARALLEL if isinstance(value, ParallelLoad) else LoadKind.SERIES),
        resistance_ohm=value.resistance_ohm,
        inductance_h=value.inductance_h,
        capacitance_f=value.capacitance_f,
    )


def _transmission_line_from_domain(
    value: TransmissionLine,
) -> TransmissionLinePayload:
    return TransmissionLinePayload(
        id=value.id,
        start_wire_id=value.start_wire_id,
        start_offset_m=value.start_offset_m,
        end_wire_id=value.end_wire_id,
        end_offset_m=value.end_offset_m,
        characteristic_impedance_ohm=value.characteristic_impedance_ohm,
        length_m=value.length_m,
        velocity_factor=value.velocity_factor,
    )


def _transmission_line_to_domain(value: TransmissionLinePayload) -> TransmissionLine:
    return TransmissionLine(
        id=value.id,
        start_wire_id=value.start_wire_id,
        start_offset_m=value.start_offset_m,
        end_wire_id=value.end_wire_id,
        end_offset_m=value.end_offset_m,
        characteristic_impedance_ohm=value.characteristic_impedance_ohm,
        length_m=value.length_m,
        velocity_factor=value.velocity_factor,
    )


def _antenna_from_domain(value: AntennaModel) -> AntennaPayload:
    return AntennaPayload(
        name=value.name,
        design_frequency_hz=value.design_frequency_hz,
        wires=[_wire_from_domain(wire) for wire in value.wires],
        feed=_feed_from_domain(value.feed),
        environment=_environment_from_domain(value.environment),
        loads=[_load_from_domain(load) for load in value.loads],
        transmission_lines=[
            _transmission_line_from_domain(line) for line in value.transmission_lines
        ],
        sources=[
            SourcePayload(
                wire_id=source.wire_id,
                offset_m=source.offset_m,
                amplitude=source.amplitude,
                phase_deg=source.phase_deg,
            )
            for source in value.sources
        ],
    )


def _dipole_parameters_from_domain(value: DipoleParameters) -> DipoleParametersPayload:
    return DipoleParametersPayload(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        height_m=value.height_m,
        orientation=value.orientation,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        sag_m=value.sag_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _folded_parameters_from_domain(
    value: FoldedDipoleParameters,
) -> FoldedDipoleParametersPayload:
    return FoldedDipoleParametersPayload(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        height_m=value.height_m,
        spacing_m=value.spacing_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _loop_parameters_from_domain(value: LoopParameters) -> LoopParametersPayload:
    return LoopParametersPayload(
        frequency_hz=value.frequency_hz,
        circumference_m=value.circumference_m,
        height_m=value.height_m,
        sides=value.sides,
        orientation=value.orientation,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _magnetic_loop_parameters_from_domain(
    value: MagneticLoopParameters,
) -> MagneticLoopParametersPayload:
    return MagneticLoopParametersPayload(
        frequency_hz=value.frequency_hz,
        diameter_m=value.diameter_m,
        tuning_capacitance_f=value.tuning_capacitance_f,
        height_m=value.height_m,
        sides=value.sides,
        gap_length_m=value.gap_length_m,
        capacitor_esr_ohm=value.capacitor_esr_ohm,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _parameters_from_domain(value: AntennaDesignParameters) -> ParameterPayload:
    if isinstance(value, DipoleParameters):
        return _dipole_parameters_from_domain(value)
    if isinstance(value, FoldedDipoleParameters):
        return _folded_parameters_from_domain(value)
    if isinstance(value, LoopParameters):
        return _loop_parameters_from_domain(value)
    if isinstance(value, MagneticLoopParameters):
        return _magnetic_loop_parameters_from_domain(value)
    if isinstance(value, OCFDParameters):
        return _ocfd_parameters_from_domain(value)
    if isinstance(value, VerticalParameters):
        return _vertical_parameters_from_domain(value)
    if isinstance(value, InvertedVParameters):
        return _inverted_v_parameters_from_domain(value)
    if isinstance(value, InvertedLParameters):
        return _inverted_l_parameters_from_domain(value)
    if isinstance(value, YagiParameters):
        return _yagi_parameters_from_domain(value)
    if isinstance(value, MoxonParameters):
        return _moxon_parameters_from_domain(value)
    if isinstance(value, FanDipoleParameters):
        return _fan_dipole_parameters_from_domain(value)
    if isinstance(value, DisconeParameters):
        return _discone_parameters_from_domain(value)
    if isinstance(value, HexbeamParameters):
        return _hexbeam_parameters_from_domain(value)
    if isinstance(value, EndFedParameters):
        return _endfed_parameters_from_domain(value)
    if isinstance(value, LoadedDipoleParameters):
        return _loaded_dipole_parameters_from_domain(value)
    if isinstance(value, PhasedVerticalParameters):
        return _phased_vertical_parameters_from_domain(value)
    if isinstance(value, QuadBeamParameters):
        return _quad_beam_parameters_from_domain(value)
    if isinstance(value, JPoleParameters):
        return _j_pole_parameters_from_domain(value)
    if isinstance(value, RingoParameters):
        return _ringo_parameters_from_domain(value)
    if isinstance(value, ScvParameters):
        return _scv_parameters_from_domain(value)
    if isinstance(value, BiquadParameters):
        return _biquad_parameters_from_domain(value)
    if isinstance(value, BeverageParameters):
        return _beverage_parameters_from_domain(value)
    if isinstance(value, TrapDipoleParameters):
        return _trap_dipole_parameters_from_domain(value)
    if isinstance(value, TrapYagiParameters):
        return _trap_yagi_parameters_from_domain(value)
    if isinstance(value, T2FDParameters):
        return _t2fd_parameters_from_domain(value)
    if isinstance(value, TransmissionLineDoubletParameters):
        return _transmission_line_doublet_parameters_from_domain(value)
    if isinstance(value, ZeppParameters):
        return _zepp_parameters_from_domain(value)
    if isinstance(value, CustomAntennaParameters):
        return _custom_parameters_from_domain(value)
    raise TypeError(f"unsupported antenna parameters: {type(value)!r}")


def _ocfd_parameters_from_domain(value: OCFDParameters) -> OCFDParametersPayload:
    return OCFDParametersPayload(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        feed_ratio=value.feed_ratio,
        height_m=value.height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
        transformer_ratio=value.transformer_ratio,
    )


def _inverted_v_parameters_from_domain(
    value: InvertedVParameters,
) -> InvertedVParametersPayload:
    return InvertedVParametersPayload(
        frequency_hz=value.frequency_hz,
        leg_length_m=value.leg_length_m,
        apex_height_m=value.apex_height_m,
        included_angle_deg=value.included_angle_deg,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _inverted_l_parameters_from_domain(
    value: InvertedLParameters,
) -> InvertedLParametersPayload:
    return InvertedLParametersPayload(
        frequency_hz=value.frequency_hz,
        vertical_height_m=value.vertical_height_m,
        horizontal_length_m=value.horizontal_length_m,
        base_height_m=value.base_height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _vertical_parameters_from_domain(
    value: VerticalParameters,
) -> VerticalParametersPayload:
    return VerticalParametersPayload(
        frequency_hz=value.frequency_hz,
        height_m=value.height_m,
        base_height_m=value.base_height_m,
        radial_count=value.radial_count,
        radial_length_m=value.radial_length_m,
        radial_angle_deg=value.radial_angle_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
        loading_coil_enabled=value.loading_coil_enabled,
        loading_coil_offset_m=value.loading_coil_offset_m,
        loading_coil_inductance_h=value.loading_coil_inductance_h,
        loading_coil_resistance_ohm=value.loading_coil_resistance_ohm,
        top_hat_enabled=value.top_hat_enabled,
        top_hat_radius_m=value.top_hat_radius_m,
        top_hat_wire_count=value.top_hat_wire_count,
    )


def _ringo_parameters_from_domain(value: RingoParameters) -> RingoParametersPayload:
    return RingoParametersPayload(
        frequency_hz=value.frequency_hz,
        radiator_height_m=value.radiator_height_m,
        ring_diameter_m=value.ring_diameter_m,
        ring_height_m=value.ring_height_m,
        ring_sides=value.ring_sides,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _scv_parameters_from_domain(value: ScvParameters) -> ScvParametersPayload:
    return ScvParametersPayload(
        kind=value.kind,
        frequency_hz=value.frequency_hz,
        horizontal_length_m=value.horizontal_length_m,
        vertical_height_m=value.vertical_height_m,
        base_height_m=value.base_height_m,
        feed_offset_m=value.feed_offset_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _biquad_parameters_from_domain(
    value: BiquadParameters,
) -> BiquadParametersPayload:
    return BiquadParametersPayload(
        frequency_hz=value.frequency_hz,
        loop_side_m=value.loop_side_m,
        reflector_spacing_m=value.reflector_spacing_m,
        kind=value.kind,
        base_height_m=value.base_height_m,
        reflector_enabled=value.reflector_enabled,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _beverage_parameters_from_domain(
    value: BeverageParameters,
) -> BeverageParametersPayload:
    return BeverageParametersPayload(
        frequency_hz=value.frequency_hz,
        length_m=value.length_m,
        height_m=value.height_m,
        azimuth_deg=value.azimuth_deg,
        termination_enabled=value.termination_enabled,
        termination_resistance_ohm=value.termination_resistance_ohm,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _trap_yagi_parameters_from_domain(
    value: TrapYagiParameters,
) -> TrapYagiParametersPayload:
    return TrapYagiParametersPayload(
        frequency_hz=value.frequency_hz,
        high_band_frequency_hz=value.high_band_frequency_hz,
        driven_length_m=value.driven_length_m,
        reflector_spacing_m=value.reflector_spacing_m,
        trap_inset_m=value.trap_inset_m,
        trap_frequency_hz=value.trap_frequency_hz,
        trap_inductance_h=value.trap_inductance_h,
        element_count=value.element_count,
        director_spacing_m=value.director_spacing_m,
        reflector_scale=value.reflector_scale,
        director_scale=value.director_scale,
        height_m=value.height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _trap_dipole_parameters_from_domain(
    value: TrapDipoleParameters,
) -> TrapDipoleParametersPayload:
    return TrapDipoleParametersPayload(
        frequency_hz=value.frequency_hz,
        high_band_frequency_hz=value.high_band_frequency_hz,
        inner_length_m=value.inner_length_m,
        outer_length_m=value.outer_length_m,
        trap_frequency_hz=value.trap_frequency_hz,
        trap_inductance_h=value.trap_inductance_h,
        height_m=value.height_m,
        orientation=value.orientation,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _t2fd_parameters_from_domain(value: T2FDParameters) -> T2FDParametersPayload:
    return T2FDParametersPayload(
        frequency_hz=value.frequency_hz,
        highest_frequency_hz=value.highest_frequency_hz,
        length_m=value.length_m,
        spacing_m=value.spacing_m,
        height_m=value.height_m,
        orientation=value.orientation,
        termination_resistance_ohm=value.termination_resistance_ohm,
        transformer_ratio=value.transformer_ratio,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _transmission_line_doublet_parameters_from_domain(
    value: TransmissionLineDoubletParameters,
) -> TransmissionLineDoubletParametersPayload:
    return TransmissionLineDoubletParametersPayload(
        frequency_hz=value.frequency_hz,
        preset=value.preset,
        dipole_total_length_m=value.dipole_total_length_m,
        height_m=value.height_m,
        feed_height_m=value.feed_height_m,
        azimuth_deg=value.azimuth_deg,
        line_impedance_ohm=value.line_impedance_ohm,
        line_length_m=value.line_length_m,
        line_velocity_factor=value.line_velocity_factor,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _zepp_parameters_from_domain(value: ZeppParameters) -> ZeppParametersPayload:
    return ZeppParametersPayload(
        frequency_hz=value.frequency_hz,
        radiator_length_m=value.radiator_length_m,
        matching_section_length_m=value.matching_section_length_m,
        spacing_m=value.spacing_m,
        base_height_m=value.base_height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _loaded_dipole_parameters_from_domain(
    value: LoadedDipoleParameters,
) -> LoadedDipoleParametersPayload:
    return LoadedDipoleParametersPayload(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        height_m=value.height_m,
        link_offset_m=value.link_offset_m,
        link_open=value.link_open,
        loading_coil_enabled=value.loading_coil_enabled,
        loading_coil_inductance_h=value.loading_coil_inductance_h,
        loading_coil_resistance_ohm=value.loading_coil_resistance_ohm,
        orientation=value.orientation,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _quad_beam_parameters_from_domain(
    value: QuadBeamParameters,
) -> QuadBeamParametersPayload:
    return QuadBeamParametersPayload(
        frequency_hz=value.frequency_hz,
        loop_side_m=value.loop_side_m,
        reflector_spacing_m=value.reflector_spacing_m,
        height_m=value.height_m,
        element_count=value.element_count,
        director_spacing_m=value.director_spacing_m,
        reflector_scale=value.reflector_scale,
        director_scale=value.director_scale,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _hexbeam_parameters_from_domain(
    value: HexbeamParameters,
) -> HexbeamParametersPayload:
    return HexbeamParametersPayload(
        frequency_hz=value.frequency_hz,
        driver_half_length_m=value.driver_half_length_m,
        reflector_half_length_m=value.reflector_half_length_m,
        turning_radius_m=value.turning_radius_m,
        tip_gap_m=value.tip_gap_m,
        height_m=value.height_m,
        feed_gap_m=value.feed_gap_m,
        element_separation_m=value.element_separation_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _discone_parameters_from_domain(
    value: DisconeParameters,
) -> DisconeParametersPayload:
    return DisconeParametersPayload(
        frequency_hz=value.frequency_hz,
        cone_height_m=value.cone_height_m,
        cone_radius_m=value.cone_radius_m,
        disc_radius_m=value.disc_radius_m,
        base_height_m=value.base_height_m,
        disc_gap_m=value.disc_gap_m,
        wire_count=value.wire_count,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _phased_vertical_parameters_from_domain(
    value: PhasedVerticalParameters,
) -> PhasedVerticalParametersPayload:
    return PhasedVerticalParametersPayload(
        frequency_hz=value.frequency_hz,
        height_m=value.height_m,
        spacing_m=value.spacing_m,
        element_count=value.element_count,
        base_height_m=value.base_height_m,
        phase_step_deg=value.phase_step_deg,
        amplitude_taper=value.amplitude_taper,
        radial_count=value.radial_count,
        radial_length_m=value.radial_length_m,
        radial_angle_deg=value.radial_angle_deg,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _j_pole_parameters_from_domain(value: JPoleParameters) -> JPoleParametersPayload:
    return JPoleParametersPayload(
        frequency_hz=value.frequency_hz,
        radiator_height_m=value.radiator_height_m,
        stub_length_m=value.stub_length_m,
        spacing_m=value.spacing_m,
        feed_offset_m=value.feed_offset_m,
        gap_m=value.gap_m,
        base_height_m=value.base_height_m,
        folded=value.folded,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _endfed_parameters_from_domain(value: EndFedParameters) -> EndFedParametersPayload:
    return EndFedParametersPayload(
        frequency_hz=value.frequency_hz,
        length_m=value.length_m,
        feed_height_m=value.feed_height_m,
        end_height_m=value.end_height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
        transformer_ratio=value.transformer_ratio,
        counterpoise_length_m=value.counterpoise_length_m,
        counterpoise_height_m=value.counterpoise_height_m,
        counterpoise_azimuth_deg=value.counterpoise_azimuth_deg,
        loading_coil_enabled=value.loading_coil_enabled,
        loading_coil_offset_m=value.loading_coil_offset_m,
        loading_coil_inductance_h=value.loading_coil_inductance_h,
        loading_coil_resistance_ohm=value.loading_coil_resistance_ohm,
        preset=value.preset,
    )


def _fan_dipole_parameters_from_domain(
    value: FanDipoleParameters,
) -> FanDipoleParametersPayload:
    return FanDipoleParametersPayload(
        frequency_hz=value.frequency_hz,
        elements=[
            FanElementPayload(
                length_m=element.length_m,
                included_angle_deg=element.included_angle_deg,
            )
            for element in value.elements
        ],
        apex_height_m=value.apex_height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _moxon_parameters_from_domain(value: MoxonParameters) -> MoxonParametersPayload:
    return MoxonParametersPayload(
        frequency_hz=value.frequency_hz,
        width_m=value.width_m,
        depth_m=value.depth_m,
        reflector_tip_m=value.reflector_tip_m,
        driven_tip_m=value.driven_tip_m,
        height_m=value.height_m,
        azimuth_deg=value.azimuth_deg,
        polarization=value.polarization,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _yagi_parameters_from_domain(value: YagiParameters) -> YagiParametersPayload:
    return YagiParametersPayload(
        frequency_hz=value.frequency_hz,
        elements=[
            YagiElementPayload(
                position_m=element.position_m,
                length_m=element.length_m,
                radius_m=element.radius_m,
            )
            for element in value.elements
        ],
        height_m=value.height_m,
        taper_tip_length_m=value.taper_tip_length_m,
        taper_tip_radius_m=value.taper_tip_radius_m,
        driven_index=value.driven_index,
        driven_folded=value.driven_folded,
        driven_fold_spacing_m=value.driven_fold_spacing_m,
        match_type=value.match_type,
        match_length_m=value.match_length_m,
        match_spacing_m=value.match_spacing_m,
        azimuth_deg=value.azimuth_deg,
        polarization=value.polarization,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _custom_parameters_from_domain(
    value: CustomAntennaParameters,
) -> CustomParametersPayload:
    return CustomParametersPayload(
        frequency_hz=value.frequency_hz,
        wires=[_wire_from_domain(wire) for wire in value.wires],
        feed=_feed_from_domain(value.feed),
        ground=_ground_from_domain(value.ground),
        loads=[_load_from_domain(load) for load in value.loads],
        transmission_lines=[
            _transmission_line_from_domain(line) for line in value.transmission_lines
        ],
        generator_id=value.generator_id,
        generator_name=value.generator_name,
        feed_transformer_ratio=value.feed_transformer_ratio,
    )


def _frequency_plan_from_domain(value: FrequencyPlan) -> FrequencyPlanPayload:
    return FrequencyPlanPayload(
        start_hz=value.start_hz,
        stop_hz=value.stop_hz,
        count=value.count,
    )


def _segmentation_from_domain(
    value: SegmentationPolicy,
) -> SegmentationPolicyPayload:
    return SegmentationPolicyPayload(
        segments_per_wire=value.segments_per_wire,
        target_segment_length_wavelengths=value.target_segment_length_wavelengths,
        min_segments_per_wire=value.min_segments_per_wire,
        max_segments_per_wire=value.max_segments_per_wire,
        wire_segments=[
            WireSegmentsPayload(wire_id=wire_id, segments=segments)
            for wire_id, segments in value.wire_segments
        ],
    )


def _feed_line_from_domain(value: FeedLine) -> FeedLinePayload:
    return FeedLinePayload(
        characteristic_impedance_ohm=value.characteristic_impedance_ohm,
        length_m=value.length_m,
        velocity_factor=value.velocity_factor,
        matched_loss_db_per_100m=value.matched_loss_db_per_100m,
    )


def _balun_loss_from_domain(value: BalunLoss) -> BalunLossPayload:
    return BalunLossPayload(
        enabled=value.enabled,
        reference_frequency_hz=value.reference_frequency_hz,
        reference_loss_db=value.reference_loss_db,
        exponent=value.exponent,
    )


def _matching_network_from_domain(value: MatchingNetwork) -> LNetworkPayload:
    if isinstance(value, PiNetwork):
        return LNetworkPayload(
            topology="pi",
            input_shunt_inductance_h=value.input_shunt_inductance_h,
            input_shunt_capacitance_f=value.input_shunt_capacitance_f,
            series_inductance_h=value.series_inductance_h,
            series_capacitance_f=value.series_capacitance_f,
            output_shunt_inductance_h=value.output_shunt_inductance_h,
            output_shunt_capacitance_f=value.output_shunt_capacitance_f,
            q_factor=value.q_factor,
        )
    if isinstance(value, TNetwork):
        return LNetworkPayload(
            topology="t",
            input_series_inductance_h=value.input_series_inductance_h,
            input_series_capacitance_f=value.input_series_capacitance_f,
            shunt_inductance_h=value.shunt_inductance_h,
            shunt_capacitance_f=value.shunt_capacitance_f,
            output_series_inductance_h=value.output_series_inductance_h,
            output_series_capacitance_f=value.output_series_capacitance_f,
            q_factor=value.q_factor,
        )
    return LNetworkPayload(
        topology="l",
        series_inductance_h=value.series_inductance_h,
        series_capacitance_f=value.series_capacitance_f,
        shunt_inductance_h=value.shunt_inductance_h,
        shunt_capacitance_f=value.shunt_capacitance_f,
        shunt_at_input=value.shunt_at_input,
        q_factor=value.q_factor,
    )


def _far_field_from_domain(value: FarFieldRequest) -> FarFieldRequestPayload:
    return FarFieldRequestPayload(
        enabled=value.enabled,
        theta_start_deg=value.theta_start_deg,
        theta_stop_deg=value.theta_stop_deg,
        theta_count=value.theta_count,
        phi_start_deg=value.phi_start_deg,
        phi_stop_deg=value.phi_stop_deg,
        phi_count=value.phi_count,
    )


def _simulation_spec_from_domain(value: SimulationSpec) -> SimulationSpecPayload:
    return SimulationSpecPayload(
        frequency_plan=_frequency_plan_from_domain(value.frequency_plan),
        segmentation=_segmentation_from_domain(value.segmentation),
        reference_impedance_ohm=value.reference_impedance_ohm,
        extended_thin_wire_kernel=value.extended_thin_wire_kernel,
        include_conductor_losses=value.include_conductor_losses,
        far_field=_far_field_from_domain(value.far_field),
        pattern_frequencies_hz=list(value.pattern_frequencies_hz),
        feed_line=(_feed_line_from_domain(value.feed_line) if value.feed_line else None),
        matching_network=(
            _matching_network_from_domain(value.matching_network)
            if value.matching_network
            else None
        ),
        balun_loss=_balun_loss_from_domain(value.balun_loss) if value.balun_loss else None,
        feed_transformer_ratio=value.feed_transformer_ratio,
        timeout_s=value.timeout_s,
    )


def _solver_from_domain(value: SolverMetadata) -> SolverMetadataPayload:
    return SolverMetadataPayload(
        name=value.name,
        version=value.version,
        executable=value.executable,
    )


def _diagnostic_from_domain(value: Diagnostic) -> DiagnosticPayload:
    return DiagnosticPayload(
        code=value.code,
        severity=value.severity,
        message=value.message,
        field=value.field,
    )


def _power_budget_from_domain(value: PowerBudget) -> PowerBudgetPayload:
    return PowerBudgetPayload(
        input_w=value.input_w,
        radiated_w=value.radiated_w,
        structure_loss_w=value.structure_loss_w,
        network_loss_w=value.network_loss_w,
        efficiency_percent=value.efficiency_percent,
    )


def _current_from_domain(value: CurrentSample) -> CurrentSamplePayload:
    return CurrentSamplePayload(
        segment=value.segment,
        tag=value.tag,
        x_m=value.x_m,
        y_m=value.y_m,
        z_m=value.z_m,
        length_m=value.length_m,
        current_real_a=value.current_a.real,
        current_imag_a=value.current_a.imag,
        magnitude_a=value.magnitude_a,
        phase_deg=value.phase_deg,
    )


def _far_field_point_from_domain(value: FarFieldPoint) -> FarFieldPointPayload:
    return FarFieldPointPayload(
        theta_deg=value.theta_deg,
        phi_deg=value.phi_deg,
        gain_vertical_db=value.gain_vertical_db,
        gain_horizontal_db=value.gain_horizontal_db,
        gain_total_db=value.gain_total_db,
        axial_ratio=value.axial_ratio,
        tilt_deg=value.tilt_deg,
        polarization=value.polarization,
        e_theta_magnitude_v_per_m=value.e_theta_magnitude_v_per_m,
        e_theta_phase_deg=value.e_theta_phase_deg,
        e_phi_magnitude_v_per_m=value.e_phi_magnitude_v_per_m,
        e_phi_phase_deg=value.e_phi_phase_deg,
    )


def _source_result_from_domain(value: SourceResult) -> SourceResultPayload:
    return SourceResultPayload(
        wire_id=value.wire_id,
        offset_m=value.offset_m,
        tag=value.tag,
        segment=value.segment,
        amplitude=value.amplitude,
        phase_deg=value.phase_deg,
        voltage_real_v=value.voltage_v.real,
        voltage_imag_v=value.voltage_v.imag,
        current_real_a=value.current_a.real,
        current_imag_a=value.current_a.imag,
        impedance_real_ohm=value.impedance_ohm.real,
        impedance_imag_ohm=value.impedance_ohm.imag,
        power_w=value.power_w,
    )


def _source_result_to_domain(value: SourceResultPayload) -> SourceResult:
    return SourceResult(
        wire_id=value.wire_id,
        offset_m=value.offset_m,
        tag=value.tag,
        segment=value.segment,
        amplitude=value.amplitude,
        phase_deg=value.phase_deg,
        voltage_v=complex(value.voltage_real_v, value.voltage_imag_v),
        current_a=complex(value.current_real_a, value.current_imag_a),
        impedance_ohm=complex(value.impedance_real_ohm, value.impedance_imag_ohm),
        power_w=value.power_w,
    )


def _frequency_result_from_domain(value: FrequencyResult) -> FrequencyResultPayload:
    return FrequencyResultPayload(
        frequency_hz=value.frequency_hz,
        feed_tag=value.feed_tag,
        feed_segment=value.feed_segment,
        impedance_real_ohm=value.impedance_ohm.real,
        impedance_imag_ohm=value.impedance_ohm.imag,
        swr=None if math.isinf(value.swr) else value.swr,
        input_power_w=value.input_power_w,
        currents=[_current_from_domain(current) for current in value.currents],
        far_field=[_far_field_point_from_domain(point) for point in value.far_field],
        source_results=[_source_result_from_domain(source) for source in value.source_results],
        power_budget=(
            _power_budget_from_domain(value.power_budget)
            if value.power_budget is not None
            else None
        ),
        directivity_db=value.directivity_db,
        realized_gain_db=value.realized_gain_db,
        mismatch_loss_db=value.mismatch_loss_db,
        feed_line_loss_db=value.feed_line_loss_db,
        network_loss_db=value.network_loss_db,
        balun_loss_db=value.balun_loss_db,
    )


def _simulation_result_from_domain(value: SimulationResult) -> SimulationResultPayload:
    return SimulationResultPayload(
        status=value.status,
        spec=_simulation_spec_from_domain(value.spec),
        model_fingerprint=value.model_fingerprint,
        solver=_solver_from_domain(value.solver),
        frequencies=[_frequency_result_from_domain(f) for f in value.frequencies],
        diagnostics=[_diagnostic_from_domain(diagnostic) for diagnostic in value.diagnostics],
        raw_input=value.raw_input,
        raw_output=value.raw_output,
        stderr=value.stderr,
        duration_s=value.duration_s,
        started_at=value.started_at,
        finished_at=value.finished_at,
    )


def _measurement_from_domain(value: Measurement) -> MeasurementPayload:
    return MeasurementPayload(
        id=value.id,
        name=value.name,
        created_at=value.created_at,
        reference_impedance_ohm=value.reference_impedance_ohm,
        points=[
            MeasurementPointPayload(
                frequency_hz=point.frequency_hz,
                impedance_real_ohm=point.impedance_ohm.real,
                impedance_imag_ohm=point.impedance_ohm.imag,
            )
            for point in value.points
        ],
        source=value.source,
        calibration=value.calibration,
        reference_plane=value.reference_plane,
        feed_line=value.feed_line,
        notes=value.notes,
    )


def _simulation_run_from_domain(value: SimulationRun) -> SimulationRunPayload:
    return SimulationRunPayload(
        id=value.id,
        design_id=value.design_id,
        created_at=value.created_at,
        result=_simulation_result_from_domain(value.result),
        band_id=value.band_id,
        batch_id=value.batch_id,
    )


def _provenance_from_domain(value: DesignProvenance) -> DesignProvenancePayload:
    return DesignProvenancePayload(
        method_id=value.method_id,
        confidence=value.confidence,
        assumptions=list(value.assumptions),
        warnings=list(value.warnings),
        tolerance_m=value.tolerance_m,
        source_ids=list(value.source_ids),
    )


def _provenance_to_domain(value: DesignProvenancePayload) -> DesignProvenance:
    return DesignProvenance(
        method_id=value.method_id,
        confidence=value.confidence,
        assumptions=tuple(value.assumptions),
        warnings=tuple(value.warnings),
        tolerance_m=value.tolerance_m,
        source_ids=tuple(value.source_ids),
    )


def _optimization_summary_from_domain(
    value: OptimizationSummary,
) -> OptimizationSummaryPayload:
    return OptimizationSummaryPayload(
        method=value.method,
        version=value.version,
        mode=value.mode.value,
        objective=value.objective,
        status=value.status,
        budget_profile=value.budget_profile,
        evaluations=value.evaluations,
        seed=value.seed,
        best_values=dict(value.best_values),
        best_metrics=dict(value.best_metrics),
        band_edges_hz=list(value.band_edges_hz),
        tolerance=value.tolerance,
        weights=dict(value.weights),
        constraints=list(value.constraints),
        recommendations=[
            OptimizationRecommendationPayload(
                key=recommendation.key,
                severity=recommendation.severity.value,
                variables=list(recommendation.variables),
            )
            for recommendation in value.recommendations
        ],
        completed_at=value.completed_at,
    )


def _optimization_summary_to_domain(
    value: OptimizationSummaryPayload,
) -> OptimizationSummary:
    return OptimizationSummary(
        mode=OptimizationMode(value.mode),
        objective=value.objective,
        status=value.status,
        budget_profile=value.budget_profile,
        evaluations=value.evaluations,
        seed=value.seed,
        best_values=dict(value.best_values),
        best_metrics=dict(value.best_metrics),
        completed_at=value.completed_at,
        method=value.method,
        version=value.version,
        band_edges_hz=tuple(value.band_edges_hz),
        tolerance=value.tolerance,
        weights=dict(value.weights),
        constraints=tuple(value.constraints),
        recommendations=tuple(
            OptimizationRecommendation(
                key=recommendation.key,
                severity=RecommendationSeverity(recommendation.severity),
                variables=tuple(recommendation.variables),
            )
            for recommendation in value.recommendations
        ),
    )


def _band_plan_from_domain(value: BandPlan) -> BandPlanPayload:
    return BandPlanPayload(
        selections=[
            BandSelectionPayload(band_id=selection.band.name, points=selection.points)
            for selection in value.selections
        ]
    )


def _design_from_domain(value: DesignVariant) -> DesignPayload:
    return DesignPayload(
        id=value.id,
        name=value.name,
        antenna_type=value.antenna_type,
        parameters=_parameters_from_domain(value.parameters),
        antenna=_antenna_from_domain(value.antenna),
        provenance=(
            _provenance_from_domain(value.provenance) if value.provenance is not None else None
        ),
        band_plan=(
            _band_plan_from_domain(value.band_plan) if value.band_plan is not None else None
        ),
        optimization_summary=(
            _optimization_summary_from_domain(value.optimization_summary)
            if value.optimization_summary is not None
            else None
        ),
    )


def _project_from_domain(value: Project) -> ProjectPayload:
    return ProjectPayload(
        id=value.id,
        name=value.name,
        description=value.description,
        created_at=value.created_at,
        updated_at=value.updated_at,
        designs=[_design_from_domain(design) for design in value.designs],
        simulation_runs=[_simulation_run_from_domain(run) for run in value.simulation_runs],
        measurements=[_measurement_from_domain(measurement) for measurement in value.measurements],
        feed_line=(_feed_line_from_domain(value.feed_line) if value.feed_line else None),
        matching_network=(
            _matching_network_from_domain(value.matching_network)
            if value.matching_network
            else None
        ),
        balun_loss=_balun_loss_from_domain(value.balun_loss) if value.balun_loss else None,
    )


def document_from_project(project: Project) -> ProjectDocument:
    return ProjectDocument(
        format=PROJECT_FORMAT,
        schema_version=SCHEMA_VERSION,
        project=_project_from_domain(project),
    )


# Payload -> domain ---------------------------------------------------------


def _material_to_domain(value: MaterialPayload) -> ConductorMaterial:
    return ConductorMaterial(
        name=value.name,
        conductivity_s_per_m=value.conductivity_s_per_m,
        relative_permeability=value.relative_permeability,
    )


def _point_to_domain(value: PointPayload) -> Point3D:
    return Point3D(x_m=value.x_m, y_m=value.y_m, z_m=value.z_m)


def _wire_to_domain(value: WirePayload) -> Wire:
    return Wire(
        id=value.id,
        start=_point_to_domain(value.start),
        end=_point_to_domain(value.end),
        radius_m=value.radius_m,
        material=_material_to_domain(value.material),
    )


def _feed_to_domain(value: FeedPayload) -> FeedPoint:
    return FeedPoint(wire_id=value.wire_id, offset_m=value.offset_m)


def _ground_to_domain(value: GroundPayload) -> GroundModel:
    return GroundModel(
        kind=value.kind,
        relative_permittivity=value.relative_permittivity,
        conductivity_s_per_m=value.conductivity_s_per_m,
    )


def _environment_to_domain(value: EnvironmentPayload) -> Environment:
    return Environment(ground=_ground_to_domain(value.ground))


def _load_to_domain(value: LoadPayload) -> SeriesLoad | ParallelLoad:
    load_class = ParallelLoad if value.kind is LoadKind.PARALLEL else SeriesLoad
    return load_class(
        id=value.id,
        wire_id=value.wire_id,
        offset_m=value.offset_m,
        resistance_ohm=value.resistance_ohm,
        inductance_h=value.inductance_h,
        capacitance_f=value.capacitance_f,
    )


def _antenna_to_domain(value: AntennaPayload) -> AntennaModel:
    return AntennaModel(
        name=value.name,
        design_frequency_hz=value.design_frequency_hz,
        wires=tuple(_wire_to_domain(wire) for wire in value.wires),
        feed=_feed_to_domain(value.feed),
        environment=_environment_to_domain(value.environment),
        loads=tuple(_load_to_domain(load) for load in value.loads),
        transmission_lines=tuple(
            _transmission_line_to_domain(line) for line in value.transmission_lines
        ),
        sources=tuple(
            Source(
                wire_id=source.wire_id,
                offset_m=source.offset_m,
                amplitude=source.amplitude,
                phase_deg=source.phase_deg,
            )
            for source in value.sources
        ),
    )


def _dipole_parameters_to_domain(value: DipoleParametersPayload) -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        height_m=value.height_m,
        orientation=value.orientation,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        sag_m=value.sag_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _folded_parameters_to_domain(
    value: FoldedDipoleParametersPayload,
) -> FoldedDipoleParameters:
    return FoldedDipoleParameters(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        height_m=value.height_m,
        spacing_m=value.spacing_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _loop_parameters_to_domain(value: LoopParametersPayload) -> LoopParameters:
    return LoopParameters(
        frequency_hz=value.frequency_hz,
        circumference_m=value.circumference_m,
        height_m=value.height_m,
        sides=value.sides,
        orientation=value.orientation,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _parameters_to_domain(value: DesignPayload) -> AntennaDesignParameters:
    if value.antenna_type == ANTENNA_TYPE_WIRE_DIPOLE:
        if not isinstance(value.parameters, DipoleParametersPayload):
            raise ValueError("wire dipole parameters have the wrong shape")
        return _dipole_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_FOLDED_DIPOLE:
        if not isinstance(value.parameters, FoldedDipoleParametersPayload):
            raise ValueError("folded dipole parameters have the wrong shape")
        return _folded_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_LOOP:
        if not isinstance(value.parameters, LoopParametersPayload):
            raise ValueError("loop parameters have the wrong shape")
        return _loop_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_MAGNETIC_LOOP:
        if not isinstance(value.parameters, MagneticLoopParametersPayload):
            raise ValueError("magnetic-loop parameters have the wrong shape")
        return _magnetic_loop_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_OCFD:
        if not isinstance(value.parameters, OCFDParametersPayload):
            raise ValueError("OCFD parameters have the wrong shape")
        return _ocfd_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_VERTICAL:
        if not isinstance(value.parameters, VerticalParametersPayload):
            raise ValueError("vertical parameters have the wrong shape")
        return _vertical_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_INVERTED_V:
        if not isinstance(value.parameters, InvertedVParametersPayload):
            raise ValueError("inverted-V parameters have the wrong shape")
        return _inverted_v_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_INVERTED_L:
        if not isinstance(value.parameters, InvertedLParametersPayload):
            raise ValueError("inverted-L parameters have the wrong shape")
        return _inverted_l_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_YAGI:
        if not isinstance(value.parameters, YagiParametersPayload):
            raise ValueError("Yagi parameters have the wrong shape")
        return _yagi_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_MOXON:
        if not isinstance(value.parameters, MoxonParametersPayload):
            raise ValueError("Moxon parameters have the wrong shape")
        return _moxon_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_FAN_DIPOLE:
        if not isinstance(value.parameters, FanDipoleParametersPayload):
            raise ValueError("fan dipole parameters have the wrong shape")
        return _fan_dipole_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_ENDFED:
        if not isinstance(value.parameters, EndFedParametersPayload):
            raise ValueError("end-fed parameters have the wrong shape")
        return _endfed_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_LOADED_DIPOLE:
        if not isinstance(value.parameters, LoadedDipoleParametersPayload):
            raise ValueError("loaded dipole parameters have the wrong shape")
        return _loaded_dipole_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_DISCONE:
        if not isinstance(value.parameters, DisconeParametersPayload):
            raise ValueError("discone parameters have the wrong shape")
        return _discone_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_HEXBEAM:
        if not isinstance(value.parameters, HexbeamParametersPayload):
            raise ValueError("hexbeam parameters have the wrong shape")
        return _hexbeam_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_PHASED_VERTICAL:
        if not isinstance(value.parameters, PhasedVerticalParametersPayload):
            raise ValueError("phased vertical parameters have the wrong shape")
        return _phased_vertical_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_QUAD_BEAM:
        if not isinstance(value.parameters, QuadBeamParametersPayload):
            raise ValueError("quad beam parameters have the wrong shape")
        return _quad_beam_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_J_POLE:
        if not isinstance(value.parameters, JPoleParametersPayload):
            raise ValueError("J-pole parameters have the wrong shape")
        return _j_pole_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_RINGO:
        if not isinstance(value.parameters, RingoParametersPayload):
            raise ValueError("Ringo parameters have the wrong shape")
        return _ringo_parameters_to_domain(value.parameters)
    if value.antenna_type in {ANTENNA_TYPE_HALF_SQUARE, ANTENNA_TYPE_BOBTAIL_CURTAIN}:
        if not isinstance(value.parameters, ScvParametersPayload):
            raise ValueError("self-contained vertical array parameters have the wrong shape")
        expected_kind = (
            ScvKind.HALF_SQUARE
            if value.antenna_type == ANTENNA_TYPE_HALF_SQUARE
            else ScvKind.BOBTAIL_CURTAIN
        )
        if value.parameters.kind is not expected_kind:
            raise ValueError("antenna_type does not match the array variant")
        return _scv_parameters_to_domain(value.parameters)
    if value.antenna_type in {ANTENNA_TYPE_BIQUAD, ANTENNA_TYPE_DOUBLE_BIQUAD}:
        if not isinstance(value.parameters, BiquadParametersPayload):
            raise ValueError("biquad parameters have the wrong shape")
        expected_biquad_kind = (
            BiquadKind.SINGLE if value.antenna_type == ANTENNA_TYPE_BIQUAD else BiquadKind.DOUBLE
        )
        if value.parameters.kind is not expected_biquad_kind:
            raise ValueError("antenna_type does not match the biquad variant")
        return _biquad_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_BEVERAGE:
        if not isinstance(value.parameters, BeverageParametersPayload):
            raise ValueError("Beverage parameters have the wrong shape")
        return _beverage_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_TRAP_DIPOLE:
        if not isinstance(value.parameters, TrapDipoleParametersPayload):
            raise ValueError("trap dipole parameters have the wrong shape")
        return _trap_dipole_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_TRAP_YAGI:
        if not isinstance(value.parameters, TrapYagiParametersPayload):
            raise ValueError("trap Yagi parameters have the wrong shape")
        return _trap_yagi_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_T2FD:
        if not isinstance(value.parameters, T2FDParametersPayload):
            raise ValueError("T2FD parameters have the wrong shape")
        return _t2fd_parameters_to_domain(value.parameters)
    if value.antenna_type in {ANTENNA_TYPE_G5RV, ANTENNA_TYPE_ZS6BKW}:
        if not isinstance(value.parameters, TransmissionLineDoubletParametersPayload):
            raise ValueError("transmission-line doublet parameters have the wrong shape")
        expected = (
            DoubletPreset.G5RV if value.antenna_type == ANTENNA_TYPE_G5RV else DoubletPreset.ZS6BKW
        )
        if value.parameters.preset is not expected:
            raise ValueError("antenna_type does not match the doublet preset")
        return _transmission_line_doublet_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_ZEPP:
        if not isinstance(value.parameters, ZeppParametersPayload):
            raise ValueError("Zepp parameters have the wrong shape")
        return _zepp_parameters_to_domain(value.parameters)
    if value.antenna_type == ANTENNA_TYPE_CUSTOM:
        if not isinstance(value.parameters, CustomParametersPayload):
            raise ValueError("custom parameters have the wrong shape")
        return _custom_parameters_to_domain(value.parameters)
    raise ValueError(f"unsupported antenna type: {value.antenna_type}")


def _ocfd_parameters_to_domain(value: OCFDParametersPayload) -> OCFDParameters:
    return OCFDParameters(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        feed_ratio=value.feed_ratio,
        height_m=value.height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
        transformer_ratio=value.transformer_ratio,
    )


def _inverted_v_parameters_to_domain(
    value: InvertedVParametersPayload,
) -> InvertedVParameters:
    return InvertedVParameters(
        frequency_hz=value.frequency_hz,
        leg_length_m=value.leg_length_m,
        apex_height_m=value.apex_height_m,
        included_angle_deg=value.included_angle_deg,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _inverted_l_parameters_to_domain(
    value: InvertedLParametersPayload,
) -> InvertedLParameters:
    return InvertedLParameters(
        frequency_hz=value.frequency_hz,
        vertical_height_m=value.vertical_height_m,
        horizontal_length_m=value.horizontal_length_m,
        base_height_m=value.base_height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _magnetic_loop_parameters_to_domain(
    value: MagneticLoopParametersPayload,
) -> MagneticLoopParameters:
    return MagneticLoopParameters(
        frequency_hz=value.frequency_hz,
        diameter_m=value.diameter_m,
        tuning_capacitance_f=value.tuning_capacitance_f,
        height_m=value.height_m,
        sides=value.sides,
        gap_length_m=value.gap_length_m,
        capacitor_esr_ohm=value.capacitor_esr_ohm,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _vertical_parameters_to_domain(value: VerticalParametersPayload) -> VerticalParameters:
    return VerticalParameters(
        frequency_hz=value.frequency_hz,
        height_m=value.height_m,
        base_height_m=value.base_height_m,
        radial_count=value.radial_count,
        radial_length_m=value.radial_length_m,
        radial_angle_deg=value.radial_angle_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
        loading_coil_enabled=value.loading_coil_enabled,
        loading_coil_offset_m=value.loading_coil_offset_m,
        loading_coil_inductance_h=value.loading_coil_inductance_h,
        loading_coil_resistance_ohm=value.loading_coil_resistance_ohm,
        top_hat_enabled=value.top_hat_enabled,
        top_hat_radius_m=value.top_hat_radius_m,
        top_hat_wire_count=value.top_hat_wire_count,
    )


def _ringo_parameters_to_domain(value: RingoParametersPayload) -> RingoParameters:
    return RingoParameters(
        frequency_hz=value.frequency_hz,
        radiator_height_m=value.radiator_height_m,
        ring_diameter_m=value.ring_diameter_m,
        ring_height_m=value.ring_height_m,
        ring_sides=value.ring_sides,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _scv_parameters_to_domain(value: ScvParametersPayload) -> ScvParameters:
    return ScvParameters(
        frequency_hz=value.frequency_hz,
        kind=value.kind,
        horizontal_length_m=value.horizontal_length_m,
        vertical_height_m=value.vertical_height_m,
        base_height_m=value.base_height_m,
        feed_offset_m=value.feed_offset_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _biquad_parameters_to_domain(
    value: BiquadParametersPayload,
) -> BiquadParameters:
    return BiquadParameters(
        frequency_hz=value.frequency_hz,
        loop_side_m=value.loop_side_m,
        reflector_spacing_m=value.reflector_spacing_m,
        kind=value.kind,
        base_height_m=value.base_height_m,
        reflector_enabled=value.reflector_enabled,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _beverage_parameters_to_domain(
    value: BeverageParametersPayload,
) -> BeverageParameters:
    return BeverageParameters(
        frequency_hz=value.frequency_hz,
        length_m=value.length_m,
        height_m=value.height_m,
        azimuth_deg=value.azimuth_deg,
        termination_enabled=value.termination_enabled,
        termination_resistance_ohm=value.termination_resistance_ohm,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _trap_yagi_parameters_to_domain(
    value: TrapYagiParametersPayload,
) -> TrapYagiParameters:
    return TrapYagiParameters(
        frequency_hz=value.frequency_hz,
        high_band_frequency_hz=value.high_band_frequency_hz,
        driven_length_m=value.driven_length_m,
        reflector_spacing_m=value.reflector_spacing_m,
        trap_inset_m=value.trap_inset_m,
        trap_frequency_hz=value.trap_frequency_hz,
        trap_inductance_h=value.trap_inductance_h,
        element_count=value.element_count,
        director_spacing_m=value.director_spacing_m,
        reflector_scale=value.reflector_scale,
        director_scale=value.director_scale,
        height_m=value.height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _trap_dipole_parameters_to_domain(
    value: TrapDipoleParametersPayload,
) -> TrapDipoleParameters:
    return TrapDipoleParameters(
        frequency_hz=value.frequency_hz,
        high_band_frequency_hz=value.high_band_frequency_hz,
        inner_length_m=value.inner_length_m,
        outer_length_m=value.outer_length_m,
        trap_frequency_hz=value.trap_frequency_hz,
        trap_inductance_h=value.trap_inductance_h,
        height_m=value.height_m,
        orientation=value.orientation,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _t2fd_parameters_to_domain(value: T2FDParametersPayload) -> T2FDParameters:
    return T2FDParameters(
        frequency_hz=value.frequency_hz,
        highest_frequency_hz=value.highest_frequency_hz,
        length_m=value.length_m,
        spacing_m=value.spacing_m,
        height_m=value.height_m,
        orientation=value.orientation,
        termination_resistance_ohm=value.termination_resistance_ohm,
        transformer_ratio=value.transformer_ratio,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _transmission_line_doublet_parameters_to_domain(
    value: TransmissionLineDoubletParametersPayload,
) -> TransmissionLineDoubletParameters:
    return TransmissionLineDoubletParameters(
        frequency_hz=value.frequency_hz,
        preset=value.preset,
        dipole_total_length_m=value.dipole_total_length_m,
        height_m=value.height_m,
        feed_height_m=value.feed_height_m,
        azimuth_deg=value.azimuth_deg,
        line_impedance_ohm=value.line_impedance_ohm,
        line_length_m=value.line_length_m,
        line_velocity_factor=value.line_velocity_factor,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _zepp_parameters_to_domain(value: ZeppParametersPayload) -> ZeppParameters:
    return ZeppParameters(
        frequency_hz=value.frequency_hz,
        radiator_length_m=value.radiator_length_m,
        matching_section_length_m=value.matching_section_length_m,
        spacing_m=value.spacing_m,
        base_height_m=value.base_height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _loaded_dipole_parameters_to_domain(
    value: LoadedDipoleParametersPayload,
) -> LoadedDipoleParameters:
    return LoadedDipoleParameters(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        height_m=value.height_m,
        link_offset_m=value.link_offset_m,
        link_open=value.link_open,
        loading_coil_enabled=value.loading_coil_enabled,
        loading_coil_inductance_h=value.loading_coil_inductance_h,
        loading_coil_resistance_ohm=value.loading_coil_resistance_ohm,
        orientation=value.orientation,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _quad_beam_parameters_to_domain(
    value: QuadBeamParametersPayload,
) -> QuadBeamParameters:
    return QuadBeamParameters(
        frequency_hz=value.frequency_hz,
        loop_side_m=value.loop_side_m,
        reflector_spacing_m=value.reflector_spacing_m,
        height_m=value.height_m,
        element_count=value.element_count,
        director_spacing_m=value.director_spacing_m,
        reflector_scale=value.reflector_scale,
        director_scale=value.director_scale,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _hexbeam_parameters_to_domain(
    value: HexbeamParametersPayload,
) -> HexbeamParameters:
    return HexbeamParameters(
        frequency_hz=value.frequency_hz,
        driver_half_length_m=value.driver_half_length_m,
        reflector_half_length_m=value.reflector_half_length_m,
        turning_radius_m=value.turning_radius_m,
        tip_gap_m=value.tip_gap_m,
        height_m=value.height_m,
        feed_gap_m=value.feed_gap_m,
        element_separation_m=value.element_separation_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _discone_parameters_to_domain(
    value: DisconeParametersPayload,
) -> DisconeParameters:
    return DisconeParameters(
        frequency_hz=value.frequency_hz,
        cone_height_m=value.cone_height_m,
        cone_radius_m=value.cone_radius_m,
        disc_radius_m=value.disc_radius_m,
        base_height_m=value.base_height_m,
        disc_gap_m=value.disc_gap_m,
        wire_count=value.wire_count,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _phased_vertical_parameters_to_domain(
    value: PhasedVerticalParametersPayload,
) -> PhasedVerticalParameters:
    return PhasedVerticalParameters(
        frequency_hz=value.frequency_hz,
        height_m=value.height_m,
        spacing_m=value.spacing_m,
        element_count=value.element_count,
        base_height_m=value.base_height_m,
        phase_step_deg=value.phase_step_deg,
        amplitude_taper=value.amplitude_taper,
        radial_count=value.radial_count,
        radial_length_m=value.radial_length_m,
        radial_angle_deg=value.radial_angle_deg,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _j_pole_parameters_to_domain(value: JPoleParametersPayload) -> JPoleParameters:
    return JPoleParameters(
        frequency_hz=value.frequency_hz,
        radiator_height_m=value.radiator_height_m,
        stub_length_m=value.stub_length_m,
        spacing_m=value.spacing_m,
        feed_offset_m=value.feed_offset_m,
        gap_m=value.gap_m,
        base_height_m=value.base_height_m,
        folded=value.folded,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _endfed_parameters_to_domain(value: EndFedParametersPayload) -> EndFedParameters:
    return EndFedParameters(
        frequency_hz=value.frequency_hz,
        length_m=value.length_m,
        feed_height_m=value.feed_height_m,
        end_height_m=value.end_height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
        transformer_ratio=value.transformer_ratio,
        counterpoise_length_m=value.counterpoise_length_m,
        counterpoise_height_m=value.counterpoise_height_m,
        counterpoise_azimuth_deg=value.counterpoise_azimuth_deg,
        loading_coil_enabled=value.loading_coil_enabled,
        loading_coil_offset_m=value.loading_coil_offset_m,
        loading_coil_inductance_h=value.loading_coil_inductance_h,
        loading_coil_resistance_ohm=value.loading_coil_resistance_ohm,
        preset=value.preset,
    )


def _fan_dipole_parameters_to_domain(
    value: FanDipoleParametersPayload,
) -> FanDipoleParameters:
    return FanDipoleParameters(
        frequency_hz=value.frequency_hz,
        elements=tuple(
            FanElement(
                length_m=element.length_m,
                included_angle_deg=element.included_angle_deg,
            )
            for element in value.elements
        ),
        apex_height_m=value.apex_height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _moxon_parameters_to_domain(value: MoxonParametersPayload) -> MoxonParameters:
    return MoxonParameters(
        frequency_hz=value.frequency_hz,
        width_m=value.width_m,
        depth_m=value.depth_m,
        reflector_tip_m=value.reflector_tip_m,
        driven_tip_m=value.driven_tip_m,
        height_m=value.height_m,
        azimuth_deg=value.azimuth_deg,
        polarization=value.polarization,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _yagi_parameters_to_domain(value: YagiParametersPayload) -> YagiParameters:
    return YagiParameters(
        frequency_hz=value.frequency_hz,
        elements=tuple(
            YagiElement(
                position_m=element.position_m,
                length_m=element.length_m,
                radius_m=element.radius_m,
            )
            for element in value.elements
        ),
        height_m=value.height_m,
        taper_tip_length_m=value.taper_tip_length_m,
        taper_tip_radius_m=value.taper_tip_radius_m,
        driven_index=value.driven_index,
        driven_folded=value.driven_folded,
        driven_fold_spacing_m=value.driven_fold_spacing_m,
        match_type=value.match_type,
        match_length_m=value.match_length_m,
        match_spacing_m=value.match_spacing_m,
        azimuth_deg=value.azimuth_deg,
        polarization=value.polarization,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _custom_parameters_to_domain(value: CustomParametersPayload) -> CustomAntennaParameters:
    return CustomAntennaParameters(
        frequency_hz=value.frequency_hz,
        wires=tuple(_wire_to_domain(wire) for wire in value.wires),
        feed=_feed_to_domain(value.feed),
        ground=_ground_to_domain(value.ground),
        loads=tuple(_load_to_domain(load) for load in value.loads),
        transmission_lines=tuple(
            _transmission_line_to_domain(line) for line in value.transmission_lines
        ),
        generator_id=value.generator_id,
        generator_name=value.generator_name,
        feed_transformer_ratio=value.feed_transformer_ratio,
    )


def _frequency_plan_to_domain(value: FrequencyPlanPayload) -> FrequencyPlan:
    return FrequencyPlan(
        start_hz=value.start_hz,
        stop_hz=value.stop_hz,
        count=value.count,
    )


def _segmentation_to_domain(
    value: SegmentationPolicyPayload,
) -> SegmentationPolicy:
    return SegmentationPolicy(
        segments_per_wire=value.segments_per_wire,
        target_segment_length_wavelengths=value.target_segment_length_wavelengths,
        min_segments_per_wire=value.min_segments_per_wire,
        max_segments_per_wire=value.max_segments_per_wire,
        wire_segments=tuple((wire.wire_id, wire.segments) for wire in value.wire_segments),
    )


def _feed_line_to_domain(value: FeedLinePayload) -> FeedLine:
    return FeedLine(
        characteristic_impedance_ohm=value.characteristic_impedance_ohm,
        length_m=value.length_m,
        velocity_factor=value.velocity_factor,
        matched_loss_db_per_100m=value.matched_loss_db_per_100m,
    )


def _balun_loss_to_domain(value: BalunLossPayload) -> BalunLoss:
    return BalunLoss(
        enabled=value.enabled,
        reference_frequency_hz=value.reference_frequency_hz,
        reference_loss_db=value.reference_loss_db,
        exponent=value.exponent,
    )


def _matching_network_to_domain(value: LNetworkPayload) -> MatchingNetwork:
    if value.topology == "pi":
        return PiNetwork(
            input_shunt_inductance_h=value.input_shunt_inductance_h,
            input_shunt_capacitance_f=value.input_shunt_capacitance_f,
            series_inductance_h=value.series_inductance_h,
            series_capacitance_f=value.series_capacitance_f,
            output_shunt_inductance_h=value.output_shunt_inductance_h,
            output_shunt_capacitance_f=value.output_shunt_capacitance_f,
            q_factor=value.q_factor,
        )
    if value.topology == "t":
        return TNetwork(
            input_series_inductance_h=value.input_series_inductance_h,
            input_series_capacitance_f=value.input_series_capacitance_f,
            shunt_inductance_h=value.shunt_inductance_h,
            shunt_capacitance_f=value.shunt_capacitance_f,
            output_series_inductance_h=value.output_series_inductance_h,
            output_series_capacitance_f=value.output_series_capacitance_f,
            q_factor=value.q_factor,
        )
    return LNetwork(
        series_inductance_h=value.series_inductance_h,
        series_capacitance_f=value.series_capacitance_f,
        shunt_inductance_h=value.shunt_inductance_h,
        shunt_capacitance_f=value.shunt_capacitance_f,
        shunt_at_input=value.shunt_at_input,
        q_factor=value.q_factor,
    )


def _far_field_to_domain(value: FarFieldRequestPayload) -> FarFieldRequest:
    return FarFieldRequest(
        enabled=value.enabled,
        theta_start_deg=value.theta_start_deg,
        theta_stop_deg=value.theta_stop_deg,
        theta_count=value.theta_count,
        phi_start_deg=value.phi_start_deg,
        phi_stop_deg=value.phi_stop_deg,
        phi_count=value.phi_count,
    )


def _simulation_spec_to_domain(value: SimulationSpecPayload) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=_frequency_plan_to_domain(value.frequency_plan),
        segmentation=_segmentation_to_domain(value.segmentation),
        reference_impedance_ohm=value.reference_impedance_ohm,
        extended_thin_wire_kernel=value.extended_thin_wire_kernel,
        include_conductor_losses=value.include_conductor_losses,
        far_field=_far_field_to_domain(value.far_field),
        pattern_frequencies_hz=tuple(value.pattern_frequencies_hz),
        feed_line=(_feed_line_to_domain(value.feed_line) if value.feed_line else None),
        matching_network=(
            _matching_network_to_domain(value.matching_network) if value.matching_network else None
        ),
        balun_loss=_balun_loss_to_domain(value.balun_loss) if value.balun_loss else None,
        feed_transformer_ratio=value.feed_transformer_ratio,
        timeout_s=value.timeout_s,
    )


def _solver_to_domain(value: SolverMetadataPayload) -> SolverMetadata:
    return SolverMetadata(
        name=value.name,
        version=value.version,
        executable=value.executable,
    )


def _diagnostic_to_domain(value: DiagnosticPayload) -> Diagnostic:
    return Diagnostic(
        code=value.code,
        severity=value.severity,
        message=value.message,
        field=value.field,
    )


def _power_budget_to_domain(value: PowerBudgetPayload) -> PowerBudget:
    return PowerBudget(
        input_w=value.input_w,
        radiated_w=value.radiated_w,
        structure_loss_w=value.structure_loss_w,
        network_loss_w=value.network_loss_w,
        efficiency_percent=value.efficiency_percent,
    )


def _current_to_domain(value: CurrentSamplePayload) -> CurrentSample:
    return CurrentSample(
        segment=value.segment,
        tag=value.tag,
        x_m=value.x_m,
        y_m=value.y_m,
        z_m=value.z_m,
        length_m=value.length_m,
        current_a=complex(value.current_real_a, value.current_imag_a),
        magnitude_a=value.magnitude_a,
        phase_deg=value.phase_deg,
    )


def _far_field_point_to_domain(value: FarFieldPointPayload) -> FarFieldPoint:
    return FarFieldPoint(
        theta_deg=value.theta_deg,
        phi_deg=value.phi_deg,
        gain_vertical_db=value.gain_vertical_db,
        gain_horizontal_db=value.gain_horizontal_db,
        gain_total_db=value.gain_total_db,
        axial_ratio=value.axial_ratio,
        tilt_deg=value.tilt_deg,
        polarization=value.polarization,
        e_theta_magnitude_v_per_m=value.e_theta_magnitude_v_per_m,
        e_theta_phase_deg=value.e_theta_phase_deg,
        e_phi_magnitude_v_per_m=value.e_phi_magnitude_v_per_m,
        e_phi_phase_deg=value.e_phi_phase_deg,
    )


def _frequency_result_to_domain(value: FrequencyResultPayload) -> FrequencyResult:
    return FrequencyResult(
        frequency_hz=value.frequency_hz,
        feed_tag=value.feed_tag,
        feed_segment=value.feed_segment,
        impedance_ohm=complex(value.impedance_real_ohm, value.impedance_imag_ohm),
        swr=math.inf if value.swr is None else value.swr,
        input_power_w=value.input_power_w,
        currents=tuple(_current_to_domain(current) for current in value.currents),
        far_field=tuple(_far_field_point_to_domain(point) for point in value.far_field),
        source_results=tuple(_source_result_to_domain(source) for source in value.source_results),
        power_budget=(
            _power_budget_to_domain(value.power_budget) if value.power_budget is not None else None
        ),
        directivity_db=value.directivity_db,
        realized_gain_db=value.realized_gain_db,
        mismatch_loss_db=value.mismatch_loss_db,
        feed_line_loss_db=value.feed_line_loss_db,
        network_loss_db=value.network_loss_db,
        balun_loss_db=value.balun_loss_db,
    )


def _simulation_result_to_domain(value: SimulationResultPayload) -> SimulationResult:
    return SimulationResult(
        status=value.status,
        spec=_simulation_spec_to_domain(value.spec),
        model_fingerprint=value.model_fingerprint,
        solver=_solver_to_domain(value.solver),
        frequencies=tuple(_frequency_result_to_domain(f) for f in value.frequencies),
        diagnostics=tuple(_diagnostic_to_domain(diagnostic) for diagnostic in value.diagnostics),
        raw_input=value.raw_input,
        raw_output=value.raw_output,
        stderr=value.stderr,
        duration_s=value.duration_s,
        started_at=value.started_at,
        finished_at=value.finished_at,
    )


def _measurement_to_domain(value: MeasurementPayload) -> Measurement:
    return Measurement(
        id=value.id,
        name=value.name,
        created_at=value.created_at,
        reference_impedance_ohm=value.reference_impedance_ohm,
        points=tuple(
            MeasurementPoint(
                frequency_hz=point.frequency_hz,
                impedance_ohm=complex(point.impedance_real_ohm, point.impedance_imag_ohm),
            )
            for point in value.points
        ),
        source=value.source,
        calibration=value.calibration,
        reference_plane=value.reference_plane,
        feed_line=value.feed_line,
        notes=value.notes,
    )


def _simulation_run_to_domain(value: SimulationRunPayload) -> SimulationRun:
    return SimulationRun(
        id=value.id,
        design_id=value.design_id,
        created_at=value.created_at,
        result=_simulation_result_to_domain(value.result),
        band_id=value.band_id,
        batch_id=value.batch_id,
    )


def _band_plan_to_domain(value: BandPlanPayload) -> BandPlan:
    selections = []
    for selection in value.selections:
        band = amateur_band_by_id(selection.band_id)
        if band is None:
            raise ValueError(f"unknown amateur band: {selection.band_id}")
        selections.append(BandSelection(band, points=selection.points))
    return BandPlan(tuple(selections))


def _design_to_domain(value: DesignPayload) -> DesignVariant:
    parameters = _parameters_to_domain(value)
    saved_antenna = _antenna_to_domain(value.antenna)
    antenna = saved_antenna
    if isinstance(parameters, YagiParameters):
        # A Yagi geometry is always derived from its element table. Regenerate
        # it so migrations that repair saved parameters cannot leave stale
        # wires behind, while preserving user loads and transmission lines.
        antenna = parameters.to_antenna(name=saved_antenna.name)
        antenna = antenna.with_loads(saved_antenna.loads)
        antenna = antenna.with_transmission_lines(saved_antenna.transmission_lines)
    return DesignVariant(
        id=value.id,
        name=value.name,
        antenna_type=value.antenna_type,
        parameters=parameters,
        antenna=antenna,
        provenance=(
            _provenance_to_domain(value.provenance) if value.provenance is not None else None
        ),
        band_plan=_band_plan_to_domain(value.band_plan) if value.band_plan is not None else None,
        optimization_summary=(
            _optimization_summary_to_domain(value.optimization_summary)
            if value.optimization_summary is not None
            else None
        ),
    )


def project_from_document(document: ProjectDocument) -> Project:
    return Project(
        id=document.project.id,
        name=document.project.name,
        description=document.project.description,
        created_at=document.project.created_at,
        updated_at=document.project.updated_at,
        designs=tuple(_design_to_domain(design) for design in document.project.designs),
        simulation_runs=tuple(
            _simulation_run_to_domain(run) for run in document.project.simulation_runs
        ),
        measurements=tuple(
            _measurement_to_domain(measurement) for measurement in document.project.measurements
        ),
        feed_line=(
            _feed_line_to_domain(document.project.feed_line) if document.project.feed_line else None
        ),
        matching_network=(
            _matching_network_to_domain(document.project.matching_network)
            if document.project.matching_network
            else None
        ),
        balun_loss=(
            _balun_loss_to_domain(document.project.balun_loss)
            if document.project.balun_loss
            else None
        ),
    )
