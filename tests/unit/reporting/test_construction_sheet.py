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
    assert "Wire schedule" in sheet
    assert design.antenna.wires[0].id in sheet
    assert "Bill of materials" in sheet
    assert "Total conductor" in sheet
    assert "Feed wire" in sheet
    assert "SWR" in sheet
    assert "1.000" in sheet
    assert "90.00 %" in sheet
    assert "a" * 64 in sheet
    assert "Construction notes" in sheet


def test_construction_sheet_embeds_a_figure(sample_project: Project) -> None:
    sheet = render_construction_sheet(
        sample_project,
        sample_project.designs[0],
        None,
        figure_png_data_uri="data:image/png;base64,AAAA",
    )

    assert 'src="data:image/png;base64,AAAA"' in sheet
    assert "construction-figure" in sheet


def test_construction_sheet_embeds_an_installation_view(sample_project: Project) -> None:
    sheet = render_construction_sheet(
        sample_project,
        sample_project.designs[0],
        None,
        figure_png_data_uri="data:image/png;base64,AAAA",
        auxiliary_png_data_uri="data:image/png;base64,BBBB",
    )

    assert "installation-figure" in sheet
    assert 'src="data:image/png;base64,BBBB"' in sheet
    assert "Installation view (front)" in sheet


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


def test_horizontal_loop_construction_sheet(sample_project: Project) -> None:
    from antennadesk.domain.antennas.loop import LoopOrientation, LoopParameters

    design = sample_project.designs[0]
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
        orientation=LoopOrientation.HORIZONTAL,
    )
    loop = design.with_parameters(parameters)
    sheet = render_construction_sheet(sample_project, loop, None)

    assert "<td>horizontal</td>" in sheet
    assert "Plane height" in sheet
    assert "8.0000 m" in sheet
    assert "in a horizontal plane" in sheet


def test_folded_yagi_construction_sheet_lists_the_fold(sample_project: Project) -> None:
    from antennadesk.domain.antennas.yagi import nbs_five_element

    design = sample_project.designs[0]
    yagi = design.with_parameters(
        nbs_five_element(
            frequency_hz=50_100_000.0,
            height_m=8.0,
            folded_driven=True,
            folded_spacing_m=0.1,
        )
    )
    sheet = render_construction_sheet(sample_project, yagi, None)

    assert "Folded driven element" in sheet
    assert "Fold spacing" in sheet
    assert "0.1000 m" in sheet
    assert "second conductor remains passive" in sheet


