# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.projects.project import DesignVariant, Project


def test_sample_project_is_valid(sample_project: Project) -> None:
    assert len(sample_project.designs) == 1
    design = sample_project.designs[0]
    assert design.antenna_type == "wire_dipole"
    assert design.antenna == design.parameters.to_antenna(name=design.antenna.name)


def test_design_rejects_inconsistent_antenna(sample_project: Project) -> None:
    design = sample_project.designs[0]
    changed_parameters = design.parameters.with_length(19.0)

    with pytest.raises(ValueError, match="inconsistent"):
        DesignVariant(
            id=design.id,
            name=design.name,
            antenna_type=design.antenna_type,
            parameters=changed_parameters,
            antenna=design.antenna,
        )


def test_design_with_parameters_returns_a_new_value(sample_project: Project) -> None:
    design = sample_project.designs[0]
    edited = design.with_parameters(design.parameters.with_length(19.5))

    assert edited is not design
    assert edited.id == design.id
    assert edited.name == design.name
    assert edited.parameters.total_length_m == pytest.approx(19.5)
    assert edited.antenna.wires[0].length_m == pytest.approx(19.5)
    assert design.parameters.total_length_m == pytest.approx(20.0)


def test_project_rejects_duplicate_design_ids(sample_project: Project) -> None:
    design = sample_project.designs[0]
    duplicate = replace(design, name="Second variant")

    with pytest.raises(ValueError, match="duplicate design id"):
        Project(
            id=sample_project.id,
            name=sample_project.name,
            description=sample_project.description,
            created_at=sample_project.created_at,
            updated_at=sample_project.updated_at,
            designs=(design, duplicate),
        )


def test_project_rejects_duplicate_design_names(sample_project: Project) -> None:
    design = sample_project.designs[0]
    duplicate = replace(design, id=uuid4())

    with pytest.raises(ValueError, match="duplicate design name"):
        Project(
            id=sample_project.id,
            name=sample_project.name,
            description=sample_project.description,
            created_at=sample_project.created_at,
            updated_at=sample_project.updated_at,
            designs=(design, duplicate),
        )


def test_project_rejects_naive_timestamps(sample_project: Project) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(sample_project, created_at=datetime(2026, 10, 29, 12, 0, 0))


def test_project_rejects_inverted_timestamps(sample_project: Project) -> None:
    with pytest.raises(ValueError, match="earlier"):
        replace(
            sample_project,
            updated_at=sample_project.created_at - timedelta(seconds=1),
        )


def test_project_with_design_replaces_without_mutating_original(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    updated_design = design.with_parameters(design.parameters.with_length(19.5))
    updated_at = sample_project.updated_at + timedelta(hours=1)

    edited_project = sample_project.with_design(updated_design, updated_at=updated_at)

    assert edited_project is not sample_project
    assert edited_project.updated_at == updated_at
    assert edited_project.designs[0].parameters.total_length_m == pytest.approx(19.5)
    assert sample_project.designs[0].parameters.total_length_m == pytest.approx(20.0)


def test_project_with_new_design_appends(sample_project: Project) -> None:
    new_id = uuid4()
    new_parameters: DipoleParameters = sample_project.designs[0].parameters.with_length(19.0)
    new_design = DesignVariant(
        id=new_id,
        name="Shortened",
        antenna_type="wire_dipole",
        parameters=new_parameters,
        antenna=new_parameters.to_antenna(name="Shortened"),
    )
    updated_at = sample_project.updated_at + timedelta(hours=1)

    edited_project = sample_project.with_design(new_design, updated_at=updated_at)

    assert len(edited_project.designs) == 2
    assert edited_project.design_by_id(new_id) == new_design


def test_missing_design_raises_key_error(sample_project: Project) -> None:
    with pytest.raises(KeyError):
        sample_project.design_by_id(uuid4())
