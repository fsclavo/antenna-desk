# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.reporting.design_summary import (
    design_evidence_rows,
    design_summary_rows,
    feed_matching_rows,
    installation_profile_rows,
    optimization_summary_rows,
)


def test_biquad_summary_reports_the_loop_stack_and_reflector() -> None:
    from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters

    parameters = biquad_parameters(BiquadKind.DOUBLE)
    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "Double biquad"
    assert rows["Loops"] == "4"
    assert "behind" in rows["Reflector"]
    assert rows["Loop side"] == f"{parameters.loop_side_m:.4f} m"


def test_hexbeam_summary_reports_the_bent_elements() -> None:
    from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters

    parameters = published_hexbeam_parameters()
    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "Hexbeam"
    assert rows["Driver half-length"] == "5.5626 m"
    assert rows["Reflector half-length"] == "5.2578 m"
    assert rows["Turning radius"] == "3.3020 m"
    assert rows["Tip gap"] == "0.6096 m"
    assert rows["Feed"] == "center of the W driver"


def test_trap_yagi_summary_reports_the_traps() -> None:
    from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters

    parameters = trap_yagi_parameters(
        driven_length_m=20.0,
        reflector_spacing_m=4.0,
        director_spacing_m=3.0,
        trap_inset_m=3.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=5e-6,
    )
    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "Trapped Yagi"
    assert rows["Elements"] == "3"
    assert rows["Driven element"] == "20.0000 m"
    assert rows["Reflector element"] == "21.0000 m"
    assert rows["Director element"] == "19.0000 m"
    assert rows["Trap inset"] == "3.0000 m"
    assert rows["Trap frequency"] == "14.100 MHz"


def test_discone_summary_reports_the_cone_and_disc() -> None:
    from antennadesk.domain.antennas.discone import discone_parameters

    parameters = discone_parameters(
        cone_height_m=0.5,
        cone_radius_m=0.3,
        disc_radius_m=0.6,
        base_height_m=0.5,
        disc_gap_m=0.02,
        wire_count=8,
    )
    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "Discone"
    assert rows["Radial wires"] == "8"
    assert rows["Cone height"] == "0.5000 m"
    assert rows["Cone base radius"] == "0.3000 m"
    assert rows["Disc radius"] == "0.6000 m"
    assert rows["Feed"] == "across the apex gap"


def test_quad_beam_summary_reports_loops_and_spacing() -> None:
    from antennadesk.domain.antennas.quad_beam import quad_beam_parameters

    parameters = quad_beam_parameters(
        element_count=3,
        loop_side_m=5.0,
        reflector_spacing_m=4.0,
        director_spacing_m=3.0,
        height_m=2.5,
    )
    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "Quad beam"
    assert rows["Loops"] == "3"
    assert rows["Driven loop side"] == "5.0000 m"
    assert rows["Reflector side"] == "5.2500 m"
    assert rows["Director side"] == "4.7500 m"
    assert rows["Boom length"] == "7.0000 m"
    assert rows["Feed"] == "driven loop side midpoint"


def test_phased_vertical_summary_reports_the_excitation_and_radials() -> None:
    from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters

    parameters = phased_vertical_parameters(
        element_count=3,
        spacing_m=5.5,
        height_m=5.0,
        phase_step_deg=120.0,
        amplitude_taper=0.25,
        radial_count=8,
        radial_length_m=5.0,
    )
    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "Phased vertical array"
    assert rows["Verticals"] == "3"
    assert rows["Element spacing"] == "5.5000 m"
    assert rows["Phase step"] == "120.0°"
    assert rows["Amplitude taper"] == "25%"
    assert rows["Radials per element"] == "8"
    assert rows["Feed"] == "first vertical (primary)"


def test_beverage_summary_reports_length_and_termination() -> None:
    from antennadesk.domain.antennas.beverage import beverage_parameters

    parameters = beverage_parameters(
        frequency_hz=3_500_000.0,
        length_m=80.0,
        termination_resistance_ohm=470.0,
    )
    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "Beverage"
    assert rows["Length"] == "80.0000 m"
    assert rows["Termination"] == "470.0 Ω to ground"
    assert rows["Feed"] == "near end"


