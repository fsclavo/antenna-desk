# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

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


def test_g5rv_custom_generator_is_labeled_in_the_summary() -> None:
    from antennadesk.domain.antennas.g5rv import g5rv_parameters

    parameters = g5rv_parameters(frequency_hz=14_100_000.0)
    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "custom wires"
    assert rows["Generator"] == "G5RV"
