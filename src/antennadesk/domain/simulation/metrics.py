# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Decision metrics derived from normalized simulation results.

All definitions here are descriptive. They reuse the stored far-field grid and
never claim more precision than its angular sampling.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise

from .pattern import front_to_back_db, max_power_gain_db, takeoff_angle_deg
from .result import FarFieldPoint, FrequencyResult


@dataclass(frozen=True, slots=True)
class SWRBandwidth:
    limit: float
    center_hz: float
    lower_hz: float | None
    upper_hz: float | None
    bandwidth_hz: float | None
    bracketed: bool


@dataclass(frozen=True, slots=True)
class Beamwidth:
    width_deg: float | None
    peak_angle_deg: float | None
    resolution_deg: float | None
    bracketed: bool


@dataclass(frozen=True, slots=True)
class CircularMetrics:
    axial_ratio_db: float | None
    sense: str | None
    cp_gain_db: float | None
    cross_polar_discrimination_db: float | None


@dataclass(frozen=True, slots=True)
class DecisionMetrics:
    frequency_hz: float
    swr_bandwidth_2_1: SWRBandwidth
    hpbw_azimuth: Beamwidth
    hpbw_elevation: Beamwidth
    front_to_back_db: float | None
    sidelobe_level_db: float | None
    takeoff_deg: float | None
    efficiency_percent: float | None
    directivity_db: float | None
    realized_gain_db: float | None
    max_gain_db: float | None
    axial_ratio_db: float | None
    polarization_sense: str | None
    cp_gain_db: float | None
    cross_polar_discrimination_db: float | None
    pattern_resolution_deg: float | None


def swr_bandwidth_rows(
    frequencies_hz: Sequence[float],
    swr_values: Sequence[float],
    *,
    swr_limit: float = 2.0,
) -> tuple[SWRBandwidth, ...]:
    """Return the contiguous SWR-limited bandwidth around every sample.

    A band that reaches a sweep edge is reported with ``bracketed=False`` and
    ``bandwidth_hz=None``; its sampled lower/upper edge is still available.
    """

    if len(frequencies_hz) != len(swr_values):
        raise ValueError("frequencies and SWR values must have the same length")
    if swr_limit <= 1.0:
        raise ValueError("swr_limit must be greater than 1")
    ordered = sorted(zip(frequencies_hz, swr_values, strict=True))
    if not ordered:
        return ()
    passing = [math.isfinite(swr) and swr <= swr_limit for _, swr in ordered]
    segments: list[tuple[int, int]] = []
    start: int | None = None
    for index, is_pass in enumerate(passing):
        if is_pass and start is None:
            start = index
        elif not is_pass and start is not None:
            segments.append((start, index - 1))
            start = None
    if start is not None:
        segments.append((start, len(ordered) - 1))

    results: list[SWRBandwidth] = [
        SWRBandwidth(swr_limit, frequency, None, None, None, False) for frequency, _ in ordered
    ]
    for first, last in segments:
        if first > 0:
            lower = _boundary(ordered[first - 1], ordered[first], swr_limit)
            low_bracketed = True
        else:
            lower = ordered[0][0]
            low_bracketed = False
        if last < len(ordered) - 1:
            upper = _boundary(ordered[last], ordered[last + 1], swr_limit)
            high_bracketed = True
        else:
            upper = ordered[-1][0]
            high_bracketed = False
        bracketed = low_bracketed and high_bracketed and upper >= lower
        bandwidth = upper - lower if bracketed else None
        for index in range(first, last + 1):
            frequency = ordered[index][0]
            results[index] = SWRBandwidth(
                swr_limit,
                frequency,
                lower,
                upper,
                bandwidth,
                bracketed,
            )
    return tuple(results)


def measure_swr_bandwidth(
    frequencies_hz: Sequence[float],
    swr_values: Sequence[float],
    *,
    center_hz: float,
    swr_limit: float = 2.0,
) -> SWRBandwidth:
    rows = swr_bandwidth_rows(
        frequencies_hz,
        swr_values,
        swr_limit=swr_limit,
    )
    if not rows:
        return SWRBandwidth(swr_limit, center_hz, None, None, None, False)
    ordered = sorted(zip(frequencies_hz, swr_values, strict=True))
    index = min(
        range(len(ordered)),
        key=lambda item: abs(ordered[item][0] - center_hz),
    )
    return rows[index]


