# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pydantic schema and domain mapping for native project files."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.custom import ANTENNA_TYPE_CUSTOM, CustomAntennaParameters
from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.dipole import (
    ANTENNA_TYPE_WIRE_DIPOLE,
    DipoleOrientation,
    DipoleParameters,
)
from ..domain.antennas.fan_dipole import (
    ANTENNA_TYPE_FAN_DIPOLE,
    FanDipoleParameters,
    FanElement,
)
from ..domain.antennas.feed import FeedPoint
from ..domain.antennas.feed_line import FeedLine
from ..domain.antennas.folded_dipole import (
    ANTENNA_TYPE_FOLDED_DIPOLE,
    FoldedDipoleParameters,
)
from ..domain.antennas.geometry import Point3D
from ..domain.antennas.inverted_v import ANTENNA_TYPE_INVERTED_V, InvertedVParameters
from ..domain.antennas.load import LoadKind, LumpedLoad, ParallelLoad, SeriesLoad
from ..domain.antennas.loop import (
    ANTENNA_TYPE_LOOP,
    MAX_SIDES,
    MIN_SIDES,
    LoopParameters,
)
from ..domain.antennas.materials import ConductorMaterial
from ..domain.antennas.moxon import ANTENNA_TYPE_MOXON, MoxonParameters
from ..domain.antennas.ocfd import ANTENNA_TYPE_OCFD, OCFDParameters
from ..domain.antennas.vertical import ANTENNA_TYPE_VERTICAL, VerticalParameters
from ..domain.antennas.wire import Wire
from ..domain.antennas.yagi import ANTENNA_TYPE_YAGI, YagiElement, YagiParameters
from ..domain.common.validation import Diagnostic, Severity
from ..domain.environment.environment import Environment
from ..domain.environment.ground import GroundKind, GroundModel
from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.far_field import FarFieldRequest
from ..domain.simulation.frequency import FrequencyPlan
from ..domain.simulation.result import (
    CurrentSample,
    FarFieldPoint,
    FrequencyResult,
    PowerBudget,
    SimulationResult,
    SimulationStatus,
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


class AntennaPayload(StrictModel):
    name: str = Field(min_length=1)
    design_frequency_hz: float = Field(gt=0.0)
    wires: list[WirePayload] = Field(min_length=1)
    feed: FeedPayload
    environment: EnvironmentPayload
    loads: list[LoadPayload] = Field(default_factory=list)


class DipoleParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    total_length_m: float = Field(gt=0.0)
    height_m: float = Field(ge=0.0)
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
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
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
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


class InvertedVParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    leg_length_m: float = Field(gt=0.0)
    apex_height_m: float = Field(ge=0.0)
    included_angle_deg: float = Field(default=120.0, gt=0.0, lt=180.0)
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
    driven_index: int = Field(default=1, ge=0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    material: MaterialPayload
    ground: GroundPayload


class CustomParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    wires: list[WirePayload] = Field(min_length=1)
    feed: FeedPayload
    ground: GroundPayload
    loads: list[LoadPayload] = Field(default_factory=list)
    generator_id: str | None = Field(default=None, min_length=1)
    generator_name: str | None = Field(default=None, min_length=1)


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
    feed_line: FeedLinePayload | None = None
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
    power_budget: PowerBudgetPayload | None = None


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


class SimulationRunPayload(StrictModel):
    id: UUID
    design_id: UUID
    created_at: datetime
    result: SimulationResultPayload


ParameterPayload = (
    DipoleParametersPayload
    | FoldedDipoleParametersPayload
    | LoopParametersPayload
    | OCFDParametersPayload
    | VerticalParametersPayload
    | InvertedVParametersPayload
    | YagiParametersPayload
    | MoxonParametersPayload
    | FanDipoleParametersPayload
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
    if isinstance(value, YagiParametersPayload):
        return ANTENNA_TYPE_YAGI
    if isinstance(value, MoxonParametersPayload):
        return ANTENNA_TYPE_MOXON
    if isinstance(value, FanDipoleParametersPayload):
        return ANTENNA_TYPE_FAN_DIPOLE
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
    if antenna_type == ANTENNA_TYPE_OCFD:
        return OCFDParametersPayload
    if antenna_type == ANTENNA_TYPE_VERTICAL:
        return VerticalParametersPayload
    if antenna_type == ANTENNA_TYPE_INVERTED_V:
        return InvertedVParametersPayload
    if antenna_type == ANTENNA_TYPE_YAGI:
        return YagiParametersPayload
    if antenna_type == ANTENNA_TYPE_MOXON:
        return MoxonParametersPayload
    if antenna_type == ANTENNA_TYPE_FAN_DIPOLE:
        return FanDipoleParametersPayload
    if antenna_type == ANTENNA_TYPE_CUSTOM:
        return CustomParametersPayload
    return None


class DesignPayload(StrictModel):
    id: UUID
    name: str = Field(min_length=1)
    antenna_type: str = Field(min_length=1)
    parameters: ParameterPayload
    antenna: AntennaPayload

    @model_validator(mode="before")
    @classmethod
    def _coerce_parameters(cls, data: Any) -> Any:
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
    feed_line: FeedLinePayload | None = None

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


def _antenna_from_domain(value: AntennaModel) -> AntennaPayload:
    return AntennaPayload(
        name=value.name,
        design_frequency_hz=value.design_frequency_hz,
        wires=[_wire_from_domain(wire) for wire in value.wires],
        feed=_feed_from_domain(value.feed),
        environment=_environment_from_domain(value.environment),
        loads=[_load_from_domain(load) for load in value.loads],
    )


def _dipole_parameters_from_domain(value: DipoleParameters) -> DipoleParametersPayload:
    return DipoleParametersPayload(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        height_m=value.height_m,
        orientation=value.orientation,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
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
    if isinstance(value, OCFDParameters):
        return _ocfd_parameters_from_domain(value)
    if isinstance(value, VerticalParameters):
        return _vertical_parameters_from_domain(value)
    if isinstance(value, InvertedVParameters):
        return _inverted_v_parameters_from_domain(value)
    if isinstance(value, YagiParameters):
        return _yagi_parameters_from_domain(value)
    if isinstance(value, MoxonParameters):
        return _moxon_parameters_from_domain(value)
    if isinstance(value, FanDipoleParameters):
        return _fan_dipole_parameters_from_domain(value)
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
        driven_index=value.driven_index,
        azimuth_deg=value.azimuth_deg,
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
        generator_id=value.generator_id,
        generator_name=value.generator_name,
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
        feed_line=(_feed_line_from_domain(value.feed_line) if value.feed_line else None),
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
        power_budget=(
            _power_budget_from_domain(value.power_budget)
            if value.power_budget is not None
            else None
        ),
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


def _simulation_run_from_domain(value: SimulationRun) -> SimulationRunPayload:
    return SimulationRunPayload(
        id=value.id,
        design_id=value.design_id,
        created_at=value.created_at,
        result=_simulation_result_from_domain(value.result),
    )


def _design_from_domain(value: DesignVariant) -> DesignPayload:
    return DesignPayload(
        id=value.id,
        name=value.name,
        antenna_type=value.antenna_type,
        parameters=_parameters_from_domain(value.parameters),
        antenna=_antenna_from_domain(value.antenna),
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
        feed_line=(_feed_line_from_domain(value.feed_line) if value.feed_line else None),
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
    )


def _dipole_parameters_to_domain(value: DipoleParametersPayload) -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        height_m=value.height_m,
        orientation=value.orientation,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
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
        driven_index=value.driven_index,
        azimuth_deg=value.azimuth_deg,
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
        generator_id=value.generator_id,
        generator_name=value.generator_name,
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
        feed_line=(_feed_line_to_domain(value.feed_line) if value.feed_line else None),
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
        power_budget=(
            _power_budget_to_domain(value.power_budget) if value.power_budget is not None else None
        ),
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


def _simulation_run_to_domain(value: SimulationRunPayload) -> SimulationRun:
    return SimulationRun(
        id=value.id,
        design_id=value.design_id,
        created_at=value.created_at,
        result=_simulation_result_to_domain(value.result),
    )


def _design_to_domain(value: DesignPayload) -> DesignVariant:
    return DesignVariant(
        id=value.id,
        name=value.name,
        antenna_type=value.antenna_type,
        parameters=_parameters_to_domain(value),
        antenna=_antenna_to_domain(value.antenna),
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
        feed_line=(
            _feed_line_to_domain(document.project.feed_line) if document.project.feed_line else None
        ),
    )