def test_sagged_dipole_summary_reports_sag_and_conductor_length() -> None:
    from antennadesk.domain.antennas.dipole import DipoleParameters

    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        sag_m=1.2,
    )
    rows = dict(design_summary_rows(parameters))

    assert rows["Sag"] == "1.2000 m"
    assert float(rows["Conductor length"].removesuffix(" m")) > 20.0


def test_loaded_dipole_summary_reports_links_and_coils() -> None:
    from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters

    rows = dict(
        design_summary_rows(
            loaded_dipole_parameters(
                total_length_m=18.0,
                link_offset_m=2.5,
                loading_coil_inductance_h=12e-6,
            )
        )
    )

    assert rows["Type"] == "Loaded dipole"
    assert rows["Full length"] == "18.0000 m"
    assert "12.000 µH" in rows["State"]
    assert rows["Coil Q"] != "—"


def test_optimization_summary_rows_describe_the_last_run() -> None:
    from datetime import UTC, datetime

    from antennadesk.application.use_cases.create_dipole_project import (
        CreateDipoleProject,
        CreateDipoleProjectCommand,
    )
    from antennadesk.domain.antennas.dipole import DipoleParameters
    from antennadesk.domain.optimization.summary import (
        OptimizationMode,
        OptimizationSummary,
    )

    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="Summary",
            variant_name="Dipole",
            parameters=DipoleParameters(
                frequency_hz=7_100_000.0,
                total_length_m=20.0,
                height_m=8.0,
            ),
        )
    )
    design = project.designs[0].with_optimization_summary(
        OptimizationSummary(
            mode=OptimizationMode.BAND_AWARE,
            objective="min_swr",
            status="converged",
            budget_profile="balanced",
            evaluations=180,
            seed=9,
            best_values={"total_length_m": 20.1},
            best_metrics={"swr": 1.2},
            completed_at=datetime(2026, 11, 7, 12, 0, tzinfo=UTC),
        )
    )

    rows = dict(optimization_summary_rows(design))

    assert rows["Last optimization"] == "band_aware · min_swr · converged"
    assert "180 evaluations" in rows["Optimization budget"]
    assert rows["Optimization completed"] == "2026-11-07 12:00"


def test_loaded_vertical_summary_reports_the_template_and_coil() -> None:
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

    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "loaded vertical"
    assert "12.0000 µH" in rows["Loading coil"]
    assert "1.0000 m" in rows["Loading coil"]
    assert "0.5 Ω" in rows["Loading coil"]


def test_trap_dipole_summary_reports_two_traps_and_band_edges() -> None:
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

    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "trap dipole"
    assert rows["Low band"] == "7.100000 MHz"
    assert rows["High band"] == "14.100000 MHz"
    assert rows["Total wire length"] == "20.0000 m"
    assert rows["Center section"] == "10.0000 m"
    assert rows["Outer section"] == "5.0000 m each"
    assert rows["Trap positions"] == "5.0000 m, 15.0000 m from wire start"
    assert rows["Trap frequency"] == "14.100000 MHz"
    assert "pF" in rows["Trap capacitance"]


def test_t2fd_summary_reports_the_band_termination_and_transformer() -> None:
    parameters = T2FDParameters(
        frequency_hz=3_500_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=26.0,
        spacing_m=0.9,
        height_m=12.0,
        termination_resistance_ohm=800.0,
        transformer_ratio=16.0,
    )

    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "terminated folded dipole (T2FD)"
    assert rows["Design band"] == "3.500000 MHz to 30.000000 MHz"
    assert rows["Element length"] == "26.0000 m"
    assert rows["Conductor spacing"] == "0.9000 m"
    assert rows["Total conductor length"] == "53.8000 m"
    assert rows["Termination resistor"] == "800 Ω non-inductive"
    assert rows["Feed transformer"] == "16:1"


