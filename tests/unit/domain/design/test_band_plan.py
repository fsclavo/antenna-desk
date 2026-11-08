# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.endfed import EndFedParameters, EndFedPreset
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.antennas.g5rv import g5rv_parameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.zepp import zepp_parameters
from antennadesk.domain.antennas.zs6bkw import zs6bkw_parameters
from antennadesk.domain.design.band_plan import (
    BandEvidence,
    BandPlan,
    BandSelection,
    default_band_plan,
)
from antennadesk.domain.simulation.bands import amateur_band_by_id


def test_band_selection_builds_a_sweep() -> None:
    band = amateur_band_by_id("40m")
    assert band is not None
    selection = BandSelection(band, points=11)

    assert selection.band_id == "40m"
    assert selection.frequency_plan.count == 11
    assert selection.frequency_plan.start_hz == band.start_hz
    assert selection.frequency_plan.stop_hz == band.stop_hz


def test_band_plan_rejects_duplicate_bands() -> None:
    band = amateur_band_by_id("40m")
    assert band is not None

    with pytest.raises(ValueError):
        BandPlan((BandSelection(band), BandSelection(band)))


def test_g5rv_default_plan_uses_published_hf_bands() -> None:
    result = default_band_plan(g5rv_parameters(frequency_hz=14_100_000.0))

    assert result.evidence is BandEvidence.PUBLISHED
    assert result.plan.band_ids == ("80m", "40m", "20m", "15m", "10m")


def test_zs6bkw_default_plan_uses_the_no_atu_bands() -> None:
    result = default_band_plan(zs6bkw_parameters())

    assert result.evidence is BandEvidence.PUBLISHED
    assert result.note_key == "band.note.zs6bkw"
    assert result.plan.band_ids == ("40m", "20m", "17m", "12m", "10m")


def test_zepp_default_plan_uses_odd_harmonics() -> None:
    result = default_band_plan(zepp_parameters())

    assert result.evidence is BandEvidence.HEURISTIC
    assert result.note_key == "band.note.zepp"
    assert result.plan.band_ids == ("40m", "15m")


def test_ocfd_default_plan_follows_harmonics() -> None:
    forty = default_band_plan(OCFDParameters(frequency_hz=7_100_000.0, total_length_m=20.4))
    eighty = default_band_plan(OCFDParameters(frequency_hz=3_750_000.0, total_length_m=40.0))

    assert forty.plan.band_ids == ("40m", "20m", "10m")
    assert eighty.plan.band_ids == ("80m", "40m", "20m", "10m")


def test_endfed_defaults_distinguish_random_wire_and_sloper() -> None:
    standard = default_band_plan(EndFedParameters(frequency_hz=7_100_000.0, length_m=20.0))
    random_wire = default_band_plan(
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=17.0,
            preset=EndFedPreset.RANDOM_WIRE,
        )
    )
    sloper = default_band_plan(
        EndFedParameters(
            frequency_hz=3_750_000.0,
            length_m=40.0,
            preset=EndFedPreset.SLOPER,
        )
    )

    assert standard.plan.band_ids == ("40m", "20m", "10m")
    assert random_wire.plan.band_ids == (
        "80m",
        "40m",
        "30m",
        "20m",
        "17m",
        "15m",
        "12m",
        "10m",
    )
    assert sloper.plan.band_ids == ("80m", "40m", "20m")


def test_fan_dipole_defaults_follow_element_lengths() -> None:
    result = default_band_plan(
        FanDipoleParameters(
            frequency_hz=7_100_000.0,
            elements=(FanElement(10.0, 120.0), FanElement(5.0, 100.0)),
            apex_height_m=10.0,
        )
    )

    assert result.plan.band_ids == ("20m", "10m")


def test_trap_dipole_defaults_use_both_design_bands() -> None:
    result = default_band_plan(
        TrapDipoleParameters(
            frequency_hz=7_100_000.0,
            high_band_frequency_hz=14_100_000.0,
            inner_length_m=10.0,
            outer_length_m=4.0,
            trap_frequency_hz=14_100_000.0,
            trap_inductance_h=2.0e-6,
        )
    )

    assert result.plan.band_ids == ("40m", "20m")
    assert result.note_key == "band.note.trap"


def test_t2fd_defaults_cover_the_broadband_range() -> None:
    result = default_band_plan(
        T2FDParameters(
            frequency_hz=3_500_000.0,
            highest_frequency_hz=30_000_000.0,
            length_m=26.13,
            spacing_m=0.87,
        )
    )

    assert result.evidence is BandEvidence.BROADBAND
    assert "80m" in result.plan.band_ids
    assert "10m" in result.plan.band_ids


def test_biquad_default_is_the_current_band() -> None:
    from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters

    default = default_band_plan(biquad_parameters(BiquadKind.SINGLE, frequency_hz=14_100_000.0))

    assert default.evidence is BandEvidence.CURRENT
    assert default.note_key == "band.note.biquad"
    assert default.plan.band_ids == ("20m",)


def test_beverage_default_is_the_current_band() -> None:
    from antennadesk.domain.antennas.beverage import beverage_parameters

    default = default_band_plan(beverage_parameters(frequency_hz=3_500_000.0))

    assert default.evidence is BandEvidence.CURRENT
    assert default.note_key == "band.note.beverage"
    assert default.plan.band_ids == ("80m",)


def test_loaded_dipole_default_is_the_current_band() -> None:
    from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters

    default = default_band_plan(loaded_dipole_parameters(frequency_hz=7_100_000.0))

    assert default.evidence is BandEvidence.CURRENT
    assert default.note_key == "band.note.loaded_dipole"
    assert default.plan.band_ids == ("40m",)


def test_narrowband_default_is_the_current_band() -> None:
    result = default_band_plan(
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0)
    )

    assert result.plan.band_ids == ("40m",)
    assert result.evidence is BandEvidence.CURRENT


def test_doublet_default_uses_the_high_impedance_feed_line() -> None:
    result = default_band_plan(
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
        high_impedance_feed_line=True,
    )

    assert result.evidence is BandEvidence.TUNABLE
    assert result.note_key == "band.note.doublet"
    assert result.plan.band_ids == (
        "80m",
        "40m",
        "30m",
        "20m",
        "17m",
        "15m",
        "12m",
        "10m",
    )
