# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.design.formulas import (
    FIVE_EIGHTH_WAVE_FACTOR,
    HALF_WAVE_FACTOR,
    QUARTER_WAVE_FACTOR,
    RADIAL_LENGTH_FACTOR,
    default_radial_length_m,
    five_eighth_wave_length_m,
    frequency_for_half_wave_length,
    half_wave_length_m,
    loop_circumference_m,
    loop_resonance_factor,
    quarter_wave_length_m,
    wavelength_m,
)


def test_shared_formula_factors_are_the_documented_starting_points() -> None:
    assert pytest.approx(0.475) == HALF_WAVE_FACTOR
    assert pytest.approx(0.2375) == QUARTER_WAVE_FACTOR
    assert pytest.approx(0.59375) == FIVE_EIGHTH_WAVE_FACTOR


@pytest.mark.parametrize(
    ("feet_constant", "factor"),
    [
        (468.0, HALF_WAVE_FACTOR),
        (234.0, QUARTER_WAVE_FACTOR),
        (585.0, FIVE_EIGHTH_WAVE_FACTOR),
    ],
)
def test_length_factors_match_the_published_arrl_formulas(
    feet_constant: float,
    factor: float,
) -> None:
    # ARRL practical formulas: L_ft = constant / f_MHz, so L/lambda is constant.
    published_factor = feet_constant * 0.3048 * 1_000_000.0 / 299_792_458.0

    assert factor == pytest.approx(published_factor, rel=0.005)


def test_common_lengths_at_seven_megahertz() -> None:
    frequency_hz = 7_100_000.0
    wavelength = wavelength_m(frequency_hz)
    assert wavelength == pytest.approx(42.22428985915493)
    assert half_wave_length_m(frequency_hz) == pytest.approx(20.05653768309859)
    assert loop_circumference_m(frequency_hz) == pytest.approx(
        wavelength * loop_resonance_factor(16)
    )
    assert quarter_wave_length_m(frequency_hz) == pytest.approx(10.028268841549295)


def test_loop_resonance_factor_accounts_for_polygon_side_count() -> None:
    assert loop_resonance_factor(3) == pytest.approx(1.056, abs=0.001)
    assert loop_resonance_factor(4) == pytest.approx(1.048, abs=0.001)
    assert loop_resonance_factor(16) == pytest.approx(1.032, abs=0.001)
    assert loop_resonance_factor(3) > loop_resonance_factor(4)
    assert loop_resonance_factor(4) > loop_resonance_factor(16)


def test_loop_resonance_factor_rejects_fewer_than_three_sides() -> None:
    with pytest.raises(ValueError, match="at least 3 sides"):
        loop_resonance_factor(2)


def test_five_eighth_vertical_is_longer_than_a_quarter_wave() -> None:
    frequency_hz = 146_000_000.0
    assert five_eighth_wave_length_m(frequency_hz) > quarter_wave_length_m(frequency_hz)


def test_frequency_for_half_wave_length_is_the_inverse() -> None:
    frequency_hz = 14_100_000.0
    length_m = half_wave_length_m(frequency_hz)

    assert frequency_for_half_wave_length(length_m) == pytest.approx(frequency_hz)
    # A sub-meter wire is valid: kill the "length <= 1 m" boundary mistake.
    assert frequency_for_half_wave_length(0.5) == pytest.approx(
        299_792_458.0 * HALF_WAVE_FACTOR / 0.5
    )
    with pytest.raises(ValueError):
        frequency_for_half_wave_length(0.0)


def test_default_radial_length_is_a_quarter_wavelength() -> None:
    frequency_hz = 7_100_000.0

    assert pytest.approx(0.25) == RADIAL_LENGTH_FACTOR
    assert default_radial_length_m(frequency_hz) == pytest.approx(wavelength_m(frequency_hz) * 0.25)
