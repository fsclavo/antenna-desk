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
from antennadesk.domain.antennas.loop import LoopOrientation, LoopParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.schema import (
    FoldedDipoleParametersPayload,
    LoopParametersPayload,
    MagneticLoopParametersPayload,
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
        feed_transformer_ratio=4.0,
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
        transformer_ratio=4.0,
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


def test_horizontal_loop_parameters_round_trip() -> None:
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
        orientation=LoopOrientation.HORIZONTAL,
        azimuth_deg=35.0,
    )
    original = _project(parameters, "Horizontal loop")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert isinstance(document.project.designs[0].parameters, LoopParametersPayload)
    assert document.project.designs[0].parameters.orientation == LoopOrientation.HORIZONTAL
    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna == original.designs[0].antenna


def test_magnetic_loop_parameters_round_trip() -> None:
    parameters = MagneticLoopParameters(
        frequency_hz=7_100_000.0,
        diameter_m=1.0,
        tuning_capacitance_f=180e-12,
        height_m=1.5,
        sides=36,
        gap_length_m=0.04,
        capacitor_esr_ohm=0.2,
        azimuth_deg=35.0,
        wire_radius_m=0.005,
    )
    original = _project(parameters, "Magnetic loop")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert isinstance(document.project.designs[0].parameters, MagneticLoopParametersPayload)
    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna == original.designs[0].antenna
    assert restored.designs[0].antenna_type == "magnetic_loop"


def test_inverted_l_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.inverted_l import InvertedLParameters

    parameters = InvertedLParameters(
        frequency_hz=7_100_000.0,
        vertical_height_m=10.0,
        horizontal_length_m=20.0,
        base_height_m=1.0,
        azimuth_deg=35.0,
    )
    original = _project(parameters, "Inverted L")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "inverted_l"


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


def test_folded_yagi_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.yagi import nbs_five_element

    parameters = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=8.0,
        folded_driven=True,
        folded_spacing_m=0.1,
    )
    original = _project(parameters, "Folded Yagi")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].parameters.driven_folded is True
    assert restored.designs[0].parameters.driven_fold_spacing_m == pytest.approx(0.1)


def test_vertical_yagi_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.polarization import Polarization
    from antennadesk.domain.antennas.yagi import nbs_five_element

    parameters = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=8.0,
        azimuth_deg=35.0,
        polarization=Polarization.VERTICAL,
    )
    original = _project(parameters, "Vertical Yagi")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].parameters.polarization is Polarization.VERTICAL
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


def test_vertical_moxon_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.moxon import MoxonParameters
    from antennadesk.domain.antennas.polarization import Polarization

    parameters = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.6,
        depth_m=2.5,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
        polarization=Polarization.VERTICAL,
    )
    original = _project(parameters, "Vertical Moxon")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].parameters.polarization is Polarization.VERTICAL
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
        transformer_ratio=49.0,
        counterpoise_length_m=2.5,
        counterpoise_height_m=0.2,
        counterpoise_azimuth_deg=210.0,
    )
    original = _project(parameters, "End-fed")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "endfed"


def test_j_pole_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.j_pole import JPoleParameters

    parameters = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        folded=True,
    )
    original = _project(parameters, "Slim Jim")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "j_pole"


def test_ringo_parameters_round_trip() -> None:
    from antennadesk.domain.antennas.ringo import RingoParameters

    parameters = RingoParameters(
        frequency_hz=50_100_000.0,
        radiator_height_m=3.0,
        ring_diameter_m=0.33,
        ring_height_m=0.1,
        ring_sides=8,
    )
    original = _project(parameters, "Ringo")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "ringo"


def test_design_provenance_round_trips_through_the_schema() -> None:
    from antennadesk.domain.projects.project import DesignProvenance

    project = _project(
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
        "Dipole",
    )
    design = project.designs[0]
    provenance = DesignProvenance(
        method_id="dipole.half_wave_end_effect",
        confidence="empirical",
        assumptions=("estimator.assumption.height_and_ground",),
        warnings=("estimator.warning.starting_point",),
        tolerance_m=0.3,
        source_ids=("arrl.antenna_book.dipole.end_effect",),
    )
    project = project.with_design(
        design.with_parameters(design.parameters, provenance=provenance),
        updated_at=project.updated_at,
    )

    restored = project_from_document(document_from_project(project))

    assert restored.designs[0].provenance == provenance


