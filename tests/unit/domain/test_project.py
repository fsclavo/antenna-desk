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


def _simulation_run(project: Project, *, run_id: object | None = None) -> object:
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.result import (
        FrequencyResult,
        SimulationResult,
        SimulationStatus,
    )
    from antennadesk.domain.simulation.run import SimulationRun
    from antennadesk.domain.simulation.solver import SolverMetadata
    from antennadesk.domain.simulation.spec import SimulationSpec

    design = project.designs[0]
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(design.parameters.frequency_hz))
    return SimulationRun(
        id=run_id if run_id is not None else uuid4(),  # type: ignore[arg-type]
        design_id=design.id,
        created_at=project.updated_at,
        result=SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=SolverMetadata(name="nec2c", version="1.3.3"),
            frequencies=(
                FrequencyResult(
                    frequency_hz=design.parameters.frequency_hz,
                    feed_tag=1,
                    feed_segment=11,
                    impedance_ohm=complex(50.0, 0.0),
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
        ),
    )


def test_project_with_simulation_run(sample_project: Project) -> None:
    run = _simulation_run(sample_project)
    project = sample_project.with_simulation_run(  # type: ignore[arg-type]
        run,
        updated_at=sample_project.updated_at + timedelta(hours=1),
    )

    assert len(project.simulation_runs) == 1
    assert project.latest_simulation_run(sample_project.designs[0].id) == run
    assert len(sample_project.simulation_runs) == 0


def test_project_rejects_run_for_unknown_design(sample_project: Project) -> None:
    from dataclasses import replace

    run = _simulation_run(sample_project)
    invalid = replace(run, design_id=uuid4())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="unknown design"):
        sample_project.with_simulation_run(  # type: ignore[arg-type]
            invalid,
            updated_at=sample_project.updated_at + timedelta(hours=1),
        )
