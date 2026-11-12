# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Property-based checks for project persistence and schema migrations."""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from hypothesis import given, settings
from hypothesis import strategies as st

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.dipole import DipoleOrientation, DipoleParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.constants import SCHEMA_VERSION
from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.persistence.migrations import migrate_document
from antennadesk.persistence.schema import (
    ProjectDocument,
    document_from_project,
    project_from_document,
)

FIXED_NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
PROJECT_ID = UUID("00000000-0000-0000-0000-000000000001")
DESIGN_ID = UUID("00000000-0000-0000-0000-000000000002")

NAME = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_",
    min_size=1,
    max_size=40,
).filter(lambda value: value.strip())
DESCRIPTION = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_",
    max_size=120,
)
FREQUENCY_HZ = st.floats(
    min_value=1_800_000.0,
    max_value=30_000_000.0,
    allow_nan=False,
    allow_infinity=False,
)
LENGTH_M = st.floats(
    min_value=0.1,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
)
HEIGHT_M = st.floats(
    min_value=0.0,
    max_value=50.0,
    allow_nan=False,
    allow_infinity=False,
)
AZIMUTH_DEG = st.floats(
    min_value=-720.0,
    max_value=720.0,
    allow_nan=False,
    allow_infinity=False,
)
RADIUS_M = st.floats(
    min_value=1e-4,
    max_value=1e-2,
    allow_nan=False,
    allow_infinity=False,
)
ORIENTATION = st.sampled_from(list(DipoleOrientation))
GROUND = st.one_of(
    st.just(GroundModel.free_space()),
    st.just(GroundModel.perfect()),
    st.builds(
        GroundModel.finite,
        relative_permittivity=st.floats(
            min_value=1.0,
            max_value=80.0,
            allow_nan=False,
            allow_infinity=False,
        ),
        conductivity_s_per_m=st.floats(
            min_value=1e-5,
            max_value=1e-1,
            allow_nan=False,
            allow_infinity=False,
        ),
    ),
)


def _project(
    *,
    project_name: str,
    description: str,
    design_name: str,
    frequency_hz: float,
    total_length_m: float,
    height_m: float,
    azimuth_deg: float,
    wire_radius_m: float,
    orientation: DipoleOrientation,
    ground: GroundModel,
) -> Project:
    parameters = DipoleParameters(
        frequency_hz=frequency_hz,
        total_length_m=total_length_m,
        height_m=height_m,
        orientation=orientation,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        ground=ground,
    )
    return CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name=project_name,
            variant_name=design_name,
            parameters=parameters,
            description=description,
        ),
        project_id=PROJECT_ID,
        design_id=DESIGN_ID,
        now=FIXED_NOW,
    )


@settings(max_examples=100, deadline=None)
@given(
    project_name=NAME,
    description=DESCRIPTION,
    design_name=NAME,
    frequency_hz=FREQUENCY_HZ,
    total_length_m=LENGTH_M,
    height_m=HEIGHT_M,
    azimuth_deg=AZIMUTH_DEG,
    wire_radius_m=RADIUS_M,
    orientation=ORIENTATION,
    ground=GROUND,
)
def test_project_document_and_repository_round_trip(
    project_name: str,
    description: str,
    design_name: str,
    frequency_hz: float,
    total_length_m: float,
    height_m: float,
    azimuth_deg: float,
    wire_radius_m: float,
    orientation: DipoleOrientation,
    ground: GroundModel,
) -> None:
    project = _project(
        project_name=project_name,
        description=description,
        design_name=design_name,
        frequency_hz=frequency_hz,
        total_length_m=total_length_m,
        height_m=height_m,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        orientation=orientation,
        ground=ground,
    )

    document = document_from_project(project)
    assert document.schema_version == SCHEMA_VERSION
    assert project_from_document(document) == project

    repository = JsonProjectRepository()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "project.antennadesk"
        repository.save(project, path)
        assert repository.load(path) == project


