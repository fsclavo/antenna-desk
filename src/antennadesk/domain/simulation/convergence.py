# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Self-consistency results for a segmentation-density ladder."""

from __future__ import annotations

import csv
import io
import math
from dataclasses import dataclass
from enum import StrEnum


class ConvergenceVerdict(StrEnum):
    CONVERGED = "converged"
    MARGINAL = "marginal"
    NOT_CONVERGED = "not_converged"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True, slots=True)
class ConvergenceThresholds:
    """Absolute/relative changes accepted between the two finest densities.

    These are self-consistency thresholds, not accuracy limits. The marginal
    band multiplies every threshold by ``marginal_factor``.
    """

    resistance_fraction: float = 0.02
    reactance_fraction: float = 0.02
    magnitude_fraction: float = 0.02
    swr_absolute: float = 0.05
    gain_db: float = 0.2
    takeoff_deg: float = 2.0
    marginal_factor: float = 2.5

    def __post_init__(self) -> None:
        for name, value in (
            ("resistance_fraction", self.resistance_fraction),
            ("reactance_fraction", self.reactance_fraction),
            ("magnitude_fraction", self.magnitude_fraction),
            ("swr_absolute", self.swr_absolute),
            ("gain_db", self.gain_db),
            ("takeoff_deg", self.takeoff_deg),
        ):
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")
        if not math.isfinite(self.marginal_factor) or self.marginal_factor < 1.0:
            raise ValueError("marginal_factor must be finite and at least 1")


DEFAULT_CONVERGENCE_THRESHOLDS = ConvergenceThresholds()


@dataclass(frozen=True, slots=True)
class ConvergenceWireMetric:
    wire_id: str
    segments: int
    segment_length_m: float
    radius_m: float

    @property
    def segment_to_radius_ratio(self) -> float:
        return self.segment_length_m / self.radius_m if self.radius_m > 0.0 else math.inf


@dataclass(frozen=True, slots=True)
class ConvergencePoint:
    density_wavelengths: float
    total_segments: int
    resistance_ohm: float
    reactance_ohm: float
    impedance_magnitude_ohm: float
    swr: float
    wire_metrics: tuple[ConvergenceWireMetric, ...] = ()
    max_gain_db: float | None = None
    takeoff_deg: float | None = None
    diagnostics: tuple[str, ...] = ()
    error: str | None = None

    @property
    def valid(self) -> bool:
        return self.error is None and all(
            math.isfinite(value) for value in (self.resistance_ohm, self.reactance_ohm, self.swr)
        )


@dataclass(frozen=True, slots=True)
class ConvergenceDelta:
    resistance_fraction: float
    reactance_fraction: float
    magnitude_fraction: float
    swr_absolute: float
    gain_db: float | None
    takeoff_deg: float | None


@dataclass(frozen=True, slots=True)
class ConvergenceResult:
    points: tuple[ConvergencePoint, ...]
    thresholds: ConvergenceThresholds = DEFAULT_CONVERGENCE_THRESHOLDS
    cancelled: bool = False
    error: str | None = None

    @property
    def valid_points(self) -> tuple[ConvergencePoint, ...]:
        return tuple(point for point in self.points if point.valid)

    @property
    def incomplete(self) -> bool:
        return self.cancelled or len(self.valid_points) < 2

    @property
    def delta(self) -> ConvergenceDelta | None:
        valid = self.valid_points
        if len(valid) < 2:
            return None
        first, second = valid[-2], valid[-1]
        return _delta(first, second)

    @property
    def verdict(self) -> ConvergenceVerdict:
        valid = self.valid_points
        if self.cancelled:
            return ConvergenceVerdict.INCOMPLETE
        if len(valid) < 2:
            return ConvergenceVerdict.NOT_CONVERGED
        if any(not point.valid for point in self.points):
            return ConvergenceVerdict.NOT_CONVERGED
        delta = self.delta
        if delta is None:
            return ConvergenceVerdict.INCOMPLETE
        if _within(delta, self.thresholds, 1.0):
            return ConvergenceVerdict.CONVERGED
        if _within(delta, self.thresholds, self.thresholds.marginal_factor):
            return ConvergenceVerdict.MARGINAL
        return ConvergenceVerdict.NOT_CONVERGED

    @property
    def resistance_spread_fraction(self) -> float | None:
        return _spread_fraction([point.resistance_ohm for point in self.valid_points])

    @property
    def reactance_spread_ohm(self) -> float | None:
        values = [point.reactance_ohm for point in self.valid_points]
        return max(values) - min(values) if values else None

    @property
    def swr_spread(self) -> float | None:
        values = [point.swr for point in self.valid_points]
        return max(values) - min(values) if values else None

    @property
    def gain_spread_db(self) -> float | None:
        values = [
            point.max_gain_db
            for point in self.valid_points
            if point.max_gain_db is not None and math.isfinite(point.max_gain_db)
        ]
        return max(values) - min(values) if len(values) >= 2 else None

    @property
    def takeoff_spread_deg(self) -> float | None:
        values = [
            point.takeoff_deg
            for point in self.valid_points
            if point.takeoff_deg is not None and math.isfinite(point.takeoff_deg)
        ]
        return max(values) - min(values) if len(values) >= 2 else None


