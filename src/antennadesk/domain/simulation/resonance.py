# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Resonance detection for impedance sweeps."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

ZERO_TOLERANCE_OHM = 1e-9


@dataclass(frozen=True, slots=True)
class ResonancePoint:
    frequency_hz: float
    impedance_ohm: complex


def find_resonances(
    frequencies_hz: Sequence[float],
    impedances_ohm: Sequence[complex],
) -> tuple[ResonancePoint, ...]:
    """Return points where the series reactance crosses or touches zero."""

    if len(frequencies_hz) != len(impedances_ohm):
        raise ValueError("frequencies and impedances must have the same length")
    if len(frequencies_hz) < 2:
        return ()

    points: list[ResonancePoint] = []
    for index in range(len(frequencies_hz) - 1):
        first_frequency = frequencies_hz[index]
        second_frequency = frequencies_hz[index + 1]
        first_impedance = impedances_ohm[index]
        second_impedance = impedances_ohm[index + 1]
        first_reactance = first_impedance.imag
        second_reactance = second_impedance.imag

        if abs(first_reactance) <= ZERO_TOLERANCE_OHM:
            points.append(
                ResonancePoint(
                    frequency_hz=first_frequency,
                    impedance_ohm=complex(first_impedance.real, 0.0),
                )
            )

        if first_reactance * second_reactance < 0.0:
            ratio = -first_reactance / (second_reactance - first_reactance)
            frequency = first_frequency + ratio * (second_frequency - first_frequency)
            resistance = first_impedance.real + ratio * (
                second_impedance.real - first_impedance.real
            )
            points.append(
                ResonancePoint(
                    frequency_hz=frequency,
                    impedance_ohm=complex(resistance, 0.0),
                )
            )

    last_frequency = frequencies_hz[-1]
    last_impedance = impedances_ohm[-1]
    if abs(last_impedance.imag) <= ZERO_TOLERANCE_OHM:
        points.append(
            ResonancePoint(
                frequency_hz=last_frequency,
                impedance_ohm=complex(last_impedance.real, 0.0),
            )
        )

    if not points:
        return ()
    deduplicated: list[ResonancePoint] = [points[0]]
    for point in points[1:]:
        if abs(point.frequency_hz - deduplicated[-1].frequency_hz) > 1e-6:
            deduplicated.append(point)
    return tuple(deduplicated)
