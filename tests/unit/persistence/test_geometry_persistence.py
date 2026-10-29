# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.design import AntennaDesignParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.schema import (
    FoldedDipoleParametersPayload,
    LoopParametersPayload,
    ProjectDocument,
    document_from_project,
    project_from_document,
)


def _project(parameters: AntennaDesignParameters, name: str) -> Project:
    return CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name=f"{name} project",
            variant_name=name,
            parameters=parameters,
        )
    )


@pytest.mark.parametrize(
    ("parameters", "payload_type"),
    [
        (
            FoldedDipoleParameters(
                frequency_hz=7_100_000.0,
                total_length_m=20.0,
                height_m=8.0,
                spacing_m=0.2,
            ),
            FoldedDipoleParametersPayload,
        ),
        (
            LoopParameters(
                frequency_hz=7_100_000.0,
                circumference_m=40.0,
                height_m=8.0,
                sides=8,
            ),
            LoopParametersPayload,
        ),
    ],
)
def test_new_geometry_round_trips_through_the_schema(
    parameters: AntennaDesignParameters,
    payload_type: type[object],
) -> None:
    original = _project(parameters, "Geometry")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert isinstance(document.project.designs[0].parameters, payload_type)
    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna == original.designs[0].antenna
    assert restored.designs[0].antenna_type == original.designs[0].antenna_type


def test_schema_rejects_payload_shape_for_the_declared_type() -> None:
    project = _project(
        LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
        ),
        "Mismatch",
    )
    document = document_from_project(project).model_dump(mode="json")
    document["project"]["designs"][0]["antenna_type"] = "folded_dipole"

    with pytest.raises(ValueError):
        ProjectDocument.model_validate(document)


def test_schema_rejects_an_unknown_antenna_type() -> None:
    project = _project(
        LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
        ),
        "Unknown",
    )
    document = document_from_project(project).model_dump(mode="json")
    document["project"]["designs"][0]["antenna_type"] = "yagi"

    with pytest.raises(ValueError, match="unsupported antenna type"):
        ProjectDocument.model_validate(document)


def test_series_loads_round_trip_through_the_schema() -> None:
    from antennadesk.domain.antennas.load import SeriesLoad

    load = SeriesLoad(
        id="load-1",
        wire_id="radiator",
        offset_m=10.0,
        resistance_ohm=25.0,
        inductance_h=12e-6,
        capacitance_f=30e-12,
    )
    original = _project(
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        "Loaded",
    )
    design = original.designs[0].with_loads((load,))
    project = original.with_design(design, updated_at=original.updated_at)

    document = document_from_project(project)
    restored = project_from_document(document)

    assert document.project.designs[0].antenna.loads[0].capacitance_f == pytest.approx(30e-12)
    assert restored.designs[0].antenna.loads == (load,)
    assert restored == project
