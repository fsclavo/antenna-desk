# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compare imported measurements with a simulated impedance sweep."""

from __future__ import annotations

import math
from bisect import bisect_left
from collections.abc import Sequence
from dataclasses import dataclass

from .measurement import Measurement, swr_for_impedance
from .simulation.resonance import ResonancePoint, find_resonances


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


@dataclass(frozen=True, slots=True)
class MeasurementPairPoint:
    frequency_hz: float
    before_ohm: complex
    after_ohm: complex
    before_swr: float
    after_swr: float
    impedance_delta_ohm: float
    swr_delta: float | None


@dataclass(frozen=True, slots=True)
class MeasurementPairComparison:
    points: tuple[MeasurementPairPoint, ...]
    compared_count: int
    mean_impedance_delta_ohm: float | None
    max_impedance_delta_ohm: float | None
    mean_swr_before: float | None
    mean_swr_after: float | None
    before_resonances: tuple[ResonancePoint, ...]
    after_resonances: tuple[ResonancePoint, ...]
    resonance_shift_hz: float | None


def _overlap_frequencies(before: Measurement, after: Measurement) -> tuple[float, ...]:
    before_frequencies = [point.frequency_hz for point in before.points]
    after_frequencies = [point.frequency_hz for point in after.points]
    lower = max(min(before_frequencies), min(after_frequencies))
    upper = min(max(before_frequencies), max(after_frequencies))
    if lower > upper:
        return ()
    candidates = {
        frequency
        for frequency in (*before_frequencies, *after_frequencies)
        if lower <= frequency <= upper
    }
    return tuple(sorted(candidates))


def compare_measurement_pair(
    before: Measurement,
    after: Measurement,
    *,
    reference_impedance_ohm: float = 50.0,
) -> MeasurementPairComparison:
    """Compare two measurements on their overlapping frequency range.

    Frequencies from both sweeps are aligned by linear interpolation inside the
    overlap.  The function never extrapolates, so a compared point always has a
    measured value on both sides.  SWR uses the explicit comparison reference
    impedance, not each measurement's calibration impedance.
    """

    before_resonances = find_resonances(
        [point.frequency_hz for point in before.points],
        [point.impedance_ohm for point in before.points],
    )
    after_resonances = find_resonances(
        [point.frequency_hz for point in after.points],
        [point.impedance_ohm for point in after.points],
    )
    resonance_shift = (
        after_resonances[0].frequency_hz - before_resonances[0].frequency_hz
        if len(before_resonances) == 1 and len(after_resonances) == 1
        else None
    )

    points: list[MeasurementPairPoint] = []
    for frequency in _overlap_frequencies(before, after):
        before_impedance = interpolate_impedance(
            [point.frequency_hz for point in before.points],
            [point.impedance_ohm for point in before.points],
            frequency,
        )
        after_impedance = interpolate_impedance(
            [point.frequency_hz for point in after.points],
            [point.impedance_ohm for point in after.points],
            frequency,
        )
        if before_impedance is None or after_impedance is None:
            continue
        before_swr = swr_for_impedance(before_impedance, reference_impedance_ohm)
        after_swr = swr_for_impedance(after_impedance, reference_impedance_ohm)
        points.append(
            MeasurementPairPoint(
                frequency_hz=frequency,
                before_ohm=before_impedance,
                after_ohm=after_impedance,
                before_swr=before_swr,
                after_swr=after_swr,
                impedance_delta_ohm=abs(after_impedance - before_impedance),
                swr_delta=(
                    after_swr - before_swr
                    if math.isfinite(before_swr) and math.isfinite(after_swr)
                    else None
                ),
            )
        )

    impedance_deltas = [point.impedance_delta_ohm for point in points]
    before_swrs = [point.before_swr for point in points]
    after_swrs = [point.after_swr for point in points]
    return MeasurementPairComparison(
        points=tuple(points),
        compared_count=len(points),
        mean_impedance_delta_ohm=(
            sum(impedance_deltas) / len(impedance_deltas) if impedance_deltas else None
        ),
        max_impedance_delta_ohm=max(impedance_deltas) if impedance_deltas else None,
        mean_swr_before=sum(before_swrs) / len(before_swrs) if before_swrs else None,
        mean_swr_after=sum(after_swrs) / len(after_swrs) if after_swrs else None,
        before_resonances=before_resonances,
        after_resonances=after_resonances,
        resonance_shift_hz=resonance_shift,
    )
