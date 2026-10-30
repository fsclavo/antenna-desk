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
    document["project"]["designs"][0]["antenna_type"] = "unsupported_type"

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


def test_parallel_load_round_trips_with_kind() -> None:
    from antennadesk.domain.antennas.load import ParallelLoad

    load = ParallelLoad(
        id="trap-1",
        wire_id="radiator",
        offset_m=10.0,
        inductance_h=12e-6,
        capacitance_f=30e-12,
    )
    original = _project(
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        "Trap",
    )
    project = original.with_design(
        original.designs[0].with_loads((load,)),
        updated_at=original.updated_at,
    )

    document = document_from_project(project)
    restored = project_from_document(document)

    assert document.project.designs[0].antenna.loads[0].kind.value == "parallel"
    assert restored.designs[0].antenna.loads == (load,)


def test_custom_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.custom import CustomAntennaParameters
    from antennadesk.domain.antennas.feed import FeedPoint
    from antennadesk.domain.antennas.geometry import Point3D
    from antennadesk.domain.antennas.materials import COPPER
    from antennadesk.domain.antennas.wire import Wire

    wire = Wire(
        id="wire-1",
        start=Point3D(-5.0, 0.0, 8.0),
        end=Point3D(5.0, 0.0, 8.0),
        radius_m=0.001,
        material=COPPER,
    )
    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(wire,),
        feed=FeedPoint("wire-1", 5.0),
        generator_id="yagi",
        generator_name="Yagi",
    )
    original = _project(parameters, "Custom")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "custom"


def test_ocfd_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.ocfd import OCFDParameters

    parameters = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        feed_ratio=1.0 / 3.0,
        height_m=10.0,
        azimuth_deg=30.0,
    )
    original = _project(parameters, "OCFD")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "ocfd"


def test_vertical_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.25,
        radial_count=16,
        radial_length_m=5.0,
    )
    original = _project(parameters, "Vertical")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "vertical"


def test_inverted_v_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.inverted_v import InvertedVParameters

    parameters = InvertedVParameters(
        frequency_hz=7_100_000.0,
        leg_length_m=10.6,
        apex_height_m=12.0,
        included_angle_deg=120.0,
    )
    original = _project(parameters, "Inverted V")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "inverted_v"


def test_yagi_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.yagi import nbs_five_element

    parameters = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0)
    original = _project(parameters, "Yagi")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "yagi"


def test_moxon_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.moxon import MoxonParameters

    parameters = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.6,
        depth_m=2.5,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
    )
    original = _project(parameters, "Moxon")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "moxon"


def test_fan_dipole_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement

    parameters = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(
            FanElement(length_m=20.0, included_angle_deg=120.0),
            FanElement(length_m=10.0, included_angle_deg=90.0),
        ),
        apex_height_m=12.0,
    )
    original = _project(parameters, "Fan dipole")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "fan_dipole"


def test_measurement_round_trip() -> None:
    from dataclasses import replace
    from datetime import UTC, datetime
    from uuid import UUID

    from antennadesk.domain.measurement import Measurement, MeasurementPoint

    measurement = Measurement(
        id=UUID("00000000-0000-0000-0000-000000000003"),
        name="Field sweep",
        created_at=datetime(2026, 10, 30, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(MeasurementPoint(7_100_000.0, complex(70.0, 5.0)),),
        source="field.csv",
        calibration="SOL",
        reference_plane="antenna terminals",
        feed_line="10 m RG-58",
        notes="Dry ground",
    )
    original = replace(
        _project(DipoleParameters(7_100_000.0, 20.0, 8.0), "Dipole"), measurements=(measurement,)
    )

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.measurements == (measurement,)


def test_endfed_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.endfed import EndFedParameters

    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=5.0,
    )
    original = _project(parameters, "End-fed")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "endfed"
