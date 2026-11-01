# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared wavelength and empirical starting-point formulas.

The factors below are deliberately explicit and documented in
`docs/ANTENNA_DESIGN_ESTIMATORS.md`. They are starting heuristics, not
universal resonant-length guarantees.
"""

from __future__ import annotations

from ..common import units

# ARRL Antenna Book, practical half-wave dipole end-effect discussion.
END_EFFECT_FACTOR = 0.95
HALF_WAVE_FACTOR = 0.5 * END_EFFECT_FACTOR
QUARTER_WAVE_FACTOR = 0.25 * END_EFFECT_FACTOR
FIVE_EIGHTH_WAVE_FACTOR = 0.625
LOOP_CIRCUMFERENCE_FACTOR = 1.0
FOLDED_SPACING_FACTOR = 0.02
RADIAL_LENGTH_FACTOR = 0.25
J_POLE_STUB_FACTOR = QUARTER_WAVE_FACTOR

MOXON_REFERENCE_FREQUENCY_HZ = 14_170_000.0
RINGO_REFERENCE_FREQUENCY_HZ = 50_100_000.0

SOURCE_ARRL_DIPOLE = "arrl.antenna_book.dipole.end_effect"
SOURCE_ARRL_LOOP = "arrl.antenna_book.loop.resonant_circumference"
SOURCE_ARRL_VERTICAL = "arrl.antenna_book.vertical.quarter_wave"
SOURCE_NBS_YAGI = "nbs.tn688.five_element"
SOURCE_CEBIK_MOXON = "cebik.moxon_review.table1"
SOURCE_APPLICATION_PRESET = "antennadesk.heuristic.application_preset"


def wavelength_m(frequency_hz: float) -> float:
    return units.wavelength_m(frequency_hz)


def half_wave_length_m(frequency_hz: float) -> float:
    return wavelength_m(frequency_hz) * HALF_WAVE_FACTOR


def loop_circumference_m(frequency_hz: float) -> float:
    return wavelength_m(frequency_hz) * LOOP_CIRCUMFERENCE_FACTOR


def quarter_wave_length_m(frequency_hz: float) -> float:
    return wavelength_m(frequency_hz) * QUARTER_WAVE_FACTOR


def five_eighth_wave_length_m(frequency_hz: float) -> float:
    return wavelength_m(frequency_hz) * FIVE_EIGHTH_WAVE_FACTOR


def default_radial_length_m(frequency_hz: float) -> float:
    return wavelength_m(frequency_hz) * RADIAL_LENGTH_FACTOR
