# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pydantic schema and domain mapping for native project files."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from ..domain.antennas.feed import FeedPoint
from ..domain.antennas.geometry import Point3D
from ..domain.antennas.materials import ConductorMaterial
from ..domain.antennas.wire import Wire
from ..domain.environment.environment import Environment
from ..domain.environment.ground import GroundKind, GroundModel
from ..domain.projects.project import DesignVariant, Project
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


class AntennaPayload(StrictModel):
    name: str = Field(min_length=1)
    design_frequency_hz: float = Field(gt=0.0)
    wires: list[WirePayload] = Field(min_length=1)
    feed: FeedPayload
    environment: EnvironmentPayload


class DipoleParametersPayload(StrictModel):
    frequency_hz: float = Field(gt=0.0)
    total_length_m: float = Field(gt=0.0)
    height_m: float = Field(ge=0.0)
    azimuth_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    wire_radius_m: float = Field(default=0.001, gt=0.0)
    material: MaterialPayload
    ground: GroundPayload


class DesignPayload(StrictModel):
    id: UUID
    name: str = Field(min_length=1)
    antenna_type: str = Field(min_length=1)
    parameters: DipoleParametersPayload
    antenna: AntennaPayload


class ProjectPayload(StrictModel):
    id: UUID
    name: str = Field(min_length=1)
    description: str = ""
    created_at: datetime
    updated_at: datetime
    designs: list[DesignPayload] = Field(default_factory=list)

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


def _antenna_from_domain(value: AntennaModel) -> AntennaPayload:
    return AntennaPayload(
        name=value.name,
        design_frequency_hz=value.design_frequency_hz,
        wires=[_wire_from_domain(wire) for wire in value.wires],
        feed=_feed_from_domain(value.feed),
        environment=_environment_from_domain(value.environment),
    )


def _dipole_parameters_from_domain(value: DipoleParameters) -> DipoleParametersPayload:
    return DipoleParametersPayload(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        height_m=value.height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_from_domain(value.material),
        ground=_ground_from_domain(value.ground),
    )


def _design_from_domain(value: DesignVariant) -> DesignPayload:
    return DesignPayload(
        id=value.id,
        name=value.name,
        antenna_type=value.antenna_type,
        parameters=_dipole_parameters_from_domain(value.parameters),
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


def _antenna_to_domain(value: AntennaPayload) -> AntennaModel:
    return AntennaModel(
        name=value.name,
        design_frequency_hz=value.design_frequency_hz,
        wires=tuple(_wire_to_domain(wire) for wire in value.wires),
        feed=_feed_to_domain(value.feed),
        environment=_environment_to_domain(value.environment),
    )


def _dipole_parameters_to_domain(value: DipoleParametersPayload) -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=value.frequency_hz,
        total_length_m=value.total_length_m,
        height_m=value.height_m,
        azimuth_deg=value.azimuth_deg,
        wire_radius_m=value.wire_radius_m,
        material=_material_to_domain(value.material),
        ground=_ground_to_domain(value.ground),
    )


def _design_to_domain(value: DesignPayload) -> DesignVariant:
    if value.antenna_type != ANTENNA_TYPE_WIRE_DIPOLE:
        raise ValueError(f"unsupported antenna type: {value.antenna_type}")
    return DesignVariant(
        id=value.id,
        name=value.name,
        antenna_type=value.antenna_type,
        parameters=_dipole_parameters_to_domain(value.parameters),
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
    )
