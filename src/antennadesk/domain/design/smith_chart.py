# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Normalized impedance and Smith-chart geometry.

The Smith chart is a presentation of the voltage reflection coefficient.  This
module keeps the projection and the reference-plane selection in the domain so
widgets only draw points; they do not perform electromagnetic calculations.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from ..antennas.feed_line import FeedLine
from ..common.reflection import calculate_reflection_coefficient, calculate_swr
from ..common.units import ensure_positive
from ..measurement import Measurement
from ..simulation.result import FrequencyResult, SimulationResult


class SmithPlane(StrEnum):
    """Reference plane shown on the Smith chart."""

    SIMULATED = "simulated"
    ANTENNA = "antenna"
    FEED_LINE = "feed_line"


@dataclass(frozen=True, slots=True)
class SmithPoint:
    """One normalized impedance point on the Smith chart."""

    frequency_hz: float
    impedance_ohm: complex
    reference_impedance_ohm: float
    gamma: complex
    swr: float

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.reference_impedance_ohm, name="reference_impedance_ohm")
        if not math.isfinite(self.impedance_ohm.real) or not math.isfinite(self.impedance_ohm.imag):
            raise ValueError("impedance_ohm must be finite")
        if not math.isfinite(self.gamma.real) or not math.isfinite(self.gamma.imag):
            raise ValueError("gamma must be finite")

    @property
    def gamma_magnitude(self) -> float:
        return abs(self.gamma)

    @property
    def gamma_phase_deg(self) -> float:
        return math.degrees(math.atan2(self.gamma.imag, self.gamma.real))

    @property
    def normalized_impedance(self) -> complex:
        return self.impedance_ohm / self.reference_impedance_ohm


def smith_point(
    frequency_hz: float,
    impedance_ohm: complex,
    reference_impedance_ohm: float,
) -> SmithPoint:
    """Build one Smith point with the reflection coefficient and SWR."""

    gamma = calculate_reflection_coefficient(impedance_ohm, reference_impedance_ohm)
    return SmithPoint(
        frequency_hz=frequency_hz,
        impedance_ohm=impedance_ohm,
        reference_impedance_ohm=reference_impedance_ohm,
        gamma=gamma,
        swr=calculate_swr(impedance_ohm, reference_impedance_ohm),
    )


def smith_locus(
    frequencies_hz: Sequence[float],
    impedances_ohm: Sequence[complex],
    reference_impedance_ohm: float,
) -> tuple[SmithPoint, ...]:
    """Return the Smith locus for parallel frequency and impedance sequences."""

    if len(frequencies_hz) != len(impedances_ohm):
        raise ValueError("frequencies_hz and impedances_ohm must have the same length")
    return tuple(
        smith_point(frequency, impedance, reference_impedance_ohm)
        for frequency, impedance in zip(frequencies_hz, impedances_ohm, strict=True)
    )


def smith_points_for_result(
    result: SimulationResult,
    plane: SmithPlane = SmithPlane.SIMULATED,
) -> tuple[SmithPoint, ...]:
    """Return the locus at one supported reference plane.

    ``SIMULATED`` is the post-chain impedance stored in ``FrequencyResult``.
    ``ANTENNA`` is the raw primary-source impedance before the ideal feed
    transformer.  ``FEED_LINE`` applies only the project feed line to the
    antenna-side load; it deliberately excludes the matching network and is
    labelled as a preview.
    """

    spec = result.spec
    points: list[SmithPoint] = []
    for frequency in result.frequencies:
        raw = _raw_impedance(frequency)
        if plane is SmithPlane.ANTENNA:
            impedance = raw
        elif (
            plane is SmithPlane.FEED_LINE
            and spec.feed_line is not None
            and spec.feed_line.is_active
        ):
            load = raw / spec.feed_transformer_ratio
            impedance = spec.feed_line.input_impedance(load, frequency.frequency_hz)
        else:
            impedance = frequency.impedance_ohm
        points.append(smith_point(frequency.frequency_hz, impedance, spec.reference_impedance_ohm))
    return tuple(points)


def available_smith_planes(result: SimulationResult | None) -> tuple[SmithPlane, ...]:
    """Return the reference planes that have data for this result."""

    planes = [SmithPlane.SIMULATED]
    if result is None:
        return tuple(planes)
    if any(frequency.source_results for frequency in result.frequencies):
        planes.append(SmithPlane.ANTENNA)
    feed_line = result.spec.feed_line
    if feed_line is not None and feed_line.is_active:
        planes.append(SmithPlane.FEED_LINE)
    return tuple(planes)


def smith_points_for_measurement(
    measurement: Measurement,
    reference_impedance_ohm: float,
) -> tuple[SmithPoint, ...]:
    """Normalize a measured sweep to the display reference impedance."""

    return smith_locus(
        [point.frequency_hz for point in measurement.points],
        [point.impedance_ohm for point in measurement.points],
        reference_impedance_ohm,
    )


def transform_with_feed_line(
    points: Sequence[SmithPoint],
    feed_line: FeedLine,
) -> tuple[SmithPoint, ...]:
    """Return a preview locus after a feed line."""

    return tuple(
        smith_point(
            point.frequency_hz,
            feed_line.input_impedance(point.impedance_ohm, point.frequency_hz),
            point.reference_impedance_ohm,
        )
        for point in points
    )


def constant_resistance_circle_points(
    resistance: float,
    *,
    count: int = 181,
) -> tuple[complex, ...]:
    """Return a normalized constant-resistance circle in the gamma plane."""

    if resistance < 0.0 or not math.isfinite(resistance):
        raise ValueError("normalized resistance must be finite and non-negative")
    if count < 2:
        raise ValueError("count must be at least 2")
    center = complex(resistance / (1.0 + resistance), 0.0)
    radius = 1.0 / (1.0 + resistance)
    return tuple(
        center + radius * complex(math.cos(angle), math.sin(angle))
        for angle in (math.tau * index / (count - 1) for index in range(count))
    )


def constant_reactance_arc_points(
    reactance: float,
    *,
    count: int = 181,
) -> tuple[complex, ...]:
    """Return a normalized constant-reactance arc inside the unit circle.

    A zero reactance is the real axis from -1 to 1.  Non-zero values are
    sampled from normalized resistance zero toward infinity, which traces the
    correct arc without special-casing the circle angle direction.
    """

    if not math.isfinite(reactance):
        raise ValueError("normalized reactance must be finite")
    if count < 2:
        raise ValueError("count must be at least 2")
    if reactance == 0.0:
        return tuple(complex(-1.0 + 2.0 * index / (count - 1), 0.0) for index in range(count))
    points: list[complex] = []
    for index in range(count):
        fraction = index / (count - 1)
        resistance = math.tan(fraction * math.pi / 2.0)
        impedance = complex(resistance, reactance)
        gamma = (impedance - 1.0) / (impedance + 1.0)
        points.append(gamma)
    return tuple(points)


def _raw_impedance(frequency: FrequencyResult) -> complex:
    if frequency.source_results:
        return frequency.source_results[0].impedance_ohm
    return frequency.impedance_ohm