def test_folded_dipole_summary_reports_the_feed_transformer() -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
        transformer_ratio=6.0,
    )

    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "folded dipole"
    assert rows["Element length"] == "20.0000 m"
    assert rows["Spacing"] == "0.2000 m"
    assert rows["Feed transformer"] == "6:1"


def test_loop_summary_reports_the_feed_transformer() -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
        transformer_ratio=4.0,
    )

    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "loop"
    assert rows["Circumference"] == "40.0000 m"
    assert rows["Feed transformer"] == "4:1"


def test_endfed_presets_are_labeled_in_the_summary() -> None:
    from antennadesk.domain.antennas.endfed import EndFedParameters, EndFedPreset

    sloper = dict(
        design_summary_rows(
            EndFedParameters(
                frequency_hz=7_100_000.0,
                length_m=20.0,
                feed_height_m=10.0,
                end_height_m=2.0,
                preset=EndFedPreset.SLOPER,
            )
        )
    )
    random_wire = dict(
        design_summary_rows(
            EndFedParameters(
                frequency_hz=7_100_000.0,
                length_m=17.0,
                preset=EndFedPreset.RANDOM_WIRE,
            )
        )
    )

    assert sloper["Type"] == "sloper"
    assert random_wire["Type"] == "random wire"


def test_yagi_and_moxon_summaries_report_polarization_and_clearance() -> None:
    from antennadesk.domain.antennas.moxon import MoxonParameters
    from antennadesk.domain.antennas.polarization import Polarization
    from antennadesk.domain.antennas.yagi import nbs_five_element

    yagi = dict(
        design_summary_rows(
            nbs_five_element(
                frequency_hz=50_100_000.0,
                height_m=8.0,
                polarization=Polarization.VERTICAL,
            )
        )
    )
    moxon = dict(
        design_summary_rows(
            MoxonParameters(
                frequency_hz=14_100_000.0,
                width_m=10.0,
                depth_m=2.5,
                reflector_tip_m=1.0,
                driven_tip_m=1.0,
                height_m=10.0,
                polarization=Polarization.VERTICAL,
            )
        )
    )

    assert yagi["Polarization"] == "vertical"
    assert yagi["Boom height"] == "8.0000 m"
    assert "Lowest tip" in yagi
    assert moxon["Polarization"] == "vertical"
    assert moxon["Boom height"] == "10.0000 m"
    assert moxon["Lowest edge"] == "5.0000 m"


def test_yagi_summary_reports_a_folded_driven_element() -> None:
    from antennadesk.domain.antennas.yagi import nbs_five_element

    rows = dict(
        design_summary_rows(
            nbs_five_element(
                frequency_hz=50_100_000.0,
                height_m=8.0,
                folded_driven=True,
                folded_spacing_m=0.1,
            )
        )
    )

    assert rows["Folded driven"] == "yes"
    assert rows["Fold spacing"] == "0.1000 m"


def test_yagi_summary_reports_a_beta_hairpin_match() -> None:
    from antennadesk.domain.antennas.yagi import YagiMatchType, nbs_five_element

    rows = dict(
        design_summary_rows(
            nbs_five_element(
                frequency_hz=50_100_000.0,
                height_m=8.0,
                match_type=YagiMatchType.BETA_HAIRPIN,
                match_length_m=0.2,
                match_spacing_m=0.1,
            )
        )
    )

    assert rows["Feed match"] == "beta_hairpin"
    assert rows["Hairpin length"] == "0.2000 m"
    assert rows["Hairpin spacing"] == "0.1000 m"


