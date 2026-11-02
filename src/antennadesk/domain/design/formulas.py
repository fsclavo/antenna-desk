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
# AntennaDesk application preset calibrated with NEC-2 for the closed thin-wire
# polygon used by the loop model.  A polygon needs slightly more conductor than
# the ideal 1.0λ circular loop, and the correction grows as the side count
# falls.  The coefficients are documented in docs/ANTENNA_DESIGN_ESTIMATORS.md.
LOOP_POLYGON_BASE_FACTOR = 1.02895
LOOP_POLYGON_SIDES_FACTOR = 0.05028
LOOP_POLYGON_SIDES_SQUARED_FACTOR = 0.09665
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
SOURCE_DL6WU_YAGI = "cebik.dl6wu.32_element_rsgb"
SOURCE_APPLICATION_PRESET = "antennadesk.heuristic.application_preset"


def wavelength_m(frequency_hz: float) -> float:
    return units.wavelength_m(frequency_hz)


def half_wave_length_m(frequency_hz: float) -> float:
    return wavelength_m(frequency_hz) * HALF_WAVE_FACTOR


def loop_resonance_factor(sides: int) -> float:
    """Return the polygon correction for a closed loop with ``sides`` sides."""

    if sides < 3:
        raise ValueError("a loop requires at least 3 sides")
    inverse = 1.0 / sides
    return (
        LOOP_POLYGON_BASE_FACTOR
        + LOOP_POLYGON_SIDES_FACTOR * inverse
        + LOOP_POLYGON_SIDES_SQUARED_FACTOR * inverse * inverse
    )


def loop_circumference_m(frequency_hz: float, sides: int = 16) -> float:
    return wavelength_m(frequency_hz) * loop_resonance_factor(sides)


def quarter_wave_length_m(frequency_hz: float) -> float:
    return wavelength_m(frequency_hz) * QUARTER_WAVE_FACTOR


def five_eighth_wave_length_m(frequency_hz: float) -> float:
    return wavelength_m(frequency_hz) * FIVE_EIGHTH_WAVE_FACTOR


def default_radial_length_m(frequency_hz: float) -> float:
    return wavelength_m(frequency_hz) * RADIAL_LENGTH_FACTOR