def _delta(first: ConvergencePoint, second: ConvergencePoint) -> ConvergenceDelta:
    resistance = _relative_change(first.resistance_ohm, second.resistance_ohm)
    reactance = abs(second.reactance_ohm - first.reactance_ohm) / max(
        abs(first.impedance_magnitude_ohm),
        abs(second.impedance_magnitude_ohm),
        1e-12,
    )
    magnitude = _relative_change(
        first.impedance_magnitude_ohm,
        second.impedance_magnitude_ohm,
    )
    gain = (
        abs(second.max_gain_db - first.max_gain_db)
        if first.max_gain_db is not None and second.max_gain_db is not None
        else None
    )
    takeoff = (
        abs(second.takeoff_deg - first.takeoff_deg)
        if first.takeoff_deg is not None and second.takeoff_deg is not None
        else None
    )
    return ConvergenceDelta(
        resistance_fraction=resistance,
        reactance_fraction=reactance,
        magnitude_fraction=magnitude,
        swr_absolute=abs(second.swr - first.swr),
        gain_db=gain,
        takeoff_deg=takeoff,
    )


def _relative_change(first: float, second: float) -> float:
    return abs(second - first) / max(abs(first), abs(second), 1e-12)


def _spread_fraction(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    return 0.0 if mean == 0.0 else (max(values) - min(values)) / abs(mean)


def _within(
    delta: ConvergenceDelta,
    thresholds: ConvergenceThresholds,
    factor: float,
) -> bool:
    checks = [
        delta.resistance_fraction <= thresholds.resistance_fraction * factor,
        delta.reactance_fraction <= thresholds.reactance_fraction * factor,
        delta.magnitude_fraction <= thresholds.magnitude_fraction * factor,
        delta.swr_absolute <= thresholds.swr_absolute * factor,
    ]
    if delta.gain_db is not None:
        checks.append(delta.gain_db <= thresholds.gain_db * factor)
    if delta.takeoff_deg is not None:
        checks.append(delta.takeoff_deg <= thresholds.takeoff_deg * factor)
    return all(checks)


def convergence_csv(result: ConvergenceResult) -> str:
    """Return the convergence table as deterministic CSV text."""

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        (
            "density_lambda",
            "total_segments",
            "resistance_ohm",
            "reactance_ohm",
            "impedance_magnitude_ohm",
            "swr",
            "max_gain_db",
            "takeoff_deg",
            "verdict",
            "error",
            "wire_metrics",
        )
    )
    verdict = result.verdict.value
    for point in result.points:
        metrics = ";".join(
            f"{metric.wire_id}:{metric.segments}:{metric.segment_to_radius_ratio:.3f}"
            for metric in point.wire_metrics
        )
        writer.writerow(
            (
                f"{point.density_wavelengths:g}",
                point.total_segments,
                f"{point.resistance_ohm:.6f}",
                f"{point.reactance_ohm:.6f}",
                f"{point.impedance_magnitude_ohm:.6f}",
                f"{point.swr:.6f}",
                "" if point.max_gain_db is None else f"{point.max_gain_db:.6f}",
                "" if point.takeoff_deg is None else f"{point.takeoff_deg:.6f}",
                verdict,
                point.error or "",
                metrics,
            )
        )
    return buffer.getvalue()