def test_loop_summary_reports_orientation_and_the_correct_height() -> None:
    from antennadesk.domain.antennas.loop import LoopOrientation, LoopParameters

    vertical = dict(
        design_summary_rows(
            LoopParameters(
                frequency_hz=7_100_000.0,
                circumference_m=40.0,
                height_m=8.0,
                sides=4,
            )
        )
    )
    horizontal = dict(
        design_summary_rows(
            LoopParameters(
                frequency_hz=7_100_000.0,
                circumference_m=40.0,
                height_m=8.0,
                sides=4,
                orientation=LoopOrientation.HORIZONTAL,
            )
        )
    )

    assert vertical["Orientation"] == "vertical"
    assert vertical["Bottom height"] == "8.0000 m"
    assert vertical["Top height"] == "22.1421 m"
    assert horizontal["Orientation"] == "horizontal"
    assert horizontal["Height"] == "8.0000 m"
    assert "Top height" not in horizontal


def test_top_loaded_vertical_summary_reports_the_capacity_hat() -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    rows = dict(
        design_summary_rows(
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
    )

    assert rows["Type"] == "top-loaded vertical"
    assert rows["Top hat wires"] == "4"
    assert rows["Top hat radius"] == "0.7500 m"


def test_scv_summary_reports_the_published_array_geometry() -> None:
    from antennadesk.domain.antennas.scv import ScvKind, scv_parameters

    rows = dict(design_summary_rows(scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0)))

    assert rows["Type"] == "bobtail curtain"
    assert rows["Horizontal length"] == "38.1000 m"
    assert rows["Vertical height"] == "11.5824 m"
    assert rows["Vertical elements"] == "3"
    assert rows["Horizontal segment"] == "19.0500 m each"
    assert rows["Total conductor"] == "72.8472 m"


def test_typed_transmission_line_doublet_summary() -> None:
    from antennadesk.domain.antennas.transmission_line_doublet import (
        DoubletPreset,
        doublet_starting_parameters,
    )

    rows = dict(design_summary_rows(doublet_starting_parameters(DoubletPreset.ZS6BKW)))

    assert rows["Type"] == "ZS6BKW"
    assert rows["Dipole length"] == "28.4000 m"
    assert rows["Matching line"] == "400 Ω, 13.6000 m, vf=1.000"


def test_typed_zepp_summary() -> None:
    from antennadesk.domain.antennas.zepp import zepp_starting_parameters

    rows = dict(design_summary_rows(zepp_starting_parameters()))

    assert rows["Type"] == "Zepp"
    assert rows["Matching section"] == "10.0283 m"
    assert rows["Estimated stub impedance"] == "468.9 Ω"


def test_magnetic_loop_summary_reports_tuning_and_loss_fields() -> None:
    from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters

    rows = dict(
        design_summary_rows(
            MagneticLoopParameters(
                frequency_hz=7_100_000.0,
                diameter_m=1.0,
                tuning_capacitance_f=180e-12,
                gap_length_m=0.04,
                capacitor_esr_ohm=0.2,
            )
        )
    )

    assert rows["Type"] == "magnetic loop"
    assert rows["Diameter"] == "1.0000 m"
    assert rows["Tuning gap"] == "0.0400 m"
    assert rows["Tuning capacitance"] == "180.000 pF"
    assert rows["Capacitor ESR"] == "0.200 Ω"
    assert "Capacitor reactance" in rows


def test_hexbeam_evidence_rows_report_the_limitations(sample_project) -> None:
    from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters

    design = sample_project.designs[0].with_parameters(published_hexbeam_parameters())
    rows = dict(design_evidence_rows(design))

    assert rows["Evidence level"] == "B (published)"
    assert "G3TXQ" in rows["Evidence source"]
    assert "frame" in rows["Limitation"]


def test_fan_dipole_summary_reports_angles_and_end_heights() -> None:
    from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement

    parameters = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(FanElement(20.0, 120.0), FanElement(10.0, 90.0)),
        apex_height_m=12.0,
    )
    rows = dict(design_summary_rows(parameters))

    assert rows["Included angles"] == "120.0°, 90.0°"
    assert rows["End heights"] == "7.0000 m, 8.4645 m"


