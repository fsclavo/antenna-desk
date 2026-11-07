# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    PowerBudget,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.reporting.construction_sheet import render_construction_sheet


def _make_result() -> SimulationResult:
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))
    frequency = FrequencyResult(
        frequency_hz=7_100_000.0,
        feed_tag=1,
        feed_segment=11,
        impedance_ohm=complex(50.0, 0.0),
        swr=1.0,
        input_power_w=0.001,
        power_budget=PowerBudget(0.001, 0.0009, 0.0001, 0.0, 90.0),
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=(frequency,),
        duration_s=0.1,
        started_at=datetime(2026, 10, 29, tzinfo=UTC),
        finished_at=datetime(2026, 10, 29, tzinfo=UTC),
    )


def test_construction_sheet_contains_dimensions_and_result(sample_project: Project) -> None:
    design = sample_project.designs[0]
    sheet = render_construction_sheet(sample_project, design, _make_result())

    assert "construction sheet" in sheet
    assert "Total wire length" in sheet
    assert "10.0000 m" in sheet
    assert "Feed height above ground" in sheet
    assert "SWR" in sheet
    assert "1.000" in sheet
    assert "90.00 %" in sheet
    assert "a" * 64 in sheet
    assert "Construction notes" in sheet


def test_construction_sheet_works_without_a_result(sample_project: Project) -> None:
    sheet = render_construction_sheet(
        sample_project,
        sample_project.designs[0],
        None,
    )
    assert "No result yet." in sheet


def test_construction_sheet_escapes_user_text(sample_project: Project) -> None:
    project = replace(sample_project, name="<script>alert(1)</script>")
    sheet = render_construction_sheet(project, project.designs[0], None)

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in sheet
    assert "<script>alert(1)</script>" not in sheet


def test_vertical_construction_sheet_uses_feed_height(sample_project: Project) -> None:
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
    sheet = render_construction_sheet(sample_project, vertical_design, None)

    assert "<td>vertical</td>" in sheet
    assert "First leg (from wire start)" in sheet
    assert "2.5000 m" in sheet
    assert "Wire height at start" in sheet
    assert "Feed height above ground" in sheet
    assert "4.5000 m" in sheet
    assert "Azimuth" in sheet


def test_t2fd_construction_sheet_lists_the_resistor_and_transformer() -> None:
    from antennadesk.application.use_cases.create_dipole_project import (
        CreateDipoleProject,
        CreateDipoleProjectCommand,
    )
    from antennadesk.domain.antennas.t2fd import T2FDParameters

    parameters = T2FDParameters(
        frequency_hz=3_500_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=26.0,
        spacing_m=0.9,
        height_m=12.0,
        termination_resistance_ohm=800.0,
        transformer_ratio=16.0,
    )
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="Broadband",
            variant_name="T2FD",
            parameters=parameters,
        )
    )

    sheet = render_construction_sheet(project, project.designs[0], None)

    assert "terminated folded dipole (T2FD)" in sheet
    assert "26.0000 m each" in sheet
    assert "800 Ω non-inductive" in sheet
    assert "16:1" in sheet
    assert "Load 1 (series)" in sheet


def test_folded_dipole_construction_sheet(sample_project: Project) -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    design = sample_project.designs[0]
    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )
    folded = design.with_parameters(parameters)
    sheet = render_construction_sheet(sample_project, folded, None)

    assert "Element length" in sheet
    assert "Spacing" in sheet
    assert "Total conductor length" in sheet
    assert "End connector length" in sheet
    assert "40.4000 m" in sheet


def test_inverted_l_construction_sheet(sample_project: Project) -> None:
    from antennadesk.domain.antennas.inverted_l import InvertedLParameters

    design = sample_project.designs[0]
    parameters = InvertedLParameters(
        frequency_hz=7_100_000.0,
        vertical_height_m=10.0,
        horizontal_length_m=20.0,
        base_height_m=1.0,
        azimuth_deg=35.0,
    )
    inverted_l = design.with_parameters(parameters)
    sheet = render_construction_sheet(sample_project, inverted_l, None)

    assert "Vertical section" in sheet
    assert "Horizontal top run" in sheet
    assert "Total wire length" in sheet
    assert "30.0000 m" in sheet
    assert "11.0000 m" in sheet
    assert "Feed the base of the vertical section" in sheet


def test_loop_construction_sheet(sample_project: Project) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    design = sample_project.designs[0]
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=8,
    )
    loop = design.with_parameters(parameters)
    sheet = render_construction_sheet(sample_project, loop, None)

    assert "Circumference" in sheet
    assert "Side length" in sheet
    assert "Feed side" in sheet
    assert "5.0000 m" in sheet
    assert "8 equal sides" in sheet


def test_construction_sheet_lists_series_loads(sample_project: Project) -> None:
    from antennadesk.domain.antennas.load import SeriesLoad

    load = SeriesLoad("load-1", "radiator", 10.0, resistance_ohm=50.0)
    design = sample_project.designs[0].with_loads((load,))
    sheet = render_construction_sheet(sample_project, design, None)

    assert "Load 1" in sheet
    assert "radiator @ 10.000 m" in sheet
    assert "R=50 Ω" in sheet


