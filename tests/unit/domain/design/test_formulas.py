# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.design.formulas import (
    FIVE_EIGHTH_WAVE_FACTOR,
    HALF_WAVE_FACTOR,
    QUARTER_WAVE_FACTOR,
    five_eighth_wave_length_m,
    half_wave_length_m,
    loop_circumference_m,
    quarter_wave_length_m,
    wavelength_m,
)


def test_shared_formula_factors_are_the_documented_starting_points() -> None:
    assert pytest.approx(0.475) == HALF_WAVE_FACTOR
    assert pytest.approx(0.2375) == QUARTER_WAVE_FACTOR
    assert pytest.approx(0.625) == FIVE_EIGHTH_WAVE_FACTOR


def test_common_lengths_at_seven_megahertz() -> None:
    frequency_hz = 7_100_000.0
    assert wavelength_m(frequency_hz) == pytest.approx(42.22428985915493)
    assert half_wave_length_m(frequency_hz) == pytest.approx(20.05653768309859)
    assert loop_circumference_m(frequency_hz) == pytest.approx(42.22428985915493)
    assert quarter_wave_length_m(frequency_hz) == pytest.approx(10.028268841549295)


def test_five_eighth_vertical_is_longer_than_a_quarter_wave() -> None:
    frequency_hz = 146_000_000.0
    assert five_eighth_wave_length_m(frequency_hz) > quarter_wave_length_m(frequency_hz)
