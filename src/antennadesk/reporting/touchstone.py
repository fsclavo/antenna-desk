# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Write simulation impedance sweeps as one-port Touchstone files."""

from __future__ import annotations

import math
from collections.abc import Sequence

from ..domain.common.units import ensure_positive
from ..domain.measurement import reflection_coefficient

_FREQUENCY_SCALES = {
    "HZ": 1.0,
    "KHZ": 1_000.0,
    "MHZ": 1_000_000.0,
    "GHZ": 1_000_000_000.0,
}
_FREQUENCY_LABELS = {
    "HZ": "Hz",
    "KHZ": "kHz",
    "MHZ": "MHz",
    "GHZ": "GHz",
}


def _format_number(value: float) -> str:
    return f"{value:.12g}"


def _clean_comment(value: str) -> str:
    return value.replace("\r", " ").replace("\n", " ").encode("ascii", "replace").decode("ascii")


def format_touchstone_s1p(
    points: Sequence[tuple[float, complex]],
    reference_impedance_ohm: float,
    *,
    frequency_unit: str = "MHz",
    comments: Sequence[str] = (),
) -> str:
    """Render impedance points as a one-port Touchstone RI document.

    ``points`` contains ``(frequency_hz, impedance_ohm)`` pairs. The impedance
    is converted to S11 against ``reference_impedance_ohm``.
    """

    ensure_positive(reference_impedance_ohm, name="reference_impedance_ohm")
    unit = frequency_unit.upper()
    if unit not in _FREQUENCY_SCALES:
        raise ValueError("frequency_unit must be Hz, kHz, MHz, or GHz")
    if not points:
        raise ValueError("at least one impedance point is required")

    lines = [
        "! AntennaDesk one-port Touchstone export",
        "! Impedance is the simulated result after the configured feed chain.",
        f"! Reference impedance: {_format_number(reference_impedance_ohm)} ohm",
    ]
    for comment in comments:
        cleaned = _clean_comment(comment).strip()
        if cleaned:
            lines.append(f"! {cleaned}")
    lines.append(f"# {_FREQUENCY_LABELS[unit]} S RI R {_format_number(reference_impedance_ohm)}")

    scale = _FREQUENCY_SCALES[unit]
    for frequency_hz, impedance_ohm in points:
        if not math.isfinite(frequency_hz) or frequency_hz <= 0.0:
            raise ValueError("frequencies must be positive and finite")
        if not math.isfinite(impedance_ohm.real) or not math.isfinite(impedance_ohm.imag):
            raise ValueError("impedances must be finite")
        reflection = reflection_coefficient(impedance_ohm, reference_impedance_ohm)
        lines.append(
            " ".join(
                (
                    _format_number(frequency_hz / scale),
                    _format_number(reflection.real),
                    _format_number(reflection.imag),
                )
            )
        )
    return "\n".join(lines) + "\n"
