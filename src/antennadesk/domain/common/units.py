# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Canonical units and explicit conversions.

The domain stores lengths in meters, frequencies in hertz, impedance in ohms,
and conductivity in siemens per meter.  The UI may present other units, but it
must convert through these helpers at the boundary.
"""

from __future__ import annotations

import math

SPEED_OF_LIGHT_M_PER_S = 299_792_458.0
SECONDS_PER_MINUTE = 60.0


def ensure_finite(value: float, *, name: str) -> float:
    """Return *value* if it is finite, otherwise raise ``ValueError``."""

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def ensure_positive(value: float, *, name: str) -> float:
    """Return *value* if it is finite and greater than zero."""

    ensure_finite(value, name=name)
    if value <= 0.0:
        raise ValueError(f"{name} must be positive")
    return value


def ensure_non_negative(value: float, *, name: str) -> float:
    """Return *value* if it is finite and greater than or equal to zero."""

    ensure_finite(value, name=name)
    if value < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return value


# Length --------------------------------------------------------------------


def m_from_mm(value: float) -> float:
    return ensure_finite(value, name="length_mm") / 1_000.0


def m_from_cm(value: float) -> float:
    return ensure_finite(value, name="length_cm") / 100.0


def m_from_in(value: float) -> float:
    return ensure_finite(value, name="length_in") * 0.0254


def m_from_ft(value: float) -> float:
    return ensure_finite(value, name="length_ft") * 0.3048


def mm_from_m(value: float) -> float:
    return ensure_finite(value, name="length_m") * 1_000.0


def cm_from_m(value: float) -> float:
    return ensure_finite(value, name="length_m") * 100.0


def in_from_m(value: float) -> float:
    return ensure_finite(value, name="length_m") / 0.0254


def ft_from_m(value: float) -> float:
    return ensure_finite(value, name="length_m") / 0.3048


# Frequency -----------------------------------------------------------------


def hz_from_khz(value: float) -> float:
    return ensure_finite(value, name="frequency_khz") * 1_000.0


def hz_from_mhz(value: float) -> float:
    return ensure_finite(value, name="frequency_mhz") * 1_000_000.0


def hz_from_ghz(value: float) -> float:
    return ensure_finite(value, name="frequency_ghz") * 1_000_000_000.0


def khz_from_hz(value: float) -> float:
    return ensure_finite(value, name="frequency_hz") / 1_000.0


def mhz_from_hz(value: float) -> float:
    return ensure_finite(value, name="frequency_hz") / 1_000_000.0


def ghz_from_hz(value: float) -> float:
    return ensure_finite(value, name="frequency_hz") / 1_000_000_000.0


def wavelength_m(frequency_hz: float, *, velocity_factor: float = 1.0) -> float:
    """Return the wavelength in meters for a frequency in hertz."""

    frequency = ensure_positive(frequency_hz, name="frequency_hz")
    factor = ensure_positive(velocity_factor, name="velocity_factor")
    return SPEED_OF_LIGHT_M_PER_S * factor / frequency


# Angles --------------------------------------------------------------------


def degrees_to_radians(value: float) -> float:
    return math.radians(ensure_finite(value, name="angle_degrees"))


def radians_to_degrees(value: float) -> float:
    return math.degrees(ensure_finite(value, name="angle_radians"))


def normalize_azimuth_degrees(value: float) -> float:
    """Normalize an azimuth to the half-open interval ``[0, 360)``."""

    return ensure_finite(value, name="azimuth_degrees") % 360.0
