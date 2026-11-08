# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters
from antennadesk.domain.antennas.endfed import EndFedParameters, EndFedPreset
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.zepp import zepp_parameters
from antennadesk.domain.antennas.zs6bkw import zs6bkw_parameters
from antennadesk.ui.template_identity import catalog_key_for, label_key_for


def test_catalog_key_for_current_templates() -> None:
    ringo = RingoParameters(
        frequency_hz=7_100_000.0,
        radiator_height_m=5.0,
        ring_diameter_m=1.0,
    )
    delta = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=42.0,
        height_m=8.0,
        sides=3,
    )
    sloper = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        preset=EndFedPreset.SLOPER,
    )
    t2fd = T2FDParameters(
        frequency_hz=1_800_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=50.8,
        spacing_m=1.69,
    )
    inverted_l = InvertedLParameters(
        frequency_hz=7_100_000.0,
        vertical_height_m=10.0,
        horizontal_length_m=20.0,
    )
    magnetic_loop = MagneticLoopParameters(
        frequency_hz=7_100_000.0,
        diameter_m=1.0,
    )

    assert catalog_key_for(ringo) == "ringo"
    assert catalog_key_for(delta) == "delta_loop"
    assert catalog_key_for(sloper) == "sloper"
    assert catalog_key_for(t2fd) == "t2fd"
    assert catalog_key_for(inverted_l) == "inverted_l"
    assert catalog_key_for(magnetic_loop) == "magnetic_loop"
    assert catalog_key_for(zs6bkw_parameters()) == "zs6bkw"
    assert catalog_key_for(zepp_parameters()) == "zepp"
    assert catalog_key_for(biquad_parameters(BiquadKind.SINGLE)) == "biquad"
    assert catalog_key_for(biquad_parameters(BiquadKind.DOUBLE)) == "double_biquad"
    assert catalog_key_for(beverage_parameters()) == "beverage"


def test_label_key_follows_the_catalog_entry() -> None:
    ringo = RingoParameters(
        frequency_hz=7_100_000.0,
        radiator_height_m=5.0,
        ring_diameter_m=1.0,
    )
    delta = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=42.0,
        height_m=8.0,
        sides=3,
    )

    assert label_key_for(ringo) == "catalog.ringo"
    assert label_key_for(delta) == "catalog.delta_loop"
    assert (
        label_key_for(
            InvertedLParameters(
                frequency_hz=7_100_000.0,
                vertical_height_m=10.0,
                horizontal_length_m=20.0,
            )
        )
        == "catalog.inverted_l"
    )
    assert (
        label_key_for(
            MagneticLoopParameters(
                frequency_hz=7_100_000.0,
                diameter_m=1.0,
            )
        )
        == "catalog.magnetic_loop"
    )
    assert label_key_for(zs6bkw_parameters()) == "catalog.zs6bkw"
    assert label_key_for(zepp_parameters()) == "catalog.zepp"
