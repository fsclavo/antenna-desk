# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
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
from antennadesk.application.use_cases.update_dipole_design import (
    UpdateDipoleDesign,
    UpdateDipoleDesignCommand,
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


def test_update_dipole_design_returns_new_project(sample_project: Project) -> None:
    design = sample_project.designs[0]
    parameters = design.parameters.with_length(19.5)

    updated = UpdateDipoleDesign().execute(
        UpdateDipoleDesignCommand(
            project=sample_project,
            design_id=design.id,
            parameters=parameters,
        )
    )

    assert updated is not sample_project
    assert updated.designs[0].parameters.total_length_m == pytest.approx(19.5)
    assert sample_project.designs[0].parameters.total_length_m == pytest.approx(20.0)


def test_add_design_variant_duplicates_the_current_design(
    sample_project: Project,
) -> None:
    from antennadesk.application.use_cases.add_design_variant import (
        AddDesignVariant,
        AddDesignVariantCommand,
    )

    source = sample_project.designs[0]
    updated = AddDesignVariant().execute(
        AddDesignVariantCommand(
            project=sample_project,
            source_design_id=source.id,
            name="Shortened",
        )
    )

    assert len(updated.designs) == 2
    new_design = updated.designs[-1]
    assert new_design.id != source.id
    assert new_design.name == "Shortened"
    assert new_design.parameters == source.parameters
    assert new_design.antenna == source.antenna
    assert len(sample_project.designs) == 1


def test_add_design_variant_rejects_duplicate_names(sample_project: Project) -> None:
    from antennadesk.application.use_cases.add_design_variant import (
        AddDesignVariant,
        AddDesignVariantCommand,
    )

    with pytest.raises(ValueError, match="duplicate design name"):
        AddDesignVariant().execute(
            AddDesignVariantCommand(
                project=sample_project,
                source_design_id=sample_project.designs[0].id,
                name=sample_project.designs[0].name,
            )
        )


def test_rename_design_variant(sample_project: Project) -> None:
    from antennadesk.application.use_cases.rename_design_variant import (
        RenameDesignVariant,
        RenameDesignVariantCommand,
    )

    design = sample_project.designs[0]
    updated = RenameDesignVariant().execute(
        RenameDesignVariantCommand(
            project=sample_project,
            design_id=design.id,
            name="Renamed",
        )
    )

    assert updated.designs[0].name == "Renamed"
    assert updated.designs[0].id == design.id
    assert sample_project.designs[0].name == "Initial"


def test_delete_design_variant(sample_project: Project) -> None:
    from antennadesk.application.use_cases.add_design_variant import (
        AddDesignVariant,
        AddDesignVariantCommand,
    )
    from antennadesk.application.use_cases.delete_design_variant import (
        DeleteDesignVariant,
        DeleteDesignVariantCommand,
    )

    with_two = AddDesignVariant().execute(
        AddDesignVariantCommand(
            project=sample_project,
            source_design_id=sample_project.designs[0].id,
            name="Second",
        )
    )
    deleted = DeleteDesignVariant().execute(
        DeleteDesignVariantCommand(
            project=with_two,
            design_id=with_two.designs[0].id,
        )
    )

    assert len(deleted.designs) == 1
    assert deleted.designs[0].name == "Second"


def test_cannot_delete_last_design_variant(sample_project: Project) -> None:
    from antennadesk.application.use_cases.delete_design_variant import (
        DeleteDesignVariant,
        DeleteDesignVariantCommand,
    )

    with pytest.raises(ValueError, match="last design"):
        DeleteDesignVariant().execute(
            DeleteDesignVariantCommand(
                project=sample_project,
                design_id=sample_project.designs[0].id,
            )
        )