def measure_bandwidth_hz(
    frequencies_hz: Sequence[float],
    swr_values: Sequence[float],
    *,
    center_hz: float,
    swr_limit: float,
) -> float:
    """Compatibility wrapper used by the length optimizer."""

    return (
        measure_swr_bandwidth(
            frequencies_hz,
            swr_values,
            center_hz=center_hz,
            swr_limit=swr_limit,
        ).bandwidth_hz
        or 0.0
    )


def _boundary(
    first: tuple[float, float],
    second: tuple[float, float],
    limit: float,
) -> float:
    first_frequency, first_swr = first
    second_frequency, second_swr = second
    if math.isclose(first_swr, second_swr):
        return first_frequency
    ratio = (limit - first_swr) / (second_swr - first_swr)
    return first_frequency + (second_frequency - first_frequency) * min(max(ratio, 0.0), 1.0)


def half_power_beamwidth(
    points: Sequence[FarFieldPoint],
    *,
    axis: str,
    cut_value: float,
) -> Beamwidth:
    """Return the -3 dB beamwidth of one linear pattern cut.

    ``axis='phi'`` reads an azimuth cut at a fixed theta and handles 0/360
    wrapping. ``axis='theta'`` reads an elevation cut at a fixed phi.
    """

    if axis not in {"phi", "theta"}:
        raise ValueError("axis must be 'phi' or 'theta'")
    other = "theta" if axis == "phi" else "phi"
    values: list[tuple[float, float]] = []
    for point in points:
        gain = point.gain_total_db
        if gain is None or not math.isfinite(gain) or gain <= -100.0:
            continue
        if abs(getattr(point, f"{other}_deg") - cut_value) > 1e-6:
            continue
        values.append((getattr(point, f"{axis}_deg"), gain))
    if len(values) < 3:
        return Beamwidth(None, None, None, False)
    values.sort(key=lambda item: item[0])
    resolution = min(second[0] - first[0] for first, second in pairwise(values))
    peak_index = max(range(len(values)), key=lambda index: values[index][1])
    peak_angle, peak_gain = values[peak_index]
    wrap = axis == "phi"
    if wrap:
        extended = (
            [(angle - 360.0, gain) for angle, gain in values]
            + values
            + [(angle + 360.0, gain) for angle, gain in values]
        )
        peak_index = len(values) + peak_index
    else:
        extended = values
    threshold = peak_gain - 3.010299956639812
    left_index = peak_index
    while left_index > 0 and extended[left_index - 1][1] >= threshold:
        left_index -= 1
    right_index = peak_index
    while right_index < len(extended) - 1 and extended[right_index + 1][1] >= threshold:
        right_index += 1
    if left_index == 0 or right_index == len(extended) - 1:
        return Beamwidth(None, peak_angle, resolution, False)
    lower = _crossing(extended[left_index - 1], extended[left_index], threshold)
    upper = _crossing(extended[right_index], extended[right_index + 1], threshold)
    return Beamwidth(
        width_deg=max(upper - lower, 0.0),
        peak_angle_deg=peak_angle,
        resolution_deg=resolution,
        bracketed=True,
    )


def _crossing(
    first: tuple[float, float],
    second: tuple[float, float],
    threshold: float,
) -> float:
    if math.isclose(first[1], second[1]):
        return first[0]
    ratio = (threshold - first[1]) / (second[1] - first[1])
    return first[0] + (second[0] - first[0]) * min(max(ratio, 0.0), 1.0)


def sidelobe_level_db(
    points: Sequence[FarFieldPoint],
    *,
    axis: str,
    cut_value: float,
) -> float | None:
    """Return the largest non-main local maximum relative to the peak."""

    other = "theta" if axis == "phi" else "phi"
    values = [
        (getattr(point, f"{axis}_deg"), point.gain_total_db)
        for point in points
        if point.gain_total_db is not None
        and math.isfinite(point.gain_total_db)
        and point.gain_total_db > -100.0
        and abs(getattr(point, f"{other}_deg") - cut_value) <= 1e-6
    ]
    if len(values) < 4:
        return None
    values.sort(key=lambda item: item[0])
    peak = max(values, key=lambda item: item[1])
    local: list[float] = []
    for index in range(1, len(values) - 1):
        gain = values[index][1]
        if (
            gain >= values[index - 1][1]
            and gain >= values[index + 1][1]
            and not math.isclose(gain, peak[1])
        ):
            local.append(gain)
    if not local:
        return None
    return peak[1] - max(local)


