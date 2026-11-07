# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.reporting.design_summary import design_summary_rows


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


def test_g5rv_custom_generator_is_labeled_in_the_summary() -> None:
    from antennadesk.domain.antennas.g5rv import g5rv_parameters

    parameters = g5rv_parameters(frequency_hz=14_100_000.0)
    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "custom wires"
    assert rows["Generator"] == "G5RV"
