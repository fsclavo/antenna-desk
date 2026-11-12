# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded 1D/2D parameter sweeps over family optimizer variables.

The sweep is a what-if tool: it evaluates the existing solver at a bounded set
of variable combinations and reports scalar metrics at one target frequency. It
does not optimize, rank physical antennas, or persist the sweep.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from itertools import pairwise

from ..optimization.variables import OptimizationVariable, VariableKind

MAX_SWEEP_POINTS = 400


class SweepMetric(StrEnum):
    SWR = "swr"
    RESISTANCE = "resistance"
    REACTANCE = "reactance"
    IMPEDANCE_MAGNITUDE = "impedance_magnitude"


@dataclass(frozen=True, slots=True)
class SweepAxis:
    """One ordered axis of variable values."""

    name: str
    label_key: str
    unit: str
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("sweep axis name must not be empty")
        if not self.label_key.strip():
            raise ValueError("sweep axis label key must not be empty")
        if not self.values:
            raise ValueError("sweep axis requires at least one value")
        values = tuple(float(value) for value in self.values)
        if any(not math.isfinite(value) for value in values):
            raise ValueError("sweep axis values must be finite")
        if any(second <= first for first, second in pairwise(values)):
            raise ValueError("sweep axis values must be strictly increasing")
        object.__setattr__(self, "values", values)

    @property
    def count(self) -> int:
        return len(self.values)


@dataclass(frozen=True, slots=True)
class SweepPlan:
    x_axis: SweepAxis
    y_axis: SweepAxis | None
    metric: SweepMetric
    target_frequency_hz: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.target_frequency_hz) or self.target_frequency_hz <= 0.0:
            raise ValueError("target_frequency_hz must be positive and finite")
        object.__setattr__(self, "metric", SweepMetric(self.metric))
        if self.y_axis is not None and self.y_axis.name == self.x_axis.name:
            raise ValueError("sweep axes must use different variables")
        if self.point_count > MAX_SWEEP_POINTS:
            raise ValueError(f"a sweep may contain at most {MAX_SWEEP_POINTS} points")

    @property
    def point_count(self) -> int:
        return self.x_axis.count * (self.y_axis.count if self.y_axis is not None else 1)

    @property
    def is_two_dimensional(self) -> bool:
        return self.y_axis is not None


@dataclass(frozen=True, slots=True)
class SweepPoint:
    x_value: float
    y_value: float | None = None
    swr: float | None = None
    resistance_ohm: float | None = None
    reactance_ohm: float | None = None
    impedance_magnitude_ohm: float | None = None
    error: str = ""

    @property
    def valid(self) -> bool:
        return not self.error and self.swr is not None

    def metric(self, metric: SweepMetric) -> float | None:
        if metric is SweepMetric.SWR:
            return self.swr
        if metric is SweepMetric.RESISTANCE:
            return self.resistance_ohm
        if metric is SweepMetric.REACTANCE:
            return self.reactance_ohm
        return self.impedance_magnitude_ohm


@dataclass(frozen=True, slots=True)
class ParameterSweepResult:
    plan: SweepPlan
    points: tuple[SweepPoint, ...]
    cancelled: bool = False
    message: str = ""

    @property
    def completed_count(self) -> int:
        return len(self.points)

    @property
    def valid_count(self) -> int:
        return sum(1 for point in self.points if point.valid)

    @property
    def best_swr_point(self) -> SweepPoint | None:
        valid = [
            point
            for point in self.points
            if point.valid and point.swr is not None and math.isfinite(point.swr)
        ]
        if not valid:
            return None
        return min(
            valid,
            key=lambda point: (
                point.swr if point.swr is not None else math.inf,
                point.x_value,
            ),
        )


def axis_values(
    variable: OptimizationVariable,
    minimum: float,
    maximum: float,
    count: int,
) -> tuple[float, ...]:
    """Return a bounded, ordered axis for one optimizer variable."""

    if count < 2:
        raise ValueError("axis count must be at least 2")
    if not math.isfinite(minimum) or not math.isfinite(maximum):
        raise ValueError("axis bounds must be finite")
    if maximum < minimum:
        raise ValueError("axis maximum must be greater than or equal to minimum")
    minimum = max(minimum, variable.minimum)
    maximum = min(maximum, variable.maximum)
    if maximum < minimum:
        raise ValueError("axis bounds are outside the variable limits")
    if variable.kind is VariableKind.CHOICE:
        values = tuple(choice for choice in variable.choices if minimum <= choice <= maximum)
        if not values:
            raise ValueError("axis range contains no discrete choices")
        return values
    if math.isclose(minimum, maximum, rel_tol=0.0, abs_tol=1e-15):
        return (variable.clamp(minimum),)
    if variable.kind is VariableKind.INTEGER:
        raw = [minimum + (maximum - minimum) * index / (count - 1) for index in range(count)]
        values = tuple(dict.fromkeys(variable.clamp(round(value)) for value in raw))
        if not values:
            raise ValueError("axis range contains no integer values")
        return values
    return tuple(
        variable.clamp(minimum + (maximum - minimum) * index / (count - 1))
        for index in range(count)
    )