def circular_metrics(frequency: FrequencyResult) -> CircularMetrics:
    peak = _peak_point(frequency)
    if peak is None:
        return CircularMetrics(None, None, None, None)
    raw = peak.axial_ratio
    if raw is None or not math.isfinite(raw) or raw <= 0.0:
        return CircularMetrics(None, _sense(peak.polarization), None, None)
    axial_ratio = max(raw, 1.0 / raw)
    axial_ratio_db = 20.0 * math.log10(axial_ratio)
    gain = peak.gain_total_db
    mismatch = 10.0 * math.log10((1.0 + axial_ratio) ** 2 / (2.0 * (1.0 + axial_ratio**2)))
    cp_gain = gain + mismatch if gain is not None and math.isfinite(gain) else None
    if axial_ratio <= 1.0 + 1e-9:
        xpd = math.inf
    else:
        xpd = 20.0 * math.log10((axial_ratio + 1.0) / (axial_ratio - 1.0))
    return CircularMetrics(
        axial_ratio_db=axial_ratio_db,
        sense=_sense(peak.polarization),
        cp_gain_db=cp_gain,
        cross_polar_discrimination_db=xpd,
    )


def decision_metrics(
    frequency: FrequencyResult,
    all_frequencies: Sequence[FrequencyResult],
    *,
    bandwidth: SWRBandwidth | None = None,
) -> DecisionMetrics:
    if bandwidth is None:
        bandwidth = measure_swr_bandwidth(
            [item.frequency_hz for item in all_frequencies],
            [item.swr for item in all_frequencies],
            center_hz=frequency.frequency_hz,
        )
    peak = _peak_point(frequency)
    if peak is None:
        azimuth = Beamwidth(None, None, None, False)
        elevation = Beamwidth(None, None, None, False)
        sidelobe = None
        takeoff = None
        resolution = None
    else:
        azimuth = half_power_beamwidth(
            frequency.far_field,
            axis="phi",
            cut_value=peak.theta_deg,
        )
        elevation = half_power_beamwidth(
            frequency.far_field,
            axis="theta",
            cut_value=peak.phi_deg,
        )
        sidelobe = _max_optional(
            sidelobe_level_db(
                frequency.far_field,
                axis="phi",
                cut_value=peak.theta_deg,
            ),
            sidelobe_level_db(
                frequency.far_field,
                axis="theta",
                cut_value=peak.phi_deg,
            ),
        )
        takeoff = takeoff_angle_deg(peak.theta_deg)
        resolution = _min_optional(azimuth.resolution_deg, elevation.resolution_deg)
    circular = circular_metrics(frequency)
    return DecisionMetrics(
        frequency_hz=frequency.frequency_hz,
        swr_bandwidth_2_1=bandwidth,
        hpbw_azimuth=azimuth,
        hpbw_elevation=elevation,
        front_to_back_db=front_to_back_db(frequency.far_field),
        sidelobe_level_db=sidelobe,
        takeoff_deg=takeoff,
        efficiency_percent=(
            frequency.power_budget.efficiency_percent
            if frequency.power_budget is not None
            else None
        ),
        directivity_db=frequency.directivity_db,
        realized_gain_db=frequency.realized_gain_db,
        max_gain_db=max_power_gain_db(frequency.far_field),
        axial_ratio_db=circular.axial_ratio_db,
        polarization_sense=circular.sense,
        cp_gain_db=circular.cp_gain_db,
        cross_polar_discrimination_db=circular.cross_polar_discrimination_db,
        pattern_resolution_deg=resolution,
    )


def _peak_point(frequency: FrequencyResult) -> FarFieldPoint | None:
    valid = [
        point
        for point in frequency.far_field
        if point.gain_total_db is not None
        and math.isfinite(point.gain_total_db)
        and point.gain_total_db > -100.0
    ]
    return max(valid, key=lambda point: point.gain_total_db or -math.inf, default=None)


def _sense(polarization: str | None) -> str | None:
    if not polarization:
        return None
    value = polarization.upper()
    if "RIGHT" in value or "RHCP" in value:
        return "RHCP"
    if "LEFT" in value or "LHCP" in value:
        return "LHCP"
    if "LINEAR" in value:
        return "linear"
    return polarization.lower()


def _max_optional(first: float | None, second: float | None) -> float | None:
    values = [value for value in (first, second) if value is not None and math.isfinite(value)]
    return max(values) if values else None


def _min_optional(first: float | None, second: float | None) -> float | None:
    values = [value for value in (first, second) if value is not None and math.isfinite(value)]
    return min(values) if values else None