def test_top_loaded_vertical_construction_sheet_lists_the_hat(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    design = sample_project.designs[0]
    vertical = design.with_parameters(
        VerticalParameters(
            frequency_hz=7_100_000.0,
            height_m=5.0,
            base_height_m=0.25,
            radial_count=4,
            radial_length_m=2.5,
            top_hat_enabled=True,
            top_hat_radius_m=0.75,
            top_hat_wire_count=4,
        )
    )
    sheet = render_construction_sheet(sample_project, vertical, None)

    assert "Top hat wires" in sheet
    assert "Top hat radius" in sheet
    assert "0.7500 m" in sheet
    assert "top-hat wires of 0.7500 m" in sheet


def test_scv_construction_sheet_lists_the_array_wires(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.scv import ScvKind, scv_parameters

    design = sample_project.designs[0]
    scv = design.with_parameters(scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0))
    sheet = render_construction_sheet(sample_project, scv, None)

    assert "Bobtail curtain" in sheet
    assert "Horizontal segment" in sheet
    assert "19.0500 m each" in sheet
    assert "three vertical wires of 11.5824 m" in sheet
    assert "two top wires of 19.0500 m each" in sheet
    assert "top junction of the center vertical" in sheet


def test_typed_transmission_line_doublet_construction_sheet(
    sample_project: Project,
) -> None:
    from datetime import UTC, datetime

    from antennadesk.domain.antennas.transmission_line_doublet import (
        DoubletPreset,
        doublet_starting_parameters,
    )
    from antennadesk.domain.optimization.summary import (
        OptimizationMode,
        OptimizationSummary,
    )

    design = sample_project.designs[0]
    doublet = design.with_parameters(doublet_starting_parameters(DoubletPreset.G5RV))
    doublet = doublet.with_optimization_summary(
        OptimizationSummary(
            mode=OptimizationMode.BAND_AWARE,
            objective="min_swr",
            status="converged",
            budget_profile="balanced",
            evaluations=180,
            seed=3,
            best_values={"dipole_total_length_m": 31.1},
            best_metrics={"swr": 1.2},
            completed_at=datetime(2026, 11, 7, 12, 0, tzinfo=UTC),
        )
    )
    sheet = render_construction_sheet(sample_project, doublet, None)

    assert "G5RV" in sheet
    assert "Matching line" in sheet
    assert "matching line" in sheet
    assert "31.1000 m" in sheet
    assert "Last optimization" in sheet
    assert "band_aware" in sheet


def test_sagged_dipole_construction_sheet_reports_the_sag(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.dipole import DipoleParameters

    design = sample_project.designs[0]
    sagged = design.with_parameters(
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
            sag_m=1.2,
        )
    )
    sheet = render_construction_sheet(sample_project, sagged, None)

    assert "Center sag" in sheet
    assert "1.2000 m" in sheet
    assert "let the center sag" in sheet


def test_loaded_dipole_construction_sheet_lists_the_coils(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters

    design = sample_project.designs[0]
    dipole = design.with_parameters(loaded_dipole_parameters(total_length_m=18.0))
    sheet = render_construction_sheet(sample_project, dipole, None)

    assert "Loaded dipole" in sheet
    assert "Link offset" in sheet
    assert "loading coils" in sheet.lower()


def test_hexbeam_construction_sheet_lists_the_bent_elements(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters

    design = sample_project.designs[0]
    hexbeam = design.with_parameters(published_hexbeam_parameters())
    sheet = render_construction_sheet(sample_project, hexbeam, None)

    assert "Hexbeam" in sheet
    assert "Driver half-length" in sheet
    assert "Build a W-shaped driver" in sheet
    assert "six-spreader" in sheet
    assert "Evidence and limitations" in sheet
    assert "B (published)" in sheet
    assert "frame" in sheet


def test_trap_yagi_construction_sheet_lists_the_traps(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters

    design = sample_project.designs[0]
    trap_yagi = design.with_parameters(
        trap_yagi_parameters(
            driven_length_m=20.0,
            trap_inset_m=3.0,
            trap_frequency_hz=14_100_000.0,
        )
    )
    sheet = render_construction_sheet(sample_project, trap_yagi, None)

    assert "Trapped Yagi" in sheet
    assert "Trap inset" in sheet
    assert "Build 3 Yagi" in sheet
    assert "parallel LC trap" in sheet


def test_discone_construction_sheet_lists_the_cone_and_disc(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.discone import discone_parameters

    design = sample_project.designs[0]
    discone = design.with_parameters(
        discone_parameters(
            cone_height_m=0.5,
            cone_radius_m=0.3,
            disc_radius_m=0.6,
            wire_count=8,
        )
    )
    sheet = render_construction_sheet(sample_project, discone, None)

    assert "Discone" in sheet
    assert "Cone base radius" in sheet
    assert "Build 8 cone wires" in sheet
    assert "wire approximations" in sheet


def test_quad_beam_construction_sheet_lists_the_loops(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.quad_beam import quad_beam_parameters

    design = sample_project.designs[0]
    quad = design.with_parameters(
        quad_beam_parameters(
            element_count=3,
            loop_side_m=5.0,
            reflector_spacing_m=4.0,
            director_spacing_m=3.0,
        )
    )
    sheet = render_construction_sheet(sample_project, quad, None)

    assert "Quad beam" in sheet
    assert "Reflector spacing" in sheet
    assert "Build 3 square loops" in sheet
    assert "driven loop's left vertical" in sheet


def test_phased_vertical_construction_sheet_lists_the_array(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters

    design = sample_project.designs[0]
    phased = design.with_parameters(
        phased_vertical_parameters(
            element_count=3,
            height_m=5.0,
            spacing_m=5.5,
            phase_step_deg=120.0,
            radial_count=8,
            radial_length_m=5.0,
        )
    )
    sheet = render_construction_sheet(sample_project, phased, None)

    assert "Phased vertical array" in sheet
    assert "Phase step" in sheet
    assert "120.0°" in sheet
    assert "Build 3 vertical" in sheet
    assert "combining network is ideal" in sheet


def test_beverage_construction_sheet_lists_the_termination(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.beverage import beverage_parameters

    design = sample_project.designs[0]
    beverage = design.with_parameters(beverage_parameters(frequency_hz=3_500_000.0, length_m=80.0))
    sheet = render_construction_sheet(sample_project, beverage, None)

    assert "Beverage" in sheet
    assert "Termination" in sheet
    assert "ground rod" in sheet
    assert "80.0000 m" in sheet


def test_biquad_construction_sheet_lists_the_loop_stack(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters

    design = sample_project.designs[0]
    biquad = design.with_parameters(biquad_parameters(BiquadKind.DOUBLE))
    sheet = render_construction_sheet(sample_project, biquad, None)

    assert "Double biquad" in sheet
    assert "Loops" in sheet
    assert "Reflector" in sheet
    assert "square loops" in sheet


def test_typed_zepp_construction_sheet_lists_the_stub(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.zepp import zepp_starting_parameters

    design = sample_project.designs[0]
    zepp = design.with_parameters(zepp_starting_parameters())
    sheet = render_construction_sheet(sample_project, zepp, None)

    assert "Matching section" in sheet
    assert "Estimated stub impedance" in sheet
    assert "two matching-stub conductors" in sheet


def test_beta_hairpin_yagi_construction_sheet_lists_the_stub(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.yagi import YagiMatchType, nbs_five_element

    design = sample_project.designs[0]
    yagi = design.with_parameters(
        nbs_five_element(
            frequency_hz=50_100_000.0,
            height_m=8.0,
            match_type=YagiMatchType.BETA_HAIRPIN,
            match_length_m=0.2,
            match_spacing_m=0.1,
        )
    )
    sheet = render_construction_sheet(sample_project, yagi, None)

    assert "Feed match" in sheet
    assert "beta / hairpin" in sheet
    assert "Hairpin length" in sheet
    assert "0.2000 m" in sheet
    assert "0.1000 m" in sheet


def test_magnetic_loop_construction_sheet_lists_gap_and_capacitor(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters

    design = sample_project.designs[0]
    parameters = MagneticLoopParameters(
        frequency_hz=7_100_000.0,
        diameter_m=1.0,
        tuning_capacitance_f=180e-12,
        gap_length_m=0.04,
        capacitor_esr_ohm=0.2,
    )
    loop = design.with_parameters(parameters)
    sheet = render_construction_sheet(sample_project, loop, None)

    assert "Loop diameter" in sheet
    assert "Tuning gap" in sheet
    assert "Tuning capacitance" in sheet
    assert "180.000 pF" in sheet
    assert "Capacitor ESR" in sheet
    assert "0.200 Ω" in sheet
    assert "Feed the midpoint of the bottom" in sheet


def test_construction_sheet_reports_swr_bandwidth(sample_project: Project) -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters

    base = _make_result()
    frequency = base.frequencies[0]
    result = replace(
        base,
        frequencies=tuple(
            replace(
                frequency,
                frequency_hz=hz,
                impedance_ohm=complex(50.0, 0.0),
                swr=swr,
            )
            for hz, swr in (
                (7_000_000.0, 1.5),
                (7_050_000.0, 1.2),
                (7_100_000.0, 1.1),
                (7_150_000.0, 1.3),
                (7_200_000.0, 1.8),
            )
        ),
    )
    design = sample_project.designs[0]
    loop = design.with_parameters(
        MagneticLoopParameters(
            frequency_hz=7_100_000.0,
            diameter_m=1.0,
        )
    )
    sheet = render_construction_sheet(sample_project, loop, result)

    assert "SWR ≤ 2 bandwidth" in sheet
    assert "200.0 kHz" in sheet


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


def test_fan_dipole_construction_sheet_lists_angles_and_end_heights(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement

    parameters = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(FanElement(20.0, 120.0), FanElement(10.0, 90.0)),
        apex_height_m=12.0,
    )
    design = sample_project.designs[0].with_parameters(parameters)
    sheet = render_construction_sheet(sample_project, design, None)

    assert "Included angles" in sheet
    assert "120.0°, 90.0°" in sheet
    assert "End heights" in sheet
    assert "7.0000 m, 8.4645 m" in sheet


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
