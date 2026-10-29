from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.application.use_cases.edit_dipole_length import (
    EditDipoleLength,
    EditDipoleLengthCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.projects.project import Project


def test_create_dipole_project_uses_supplied_timestamp(
    dipole_parameters: DipoleParameters,
) -> None:
    timestamp = datetime(2026, 10, 29, 12, 0, 0, tzinfo=UTC)

    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="40 m dipole",
            variant_name="Initial",
            parameters=dipole_parameters,
        ),
        now=timestamp,
    )

    assert project.created_at == timestamp
    assert project.updated_at == timestamp
    assert len(project.designs) == 1
    assert project.designs[0].name == "Initial"


@pytest.mark.parametrize(
    ("project_name", "variant_name"),
    [
        ("", "Initial"),
        ("   ", "Initial"),
        ("40 m dipole", ""),
        ("40 m dipole", "   "),
    ],
)
def test_create_dipole_rejects_empty_names(
    dipole_parameters: DipoleParameters,
    project_name: str,
    variant_name: str,
) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        CreateDipoleProject().execute(
            CreateDipoleProjectCommand(
                project_name=project_name,
                variant_name=variant_name,
                parameters=dipole_parameters,
            )
        )


def test_edit_length_rejects_unknown_design(sample_project: Project) -> None:
    with pytest.raises(KeyError):
        EditDipoleLength().execute(
            EditDipoleLengthCommand(
                project=sample_project,
                design_id=uuid4(),
                total_length_m=19.5,
            )
        )