def test_matching_network_round_trips_through_the_project_schema() -> None:
    from antennadesk.domain.antennas.matching_network import LNetwork

    project = _project(
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
        "Dipole",
    )
    network = LNetwork(
        series_inductance_h=1e-6,
        shunt_capacitance_f=100e-12,
        shunt_at_input=True,
    )
    project = project.with_matching_network(network, updated_at=project.updated_at)

    restored = project_from_document(document_from_project(project))

    assert restored.matching_network == network


def test_pi_matching_network_round_trips_through_the_project_schema() -> None:
    from antennadesk.domain.antennas.matching_network import PiNetwork

    project = _project(
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
        "Dipole",
    )
    network = PiNetwork(
        input_shunt_capacitance_f=100e-12,
        series_inductance_h=1e-6,
        output_shunt_capacitance_f=120e-12,
        q_factor=200.0,
    )
    project = project.with_matching_network(network, updated_at=project.updated_at)

    restored = project_from_document(document_from_project(project))

    assert restored.matching_network == network


def test_t_matching_network_round_trips_through_the_project_schema() -> None:
    from antennadesk.domain.antennas.matching_network import TNetwork

    project = _project(
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
        "Dipole",
    )
    network = TNetwork(
        input_series_inductance_h=1e-6,
        shunt_capacitance_f=100e-12,
        output_series_inductance_h=1e-6,
    )
    project = project.with_matching_network(network, updated_at=project.updated_at)

    restored = project_from_document(document_from_project(project))

    assert restored.matching_network == network


def test_loaded_vertical_parameters_and_coil_round_trip() -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=1.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=12e-6,
        loading_coil_resistance_ohm=0.5,
    )
    original = _project(parameters, "Loaded vertical")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna.loads == original.designs[0].antenna.loads
    assert restored.designs[0].antenna.loads[0].id == "loading-coil"
    assert restored.designs[0].antenna_type == "vertical"


def test_trap_dipole_parameters_and_traps_round_trip() -> None:
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    parameters = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=10e-6,
        height_m=12.0,
    )
    original = _project(parameters, "Trap dipole")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "trap_dipole"
    assert [load.id for load in restored.designs[0].antenna.loads] == [
        "trap-left",
        "trap-right",
    ]
    assert restored == original


def test_t2fd_parameters_and_termination_round_trip() -> None:
    from antennadesk.domain.antennas.dipole import DipoleOrientation
    from antennadesk.domain.antennas.t2fd import T2FDParameters

    parameters = T2FDParameters(
        frequency_hz=3_500_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=26.0,
        spacing_m=0.9,
        height_m=12.0,
        orientation=DipoleOrientation.VERTICAL,
        termination_resistance_ohm=820.0,
        transformer_ratio=16.0,
        azimuth_deg=45.0,
    )
    original = _project(parameters, "T2FD")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna_type == "t2fd"
    assert [load.id for load in restored.designs[0].antenna.loads] == [
        "t2fd-termination",
    ]
    assert restored.designs[0].antenna.loads[0].resistance_ohm == 820.0
    assert restored == original


def test_endfed_preset_round_trips() -> None:
    from antennadesk.domain.antennas.endfed import EndFedParameters, EndFedPreset

    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=2.0,
        transformer_ratio=49.0,
        counterpoise_length_m=2.0,
        preset=EndFedPreset.SLOPER,
    )
    original = _project(parameters, "Sloper")

    document = document_from_project(original)
    restored = project_from_document(document)

    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].parameters.preset is EndFedPreset.SLOPER
    assert restored.designs[0].antenna_type == "endfed"


def test_transmission_lines_round_trip_through_the_schema() -> None:
    from antennadesk.domain.antennas.transmission_line import TransmissionLine

    line = TransmissionLine(
        id="line-1",
        start_wire_id="radiator",
        start_offset_m=0.0,
        end_wire_id="radiator",
        end_offset_m=20.0,
        characteristic_impedance_ohm=300.0,
        length_m=10.0,
        velocity_factor=0.9,
    )
    original = _project(
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        "Transmission line",
    )
    design = original.designs[0].with_transmission_lines((line,))
    project = original.with_design(design, updated_at=original.updated_at)

    document = document_from_project(project)
    restored = project_from_document(document)

    assert restored.designs[0].antenna.transmission_lines == (line,)
    assert restored == project
