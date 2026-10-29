# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.application.use_cases.edit_dipole_length import (
    EditDipoleLength,
    EditDipoleLengthCommand,
)
from antennadesk.application.use_cases.open_project import OpenProject
from antennadesk.application.use_cases.save_project import SaveProject
from antennadesk.domain.antennas.design import AntennaDesignParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
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


def test_vertical_dipole_project_round_trip(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.dipole import DipoleOrientation

    design = sample_project.designs[0]
    parameters = replace(
        design.parameters,
        orientation=DipoleOrientation.VERTICAL,
        total_length_m=5.0,
        height_m=2.0,
        wire_radius_m=0.3,
        frequency_hz=30_000_000.0,
    )
    vertical_design = design.with_parameters(parameters)
    project = sample_project.with_design(
        vertical_design,
        updated_at=sample_project.updated_at + timedelta(hours=1),
    )
    path = tmp_path / "vertical.antennadesk"

    SaveProject(repository).execute(project, path)
    loaded = OpenProject(repository).execute(path)

    loaded_design = loaded.designs[0]
    assert loaded_design.parameters.orientation is DipoleOrientation.VERTICAL
    assert loaded_design.antenna.wires[0].start.z_m == pytest.approx(2.0)
    assert loaded_design.antenna.wires[0].end.z_m == pytest.approx(7.0)


def test_example_project_migrates_to_the_current_schema(
    repository: JsonProjectRepository,
) -> None:
    from antennadesk.domain.antennas.dipole import DipoleOrientation

    project = OpenProject(repository).execute(EXAMPLE_PROJECT)
    assert project.designs[0].parameters.orientation is DipoleOrientation.HORIZONTAL
    assert project.simulation_runs == ()


@pytest.mark.parametrize(
    "parameters",
    [
        pytest.param(
            FoldedDipoleParameters(
                frequency_hz=7_100_000.0,
                total_length_m=20.0,
                height_m=8.0,
                spacing_m=0.2,
            ),
            id="folded",
        ),
        pytest.param(
            LoopParameters(
                frequency_hz=7_100_000.0,
                circumference_m=40.0,
                height_m=8.0,
                sides=8,
            ),
            id="loop",
        ),
    ],
)
def test_new_geometry_project_round_trip(
    repository: JsonProjectRepository,
    tmp_path: Path,
    parameters: AntennaDesignParameters,
) -> None:
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="Geometry",
            variant_name="Initial",
            parameters=parameters,
        )
    )
    path = tmp_path / "geometry.antennadesk"

    SaveProject(repository).execute(project, path)
    loaded = OpenProject(repository).execute(path)

    assert loaded == project
    assert loaded.designs[0].antenna_type == project.designs[0].antenna_type
    assert len(loaded.designs[0].antenna.wires) == len(project.designs[0].antenna.wires)
