# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace

import pytest

from antennadesk.domain.antennas.biquad import BiquadParameters
from antennadesk.domain.antennas.design import primary_dimension_m
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import DisconeParameters, discone_parameters
from antennadesk.domain.antennas.endfed import efhw_parameters
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.hexbeam import (
    HexbeamBand,
    HexbeamParameters,
    published_hexbeam_multiband_parameters,
    published_hexbeam_parameters,
)
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.quad_beam import (
    QuadBeamParameters,
    quad_beam_parameters,
)
from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters
from antennadesk.domain.antennas.yagi import nbs_five_element
from antennadesk.domain.design.frequency_scale import (
    UnsupportedFrequencyScaleError,
    scale_hexbeam_band_set,
    scaled_to_frequency,
    supports_frequency_scaling,
)


def test_hexbeam_band_set_scales_uniformly_within_the_primary_band() -> None:
    parameters = published_hexbeam_multiband_parameters(labels=("20m", "15m", "10m"))
    target_hz = 14_100_000.0
    length_ratio = parameters.bands[0].frequency_hz / target_hz
    frequency_ratio = target_hz / parameters.bands[0].frequency_hz

    scaled = scale_hexbeam_band_set(parameters, target_hz)

    assert scaled.frequency_hz == pytest.approx(target_hz)
    assert scaled.turning_radius_m == pytest.approx(parameters.turning_radius_m * length_ratio)
    for original, changed in zip(parameters.bands, scaled.bands, strict=True):
        assert changed.label == original.label
        assert changed.frequency_hz == pytest.approx(original.frequency_hz * frequency_ratio)
        assert changed.driver_half_length_m == pytest.approx(
            original.driver_half_length_m * length_ratio
        )
        assert changed.reflector_half_length_m == pytest.approx(
            original.reflector_half_length_m * length_ratio
        )
        assert changed.tip_gap_m == pytest.approx(original.tip_gap_m * length_ratio)
        assert changed.vertical_offset_m == pytest.approx(original.vertical_offset_m * length_ratio)

    with pytest.raises(UnsupportedFrequencyScaleError):
        scale_hexbeam_band_set(parameters, 10_000_000.0)
    with pytest.raises(UnsupportedFrequencyScaleError):
        scale_hexbeam_band_set(published_hexbeam_parameters(), 14_100_000.0)


def test_dipole_scales_length_and_preserves_installation() -> None:
    parameters = DipoleParameters(
        frequency_hz=14_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )

    scaled = scaled_to_frequency(parameters, 28_200_000.0)

    assert isinstance(scaled, DipoleParameters)
    assert scaled.frequency_hz == pytest.approx(28_200_000.0)
    assert scaled.total_length_m == pytest.approx(10.0)
    assert scaled.height_m == pytest.approx(8.0)


def test_folded_dipole_scales_length_and_spacing() -> None:
    parameters = FoldedDipoleParameters(
        frequency_hz=14_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )

    scaled = scaled_to_frequency(parameters, 28_200_000.0)

    assert isinstance(scaled, FoldedDipoleParameters)
    assert scaled.total_length_m == pytest.approx(10.0)
    assert scaled.spacing_m == pytest.approx(0.1)
    assert scaled.height_m == pytest.approx(8.0)


def test_loop_scales_circumference_and_preserves_transformer() -> None:
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=42.0,
        height_m=8.0,
        sides=4,
        transformer_ratio=4.0,
    )

    scaled = scaled_to_frequency(parameters, 14_200_000.0)

    assert isinstance(scaled, LoopParameters)
    assert scaled.circumference_m == pytest.approx(21.0)
    assert scaled.transformer_ratio == pytest.approx(4.0)
    assert scaled.height_m == pytest.approx(8.0)


def test_quad_beam_scales_spacing_and_preserves_family_fields() -> None:
    parameters = quad_beam_parameters(
        frequency_hz=144_000_000.0,
        element_count=3,
        loop_side_m=0.50,
        reflector_spacing_m=0.45,
        director_spacing_m=0.45,
        height_m=8.0,
        reflector_scale=1.1,
        director_scale=0.9,
        transformer_ratio=6.0,
    )

    scaled = scaled_to_frequency(parameters, 288_000_000.0)

    assert isinstance(scaled, QuadBeamParameters)
    assert scaled.loop_side_m == pytest.approx(0.25)
    assert scaled.reflector_spacing_m == pytest.approx(0.225)
    assert scaled.director_spacing_m == pytest.approx(0.225)
    assert scaled.height_m == pytest.approx(8.0)
    assert scaled.element_count == 3
    assert scaled.reflector_scale == pytest.approx(1.1)
    assert scaled.director_scale == pytest.approx(0.9)
    assert scaled.transformer_ratio == pytest.approx(6.0)


