# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from antennadesk.application.use_cases.edit_dipole_length import (
    EditDipoleLength,
    EditDipoleLengthCommand,
)
from antennadesk.application.use_cases.open_project import OpenProject
from antennadesk.application.use_cases.save_project import SaveProject
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.json_repository import JsonProjectRepository

EXAMPLE_PROJECT = Path(__file__).resolve().parents[2] / "examples" / "dipole_40m.antennadesk"


def test_create_save_and_open_a_dipole_project(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"

    SaveProject(repository).execute(sample_project, path)
    loaded = OpenProject(repository).execute(path)

    assert loaded == sample_project
    assert loaded.designs[0].parameters.total_length_m == pytest.approx(20.0)
    assert loaded.designs[0].antenna.wires[0].length_m == pytest.approx(20.0)


def test_editing_length_keeps_previous_snapshot_unchanged(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    SaveProject(repository).execute(sample_project, path)
    loaded = OpenProject(repository).execute(path)
    design = loaded.designs[0]

    edited = EditDipoleLength().execute(
        EditDipoleLengthCommand(
            project=loaded,
            design_id=design.id,
            total_length_m=19.5,
            updated_at=loaded.updated_at + timedelta(hours=1),
        )
    )

    assert edited is not loaded
    assert edited.designs[0].parameters.total_length_m == pytest.approx(19.5)
    assert edited.designs[0].antenna.wires[0].length_m == pytest.approx(19.5)
    assert loaded.designs[0].parameters.total_length_m == pytest.approx(20.0)
    assert loaded.designs[0].antenna.wires[0].length_m == pytest.approx(20.0)

    edited_path = tmp_path / "dipole-shortened.antennadesk"
    SaveProject(repository).execute(edited, edited_path)
    reopened = OpenProject(repository).execute(edited_path)
    assert reopened.designs[0].parameters.total_length_m == pytest.approx(19.5)


def test_invalid_dipole_is_rejected_before_persistence() -> None:
    with pytest.raises(ValueError):
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=0.0,
            height_m=8.0,
        )


def test_example_project_opens(repository: JsonProjectRepository) -> None:
    project = OpenProject(repository).execute(EXAMPLE_PROJECT)

    assert project.name == "40 m dipole"
    assert len(project.designs) == 1
    assert project.designs[0].parameters.total_length_m == pytest.approx(20.0)
    assert project.designs[0].antenna.wires[0].length_m == pytest.approx(20.0)