def test_g5rv_custom_generator_is_labeled_in_the_summary() -> None:
    from antennadesk.domain.antennas.g5rv import g5rv_parameters

    parameters = g5rv_parameters(frequency_hz=14_100_000.0)
    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "custom wires"
    assert rows["Generator"] == "G5RV"


def test_endfed_summary_marks_internal_matching_retained_under_override() -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters
    from antennadesk.domain.antennas.matching_network import LNetwork

    parameters = shortened_efhw_80_10_parameters()
    project = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)

    rows = dict(design_summary_rows(parameters, project_network=project))

    assert "retained; project network overrides" in rows["Matching capacitor"]
    assert "retained; project network overrides" in rows["Transformer leakage"]


def test_endfed_summary_marks_internal_matching_active_without_an_override() -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters

    rows = dict(design_summary_rows(shortened_efhw_80_10_parameters()))

    assert "primary shunt, active" in rows["Matching capacitor"]
    assert "µH (active)" in rows["Transformer leakage"]


def test_endfed_bend_summary_reports_vertical_and_horizontal_sections() -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters

    parameters = replace(
        shortened_efhw_80_10_parameters(feed_height_m=2.0),
        bend_enabled=True,
        bend_vertical_length_m=8.0,
    )
    rows = dict(design_summary_rows(parameters))

    assert rows["Vertical section"] == "8.0000 m"
    assert rows["Horizontal run"] == "14.7400 m"
    assert rows["Top height"] == "10.0000 m"
    assert "End height" not in rows


def test_feed_matching_rows_describe_the_project_chain() -> None:
    from antennadesk.domain.antennas.balun import BalunLoss
    from antennadesk.domain.antennas.feed_line import FeedLine
    from antennadesk.domain.antennas.matching_network import LNetwork

    project = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    feed_line = FeedLine(characteristic_impedance_ohm=50.0, length_m=5.0, velocity_factor=0.8)
    balun = BalunLoss(reference_frequency_hz=7_000_000.0, reference_loss_db=0.5)

    rows = dict(
        feed_matching_rows(
            project,
            feed_line,
            balun,
        )
    )

    assert "L network" in rows["Project matching"]
    assert "active" in rows["Project matching"]
    assert "50 Ω, 5.0000 m, velocity factor 0.8" in rows["Feed line"]
    assert "0.500 dB at 7.000000 MHz" in rows["Balun/unun loss"]
    assert "at feedpoint" in rows["Project matching"]

    from antennadesk.domain.antennas.matching_network import MatchingNetworkPosition

    shack_rows = dict(
        feed_matching_rows(
            project,
            feed_line,
            balun,
            position=MatchingNetworkPosition.SHACK,
        )
    )
    assert "in shack" in shack_rows["Project matching"]


def test_feed_matching_rows_omit_inactive_project_items() -> None:
    from antennadesk.domain.antennas.feed_line import FeedLine

    rows = dict(
        feed_matching_rows(
            None,
            FeedLine(),
            None,
        )
    )

    assert "Project matching" not in rows
    assert "Feed line" not in rows
    assert "Balun/unun loss" not in rows


def test_installation_profile_rows_describe_the_active_site() -> None:
    from uuid import uuid4

    from antennadesk.domain.environment.ground import FREE_SPACE
    from antennadesk.domain.projects.installation import (
        InstallationProfile,
        InstallationSupport,
    )

    profile = InstallationProfile(
        id=uuid4(),
        name="Home",
        available_height_m=12.0,
        available_width_m=30.0,
        orientation_deg=90.0,
        ground=FREE_SPACE,
        support=InstallationSupport.TREE,
        notes="Back yard",
    )

    rows = dict(installation_profile_rows(profile))

    assert rows["Installation profile"] == "Home"
    assert rows["Available height"] == "12.000 m"
    assert rows["Available space"] == "30.000 m"
    assert rows["Installation orientation"] == "90°"
    assert rows["Support"] == "tree"
    assert rows["Profile ground"] == "free_space"
    assert rows["Profile notes"] == "Back yard"
    assert installation_profile_rows(None) == ()