def test_measurement_sessions_round_trip() -> None:
    from uuid import uuid4

    from antennadesk.domain.measurement import (
        Measurement,
        MeasurementPoint,
        MeasurementSession,
    )

    project = _project(
        project_name="Sessions",
        description="",
        design_name="Initial",
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        azimuth_deg=0.0,
        wire_radius_m=0.001,
        orientation=DipoleOrientation.HORIZONTAL,
        ground=GroundModel.free_space(),
    )
    session = MeasurementSession(
        id=uuid4(),
        name="Before tuning",
        created_at=FIXED_NOW,
        design_id=project.designs[0].id,
        location="Back yard",
        conditions="Dry ground",
        notes="First session",
    )
    measurement = Measurement(
        id=uuid4(),
        name="Field sweep",
        created_at=FIXED_NOW,
        reference_impedance_ohm=50.0,
        points=(MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),),
        calibration="SOL",
        session_id=session.id,
    )
    project = project.with_measurement_session(
        session,
        updated_at=FIXED_NOW,
    ).with_measurement(
        measurement,
        updated_at=FIXED_NOW,
    )

    document = document_from_project(project)
    restored = project_from_document(document)

    assert restored == project
    assert restored.measurement_sessions == (session,)
    assert restored.measurements[0].session_id == session.id

    repository = JsonProjectRepository()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "sessions.antennadesk"
        repository.save(project, path)
        assert repository.load(path) == project


@settings(max_examples=50, deadline=None)
@given(
    project_name=NAME,
    description=DESCRIPTION,
    design_name=NAME,
    frequency_hz=FREQUENCY_HZ,
    total_length_m=LENGTH_M,
    height_m=HEIGHT_M,
    azimuth_deg=AZIMUTH_DEG,
    wire_radius_m=RADIUS_M,
    orientation=ORIENTATION,
    ground=GROUND,
)
def test_current_document_migration_is_an_identity(
    project_name: str,
    description: str,
    design_name: str,
    frequency_hz: float,
    total_length_m: float,
    height_m: float,
    azimuth_deg: float,
    wire_radius_m: float,
    orientation: DipoleOrientation,
    ground: GroundModel,
) -> None:
    project = _project(
        project_name=project_name,
        description=description,
        design_name=design_name,
        frequency_hz=frequency_hz,
        total_length_m=total_length_m,
        height_m=height_m,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        orientation=orientation,
        ground=ground,
    )
    data = document_from_project(project).model_dump(mode="json")

    assert migrate_document(data) == data


@settings(max_examples=50, deadline=None)
@given(
    project_name=NAME,
    description=DESCRIPTION,
    design_name=NAME,
    frequency_hz=FREQUENCY_HZ,
    total_length_m=LENGTH_M,
    height_m=HEIGHT_M,
    azimuth_deg=AZIMUTH_DEG,
    wire_radius_m=RADIUS_M,
    ground=GROUND,
)
def test_v1_dipole_document_migrates_to_the_current_project(
    project_name: str,
    description: str,
    design_name: str,
    frequency_hz: float,
    total_length_m: float,
    height_m: float,
    azimuth_deg: float,
    wire_radius_m: float,
    ground: GroundModel,
) -> None:
    project = _project(
        project_name=project_name,
        description=description,
        design_name=design_name,
        frequency_hz=frequency_hz,
        total_length_m=total_length_m,
        height_m=height_m,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        orientation=DipoleOrientation.HORIZONTAL,
        ground=ground,
    )
    data = document_from_project(project).model_dump(mode="json")
    data["schema_version"] = 1
    design = data["project"]["designs"][0]
    design["parameters"].pop("orientation", None)
    design.pop("band_plan", None)
    data["project"].pop("simulation_runs", None)

    migrated = migrate_document(data)
    restored = project_from_document(ProjectDocument.model_validate(migrated))

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert restored == project
