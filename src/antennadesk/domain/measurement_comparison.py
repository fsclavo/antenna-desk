# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compare imported measurements with a simulated impedance sweep."""

from __future__ import annotations

import math
from bisect import bisect_left
from collections.abc import Sequence
from dataclasses import dataclass

from .measurement import Measurement


@dataclass(frozen=True, slots=True)
class ImpedanceComparisonPoint:
    frequency_hz: float
    measured_ohm: complex
    simulated_ohm: complex | None
    error_ohm: float | None


@dataclass(frozen=True, slots=True)
class ImpedanceComparison:
    points: tuple[ImpedanceComparisonPoint, ...]
    mean_error_ohm: float | None
    max_error_ohm: float | None
    compared_count: int


def interpolate_impedance(
    frequencies_hz: Sequence[float],
    impedances_ohm: Sequence[complex],
    frequency_hz: float,
) -> complex | None:
    """Linearly interpolate a complex impedance, returning None outside the sweep."""

    if len(frequencies_hz) != len(impedances_ohm):
        raise ValueError("frequencies and impedances must have the same length")
    if not frequencies_hz:
        return None
    ordered = sorted(zip(frequencies_hz, impedances_ohm, strict=True))
    frequencies = [item[0] for item in ordered]
    if frequency_hz < frequencies[0] or frequency_hz > frequencies[-1]:
        return None
    index = bisect_left(frequencies, frequency_hz)
    if index < len(frequencies) and math.isclose(
        frequencies[index], frequency_hz, rel_tol=0.0, abs_tol=1e-9
    ):
        return ordered[index][1]
    if index == 0:
        return ordered[0][1]
    first_frequency, first_impedance = ordered[index - 1]
    second_frequency, second_impedance = ordered[index]
    if math.isclose(second_frequency, first_frequency, rel_tol=0.0, abs_tol=1e-9):
        return first_impedance
    ratio = (frequency_hz - first_frequency) / (second_frequency - first_frequency)
    return first_impedance + ratio * (second_impedance - first_impedance)


def compare_measurement(
    measurement: Measurement,
    frequencies_hz: Sequence[float],
    impedances_ohm: Sequence[complex],
) -> ImpedanceComparison:
    """Compare every measurement point against an interpolated simulated sweep."""

    points: list[ImpedanceComparisonPoint] = []
    for point in measurement.points:
        simulated = interpolate_impedance(
            frequencies_hz,
            impedances_ohm,
            point.frequency_hz,
        )
        error = None if simulated is None else abs(point.impedance_ohm - simulated)
        points.append(
            ImpedanceComparisonPoint(
                frequency_hz=point.frequency_hz,
                measured_ohm=point.impedance_ohm,
                simulated_ohm=simulated,
                error_ohm=error,
            )
        )
    errors = [point.error_ohm for point in points if point.error_ohm is not None]
    return ImpedanceComparison(
        points=tuple(points),
        mean_error_ohm=sum(errors) / len(errors) if errors else None,
        max_error_ohm=max(errors) if errors else None,
        compared_count=len(errors),
    )