def test_biquad_scales_loop_and_reflector_spacing() -> None:
    parameters = BiquadParameters(
        frequency_hz=2_440_000_000.0,
        loop_side_m=0.031,
        reflector_spacing_m=0.0155,
        base_height_m=1.0,
        reflector_enabled=True,
    )

    scaled = scaled_to_frequency(parameters, 4_880_000_000.0)

    assert isinstance(scaled, BiquadParameters)
    assert scaled.loop_side_m == pytest.approx(0.0155)
    assert scaled.reflector_spacing_m == pytest.approx(0.00775)
    assert scaled.base_height_m == pytest.approx(1.0)


def test_discone_scales_cone_but_preserves_feed_and_wire_count() -> None:
    parameters = discone_parameters(
        frequency_hz=145_000_000.0,
        base_height_m=0.5,
        disc_gap_m=0.01,
        wire_count=8,
    )

    scaled = scaled_to_frequency(parameters, 290_000_000.0)

    assert isinstance(scaled, DisconeParameters)
    assert scaled.cone_height_m == pytest.approx(parameters.cone_height_m / 2.0)
    assert scaled.cone_radius_m == pytest.approx(parameters.cone_radius_m / 2.0)
    assert scaled.disc_radius_m == pytest.approx(parameters.disc_radius_m / 2.0)
    assert scaled.base_height_m == pytest.approx(0.5)
    assert scaled.disc_gap_m == pytest.approx(0.01)
    assert scaled.wire_count == 8


def test_hexbeam_scales_reference_geometry_and_preserves_installation() -> None:
    parameters = published_hexbeam_parameters(
        frequency_hz=14_184_000.0,
        height_m=10.0,
    )

    scaled = scaled_to_frequency(parameters, 28_368_000.0)

    assert isinstance(scaled, HexbeamParameters)
    assert scaled.driver_half_length_m == pytest.approx(parameters.driver_half_length_m / 2.0)
    assert scaled.turning_radius_m == pytest.approx(parameters.turning_radius_m / 2.0)
    assert scaled.height_m == pytest.approx(10.0)


def test_multiband_hexbeam_frequency_scaling_is_explicitly_unsupported() -> None:
    primary = published_hexbeam_parameters()
    secondary = published_hexbeam_parameters(frequency_hz=21_200_000.0)
    parameters = replace(
        primary,
        bands=(
            HexbeamBand(
                label="20m",
                frequency_hz=primary.frequency_hz,
                driver_half_length_m=primary.driver_half_length_m,
                reflector_half_length_m=primary.reflector_half_length_m,
                tip_gap_m=primary.tip_gap_m,
                feed_gap_m=primary.feed_gap_m,
                vertical_offset_m=0.0,
            ),
            HexbeamBand(
                label="15m",
                frequency_hz=secondary.frequency_hz,
                driver_half_length_m=secondary.driver_half_length_m,
                reflector_half_length_m=secondary.reflector_half_length_m,
                tip_gap_m=secondary.tip_gap_m,
                feed_gap_m=secondary.feed_gap_m,
                vertical_offset_m=0.2286,
            ),
        ),
    )

    assert not supports_frequency_scaling(parameters)
    with pytest.raises(UnsupportedFrequencyScaleError):
        scaled_to_frequency(parameters, 28_368_000.0)


def test_unsupported_families_raise_a_clear_error() -> None:
    unsupported = (
        nbs_five_element(frequency_hz=145_000_000.0, height_m=10.0),
        trap_yagi_parameters(),
        efhw_parameters("40m"),
    )

    for parameters in unsupported:
        assert supports_frequency_scaling(parameters) is False
        with pytest.raises(UnsupportedFrequencyScaleError):
            scaled_to_frequency(parameters, 14_100_000.0)


def test_scaling_rejects_a_non_positive_frequency() -> None:
    parameters = DipoleParameters(
        frequency_hz=14_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )

    with pytest.raises(ValueError, match="frequency_hz"):
        scaled_to_frequency(parameters, 0.0)


def test_allowlisted_primary_dimension_scales_by_the_frequency_ratio() -> None:
    parameters = quad_beam_parameters(
        frequency_hz=144_000_000.0,
        element_count=2,
    )

    scaled = scaled_to_frequency(parameters, 432_000_000.0)

    assert primary_dimension_m(scaled) == pytest.approx(primary_dimension_m(parameters) / 3.0)
