# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Unit-safe normalization helpers."""

from __future__ import annotations

import math

from ..domain.common.units import ensure_positive


def calculate_reflection_coefficient(
    impedance_ohm: complex,
    reference_impedance_ohm: float = 50.0,
) -> complex:
    """Return the voltage reflection coefficient for a load impedance."""

    reference = ensure_positive(reference_impedance_ohm, name="reference_impedance_ohm")
    if not math.isfinite(impedance_ohm.real) or not math.isfinite(impedance_ohm.imag):
        raise ValueError("impedance_ohm must be finite")
    denominator = impedance_ohm + reference
    if denominator == 0:
        raise ValueError("reflection coefficient is undefined for -reference impedance")
    return (impedance_ohm - reference) / denominator


def calculate_swr(
    impedance_ohm: complex,
    reference_impedance_ohm: float = 50.0,
) -> float:
    """Return SWR, or infinity when the reflection magnitude is at least one."""

    gamma = calculate_reflection_coefficient(impedance_ohm, reference_impedance_ohm)
    magnitude = abs(gamma)
    if magnitude >= 1.0:
        return math.inf
    return (1.0 + magnitude) / (1.0 - magnitude)
