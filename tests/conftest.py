from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.json_repository import JsonProjectRepository

PROJECT_ID = UUID("00000000-0000-0000-0000-000000000001")
DESIGN_ID = UUID("00000000-0000-0000-0000-000000000002")
FIXED_NOW = datetime(2026, 10, 29, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def dipole_parameters() -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        azimuth_deg=0.0,
        wire_radius_m=0.001,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )


@pytest.fixture
def sample_project(dipole_parameters: DipoleParameters) -> Project:
    return CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="40 m dipole",
            variant_name="Initial",
            parameters=dipole_parameters,
            description="Half-wave dipole for the 40 m band.",
        ),
        project_id=PROJECT_ID,
        design_id=DESIGN_ID,
        now=FIXED_NOW,
    )


@pytest.fixture
def repository() -> JsonProjectRepository:
    return JsonProjectRepository()
