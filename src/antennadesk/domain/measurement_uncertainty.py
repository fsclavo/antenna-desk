# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Qualitative measurement uncertainty and documentation limits.

The assessment deliberately avoids a numerical uncertainty budget. It reports
what is documented, what is missing, and how much of the measured sweep can be
compared with a simulation. It never converts missing metadata into an invented
plus/minus value.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import pairwise

from .measurement import Measurement, MeasurementSession
from .simulation.resonance import find_resonances
from .simulation.result import SimulationResult

PARTIAL_COMPARISON_FRACTION = 0.5


class MeasurementDocumentationStatus(StrEnum):
    DOCUMENTED = "documented"
    UNCERTAIN = "uncertain"
    MISSING = "missing"


class MeasurementUncertaintyLevel(StrEnum):
    DOCUMENTED = "documented"
    PARTIAL = "partial"
    LIMITED = "limited"


@dataclass(frozen=True, slots=True)
class MeasurementUncertainty:
    """Qualitative documentation and comparison limits for one measurement."""

    level: MeasurementUncertaintyLevel
    calibration_status: MeasurementDocumentationStatus
    calibration_value: str
    reference_plane_status: MeasurementDocumentationStatus
    reference_plane_value: str
    feed_line_status: MeasurementDocumentationStatus
    feed_line_value: str
    conditions_status: MeasurementDocumentationStatus
    conditions_value: str
    session_name: str | None
    point_count: int
    start_frequency_hz: float
    stop_frequency_hz: float
    max_spacing_hz: float
    reference_impedance_ohm: float
    resonance_frequencies_hz: tuple[float, ...]
    compared_count: int | None
    coverage_fraction: float | None
    simulated_max_spacing_hz: float | None
    warnings: tuple[str, ...]

    @property
    def coverage_percent(self) -> float | None:
        if self.coverage_fraction is None:
            return None
        return self.coverage_fraction * 100.0


def _calibration_status(value: str) -> MeasurementDocumentationStatus:
    text = value.strip().lower()
    if not text:
        return MeasurementDocumentationStatus.MISSING
    recognised = ("sol", "full", "2-port", "2 port", "two-port", "calibrated")
    if any(token in text for token in recognised):
        return MeasurementDocumentationStatus.DOCUMENTED
    return MeasurementDocumentationStatus.UNCERTAIN


def _documentation_score(
    calibration: MeasurementDocumentationStatus,
    reference_plane: MeasurementDocumentationStatus,
    feed_line: MeasurementDocumentationStatus,
    conditions: MeasurementDocumentationStatus,
) -> int:
    return (
        (2 if calibration is MeasurementDocumentationStatus.DOCUMENTED else 0)
        + (1 if calibration is MeasurementDocumentationStatus.UNCERTAIN else 0)
        + (2 if reference_plane is MeasurementDocumentationStatus.DOCUMENTED else 0)
        + (1 if feed_line is MeasurementDocumentationStatus.DOCUMENTED else 0)
        + (1 if conditions is MeasurementDocumentationStatus.DOCUMENTED else 0)
    )


def _level_for_score(score: int) -> MeasurementUncertaintyLevel:
    if score >= 5:
        return MeasurementUncertaintyLevel.DOCUMENTED
    if score >= 3:
        return MeasurementUncertaintyLevel.PARTIAL
    return MeasurementUncertaintyLevel.LIMITED


def _simulation_coverage(
    measurement: Measurement,
    simulation: SimulationResult | None,
) -> tuple[int | None, float | None, float | None]:
    if simulation is None or not simulation.frequencies:
        return None, None, None
    frequencies = tuple(frequency.frequency_hz for frequency in simulation.frequencies)
    lower = min(frequencies)
    upper = max(frequencies)
    compared = sum(1 for point in measurement.points if lower <= point.frequency_hz <= upper)
    coverage = compared / len(measurement.points)
    ordered = sorted(frequencies)
    max_spacing = max((second - first for first, second in pairwise(ordered)), default=0.0)
    return compared, coverage, max_spacing


def assess_measurement_uncertainty(
    measurement: Measurement,
    *,
    session: MeasurementSession | None = None,
    simulation: SimulationResult | None = None,
) -> MeasurementUncertainty:
    """Assess documentation quality and comparison limits for a measurement."""

    calibration = _calibration_status(measurement.calibration)
    reference_plane = (
        MeasurementDocumentationStatus.DOCUMENTED
        if measurement.reference_plane.strip()
        else MeasurementDocumentationStatus.MISSING
    )
    feed_line = (
        MeasurementDocumentationStatus.DOCUMENTED
        if measurement.feed_line.strip()
        else MeasurementDocumentationStatus.MISSING
    )
    conditions_value = session.conditions.strip() if session is not None else ""
    conditions = (
        MeasurementDocumentationStatus.DOCUMENTED
        if conditions_value
        else MeasurementDocumentationStatus.MISSING
    )
    score = _documentation_score(calibration, reference_plane, feed_line, conditions)
    level = _level_for_score(score)

    points = measurement.points
    start_frequency = points[0].frequency_hz
    stop_frequency = points[-1].frequency_hz
    max_spacing = max(
        (second.frequency_hz - first.frequency_hz for first, second in pairwise(points)),
        default=0.0,
    )
    resonances = find_resonances(
        [point.frequency_hz for point in points],
        [point.impedance_ohm for point in points],
    )
    compared, coverage, simulated_spacing = _simulation_coverage(measurement, simulation)

    warnings: list[str] = []
    if calibration is MeasurementDocumentationStatus.MISSING:
        warnings.append("measurement.uncertainty.warning.calibration_missing")
    elif calibration is MeasurementDocumentationStatus.UNCERTAIN:
        warnings.append("measurement.uncertainty.warning.calibration_unverified")
    if reference_plane is MeasurementDocumentationStatus.MISSING:
        warnings.append("measurement.uncertainty.warning.reference_plane_missing")
    if feed_line is MeasurementDocumentationStatus.MISSING:
        warnings.append("measurement.uncertainty.warning.feed_line_missing")
    if conditions is MeasurementDocumentationStatus.MISSING:
        warnings.append("measurement.uncertainty.warning.conditions_missing")
    if not resonances:
        warnings.append("measurement.uncertainty.warning.no_resonance")
    elif len(resonances) > 1:
        warnings.append("measurement.uncertainty.warning.multiple_resonances")
    if compared == 0:
        warnings.append("measurement.uncertainty.warning.no_comparison")
    elif coverage is not None and coverage < PARTIAL_COMPARISON_FRACTION:
        warnings.append("measurement.uncertainty.warning.partial_comparison")

    return MeasurementUncertainty(
        level=level,
        calibration_status=calibration,
        calibration_value=measurement.calibration.strip(),
        reference_plane_status=reference_plane,
        reference_plane_value=measurement.reference_plane.strip(),
        feed_line_status=feed_line,
        feed_line_value=measurement.feed_line.strip(),
        conditions_status=conditions,
        conditions_value=conditions_value,
        session_name=session.name if session is not None else None,
        point_count=len(points),
        start_frequency_hz=start_frequency,
        stop_frequency_hz=stop_frequency,
        max_spacing_hz=max_spacing,
        reference_impedance_ohm=measurement.reference_impedance_ohm,
        resonance_frequencies_hz=tuple(point.frequency_hz for point in resonances),
        compared_count=compared,
        coverage_fraction=coverage,
        simulated_max_spacing_hz=simulated_spacing,
        warnings=tuple(warnings),
    )
