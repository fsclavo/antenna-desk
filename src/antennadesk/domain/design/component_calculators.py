# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Practical component calculators for antenna construction.

These are construction aids, not antenna models. The solenoid formula is the
Wheeler air-core approximation, the LC relations are ideal, and the conductor
resistance is a smooth DC/RF estimate. Results must be verified with the solver
and, where possible, with a measurement.
"""

from __future__ import annotations

import math

from ..antennas.materials import ConductorMaterial
from ..common.units import ensure_positive

VACUUM_PERMEABILITY_H_PER_M = 4.0 * math.pi * 1e-7
"""Magnetic constant used by the skin-depth estimate."""


def solenoid_inductance_h(
    *,
    turns: int,
    diameter_m: float,
    length_m: float,
) -> float:
    """Return the Wheeler air-core solenoid inductance in henries.

    Wheeler's formula is expressed in inches:

    ``L[uH] = d^2 N^2 / (18 d + 40 l)``

    with ``d`` and ``l`` in inches. It is a starting approximation for a
    single-layer air-core coil and assumes a winding length not much shorter
    than the diameter.
    """

    if turns <= 0:
        raise ValueError("turns must be positive")
    ensure_positive(diameter_m, name="diameter_m")
    ensure_positive(length_m, name="length_m")
    diameter_in = diameter_m / 0.0254
    length_in = length_m / 0.0254
    inductance_uh = (
        turns * turns * diameter_in * diameter_in / (18.0 * diameter_in + 40.0 * length_in)
    )
    return inductance_uh * 1e-6


def solenoid_turns_for_inductance(
    *,
    inductance_h: float,
    diameter_m: float,
    length_m: float,
) -> float:
    """Return the Wheeler turns estimate for a target inductance."""

    ensure_positive(inductance_h, name="inductance_h")
    ensure_positive(diameter_m, name="diameter_m")
    ensure_positive(length_m, name="length_m")
    inductance_uh = inductance_h * 1e6
    diameter_in = diameter_m / 0.0254
    length_in = length_m / 0.0254
    turns_squared = (
        inductance_uh * (18.0 * diameter_in + 40.0 * length_in) / (diameter_in * diameter_in)
    )
    if turns_squared <= 0.0:
        raise ValueError("target inductance is too small for this coil")
    return math.sqrt(turns_squared)


def lc_resonance_hz(*, inductance_h: float, capacitance_f: float) -> float:
    ensure_positive(inductance_h, name="inductance_h")
    ensure_positive(capacitance_f, name="capacitance_f")
    return 1.0 / (2.0 * math.pi * math.sqrt(inductance_h * capacitance_f))


def capacitance_for_resonance_f(*, inductance_h: float, frequency_hz: float) -> float:
    ensure_positive(inductance_h, name="inductance_h")
    ensure_positive(frequency_hz, name="frequency_hz")
    return 1.0 / ((2.0 * math.pi * frequency_hz) ** 2 * inductance_h)


def inductance_for_resonance_f(*, capacitance_f: float, frequency_hz: float) -> float:
    ensure_positive(capacitance_f, name="capacitance_f")
    ensure_positive(frequency_hz, name="frequency_hz")
    return 1.0 / ((2.0 * math.pi * frequency_hz) ** 2 * capacitance_f)


def inductive_reactance_ohm(*, inductance_h: float, frequency_hz: float) -> float:
    ensure_positive(inductance_h, name="inductance_h")
    ensure_positive(frequency_hz, name="frequency_hz")
    return 2.0 * math.pi * frequency_hz * inductance_h


def capacitive_reactance_ohm(*, capacitance_f: float, frequency_hz: float) -> float:
    ensure_positive(capacitance_f, name="capacitance_f")
    ensure_positive(frequency_hz, name="frequency_hz")
    return 1.0 / (2.0 * math.pi * frequency_hz * capacitance_f)


def skin_depth_m(
    *,
    frequency_hz: float,
    material: ConductorMaterial,
) -> float:
    ensure_positive(frequency_hz, name="frequency_hz")
    return math.sqrt(
        1.0
        / (
            math.pi
            * frequency_hz
            * VACUUM_PERMEABILITY_H_PER_M
            * material.relative_permeability
            * material.conductivity_s_per_m
        )
    )


def round_wire_resistance_per_m(
    *,
    frequency_hz: float,
    diameter_m: float,
    material: ConductorMaterial,
) -> tuple[float, float, float]:
    """Return ``(dc, approximate_rf, skin_depth)`` per metre.

    The RF estimate uses the high-frequency surface-resistance limit and is
    capped below by the DC value. It is a comparison aid, not a substitute for
    a measured conductor loss.
    """

    ensure_positive(frequency_hz, name="frequency_hz")
    ensure_positive(diameter_m, name="diameter_m")
    radius_m = diameter_m / 2.0
    dc = 1.0 / (material.conductivity_s_per_m * math.pi * radius_m * radius_m)
    depth = skin_depth_m(frequency_hz=frequency_hz, material=material)
    surface_resistance = math.sqrt(
        math.pi
        * frequency_hz
        * VACUUM_PERMEABILITY_H_PER_M
        * material.relative_permeability
        / material.conductivity_s_per_m
    )
    rf = max(dc, surface_resistance / (math.pi * diameter_m))
    return dc, rf, depth


def impedance_ratio_for_turns_ratio(turns_ratio: float) -> float:
    ensure_positive(turns_ratio, name="turns_ratio")
    return turns_ratio * turns_ratio


def turns_ratio_for_impedance_ratio(impedance_ratio: float) -> float:
    ensure_positive(impedance_ratio, name="impedance_ratio")
    return math.sqrt(impedance_ratio)