def test_construction_sheet_includes_estimator_provenance(sample_project: Project) -> None:
    from antennadesk.domain.projects.project import DesignProvenance

    design = replace(
        sample_project.designs[0],
        provenance=DesignProvenance(
            method_id="dipole.half_wave_end_effect",
            confidence="empirical",
            tolerance_m=0.6,
            source_ids=("arrl.antenna_book.dipole.end_effect",),
        ),
    )
    sheet = render_construction_sheet(sample_project, design, _make_result())

    assert "Dimension source" in sheet
    assert "dipole.half_wave_end_effect" in sheet
    assert "Estimate confidence" in sheet
    assert "arrl.antenna_book.dipole.end_effect" in sheet


def test_loaded_vertical_construction_sheet_lists_the_loading_coil() -> None:
    from antennadesk.application.use_cases.create_dipole_project import (
        CreateDipoleProject,
        CreateDipoleProjectCommand,
    )
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
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="Mobile",
            variant_name="Loaded vertical",
            parameters=parameters,
        )
    )

    sheet = render_construction_sheet(project, project.designs[0], None)

    assert "loaded vertical" in sheet
    assert "Loading coil" in sheet
    assert "12.0000 µH" in sheet
    assert "Load 1 (series)" in sheet
    assert "radiator @ 1.000 m" in sheet


def test_trap_dipole_construction_sheet_lists_both_traps() -> None:
    from antennadesk.application.use_cases.create_dipole_project import (
        CreateDipoleProject,
        CreateDipoleProjectCommand,
    )
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
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="Two bands",
            variant_name="Trap dipole",
            parameters=parameters,
        )
    )

    sheet = render_construction_sheet(project, project.designs[0], None)

    assert "trap dipole" in sheet
    assert "5.0000 m, 15.0000 m from wire start" in sheet
    assert "14.100000 MHz" in sheet
    assert "Load 1 (parallel)" in sheet
    assert "Load 2 (parallel)" in sheet


def test_construction_sheet_reports_realized_gain_and_losses(sample_project: Project) -> None:
    from antennadesk.domain.simulation.result import FarFieldPoint

    point = FarFieldPoint(
        theta_deg=90.0,
        phi_deg=0.0,
        gain_vertical_db=2.15,
        gain_horizontal_db=None,
        gain_total_db=2.15,
        axial_ratio=1.0,
        tilt_deg=0.0,
        polarization="linear",
        e_theta_magnitude_v_per_m=None,
        e_theta_phase_deg=None,
        e_phi_magnitude_v_per_m=None,
        e_phi_phase_deg=None,
    )
    result = _make_result()
    frequency = replace(
        result.frequencies[0],
        far_field=(point,),
        directivity_db=2.20,
        realized_gain_db=1.85,
        mismatch_loss_db=0.20,
        feed_line_loss_db=0.10,
        network_loss_db=0.05,
    )
    result = replace(result, frequencies=(frequency,))

    sheet = render_construction_sheet(sample_project, sample_project.designs[0], result)

    assert "Max power gain (NEC)" in sheet
    assert "2.15 dBi" in sheet
    assert "Max directivity" in sheet
    assert "2.20 dBi" in sheet
    assert "Max realized gain" in sheet
    assert "1.85 dBi" in sheet
    assert "Mismatch loss" in sheet
    assert "0.200 dB" in sheet


def test_construction_sheet_lists_transmission_lines(sample_project: Project) -> None:
    from antennadesk.domain.antennas.transmission_line import TransmissionLine

    line = TransmissionLine(
        id="line-1",
        start_wire_id="radiator",
        start_offset_m=0.0,
        end_wire_id="radiator",
        end_offset_m=10.0,
        characteristic_impedance_ohm=300.0,
        length_m=8.0,
        velocity_factor=0.9,
    )
    design = sample_project.designs[0].with_transmission_lines((line,))
    project = sample_project.with_design(design, updated_at=sample_project.updated_at)

    sheet = render_construction_sheet(project, design, None)

    assert "Transmission line 1" in sheet
    assert "300 Ω" in sheet
    assert "VF 0.9" in sheet


def test_zepp_construction_sheet_lists_the_stub_and_choke(sample_project: Project) -> None:
    from antennadesk.domain.antennas.zepp import zepp_parameters

    design = sample_project.designs[0].with_parameters(zepp_parameters())
    project = sample_project.with_design(design, updated_at=sample_project.updated_at)

    sheet = render_construction_sheet(project, design, None)

    assert "Radiator length" in sheet
    assert "Matching stub length" in sheet
    assert "Conductor spacing" in sheet
    assert "Estimated stub impedance" in sheet
    assert "1:1 common-mode choke" in sheet
    assert "10.0283" in sheet
