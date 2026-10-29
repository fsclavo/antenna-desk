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


def test_record_simulation_run(sample_project: Project) -> None:
    from uuid import uuid4

    from antennadesk.application.use_cases.record_simulation_run import (
        RecordSimulationRun,
        RecordSimulationRunCommand,
    )
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.result import (
        FrequencyResult,
        SimulationResult,
        SimulationStatus,
    )
    from antennadesk.domain.simulation.solver import SolverMetadata
    from antennadesk.domain.simulation.spec import SimulationSpec

    design = sample_project.designs[0]
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))
    result = SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=(
            FrequencyResult(
                frequency_hz=7_100_000.0,
                feed_tag=1,
                feed_segment=11,
                impedance_ohm=complex(50.0, 0.0),
                swr=1.0,
                input_power_w=0.001,
            ),
        ),
    )
    run_id = uuid4()

    project = RecordSimulationRun().execute(
        RecordSimulationRunCommand(
            project=sample_project,
            design_id=design.id,
            result=result,
            run_id=run_id,
            created_at=sample_project.updated_at,
        )
    )

    assert len(project.simulation_runs) == 1
    assert project.simulation_runs[0].id == run_id
    assert project.simulation_runs[0].design_id == design.id


def test_edit_length_rejects_a_folded_dipole(sample_project: Project) -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    design = sample_project.designs[0].with_parameters(
        FoldedDipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        )
    )
    project = sample_project.with_design(design, updated_at=sample_project.updated_at)

    with pytest.raises(ValueError, match="wire dipoles"):
        EditDipoleLength().execute(
            EditDipoleLengthCommand(
                project=project,
                design_id=design.id,
                total_length_m=19.5,
            )
        )


def test_update_design_accepts_a_loop(sample_project: Project) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    design = sample_project.designs[0]
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=8,
    )

    updated = UpdateDipoleDesign().execute(
        UpdateDipoleDesignCommand(
            project=sample_project,
            design_id=design.id,
            parameters=parameters,
        )
    )

    assert updated.designs[0].antenna_type == "loop"
    assert updated.designs[0].parameters is parameters
    assert len(updated.designs[0].antenna.wires) == 8
