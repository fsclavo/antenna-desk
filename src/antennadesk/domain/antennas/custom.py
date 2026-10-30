# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""User-defined straight-wire antenna parameters."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_positive
from ..common.validation import Diagnostic, Severity
from ..environment.environment import Environment
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .feed import FeedPoint
from .load import LumpedLoad
from .wire import Wire

ANTENNA_TYPE_CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class CustomAntennaParameters:
    """A user-defined set of straight wires, one feed, and optional loads."""

    frequency_hz: float
    wires: tuple[Wire, ...]
    feed: FeedPoint
    ground: GroundModel = FREE_SPACE
    loads: tuple[LumpedLoad, ...] = ()

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        object.__setattr__(self, "wires", tuple(self.wires))
        object.__setattr__(self, "loads", tuple(self.loads))

    def to_antenna(self, *, name: str = "Custom antenna") -> AntennaModel:
        return AntennaModel(
            name=name,
            design_frequency_hz=self.frequency_hz,
            wires=self.wires,
            feed=self.feed,
            environment=Environment(ground=self.ground),
            loads=self.loads,
        )


def _segment_distance(first: Wire, second: Wire) -> float:
    """Shortest distance between two 3-D segments."""

    p1 = (first.start.x_m, first.start.y_m, first.start.z_m)
    q1 = (first.end.x_m, first.end.y_m, first.end.z_m)
    p2 = (second.start.x_m, second.start.y_m, second.start.z_m)
    q2 = (second.end.x_m, second.end.y_m, second.end.z_m)

    def sub(
        a: tuple[float, float, float], b: tuple[float, float, float]
    ) -> tuple[float, float, float]:
        return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

    def dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    d1 = sub(q1, p1)
    d2 = sub(q2, p2)
    r = sub(p1, p2)
    a = dot(d1, d1)
    e = dot(d2, d2)
    f = dot(d2, r)
    if a <= 1e-18 and e <= 1e-18:
        return math.dist(p1, p2)
    if a <= 1e-18:
        s = 0.0
        t = min(max(f / e, 0.0), 1.0)
    else:
        c = dot(d1, r)
        if e <= 1e-18:
            t = 0.0
            s = min(max(-c / a, 0.0), 1.0)
        else:
            b = dot(d1, d2)
            denominator = a * e - b * b
            s = min(max((b * f - c * e) / denominator, 0.0), 1.0) if denominator != 0.0 else 0.0
            t = (b * s + f) / e
            if t < 0.0:
                t = 0.0
                s = min(max(-c / a, 0.0), 1.0)
            elif t > 1.0:
                t = 1.0
                s = min(max((b - c) / a, 0.0), 1.0)
    closest_first = (p1[0] + d1[0] * s, p1[1] + d1[1] * s, p1[2] + d1[2] * s)
    closest_second = (p2[0] + d2[0] * t, p2[1] + d2[1] * t, p2[2] + d2[2] * t)
    return math.dist(closest_first, closest_second)


def _collinear_overlap(first: Wire, second: Wire) -> bool:
    d1 = (
        first.end.x_m - first.start.x_m,
        first.end.y_m - first.start.y_m,
        first.end.z_m - first.start.z_m,
    )
    d2 = (
        second.end.x_m - second.start.x_m,
        second.end.y_m - second.start.y_m,
        second.end.z_m - second.start.z_m,
    )
    cross = (
        d1[1] * d2[2] - d1[2] * d2[1],
        d1[2] * d2[0] - d1[0] * d2[2],
        d1[0] * d2[1] - d1[1] * d2[0],
    )
    if math.sqrt(sum(value * value for value in cross)) > 1e-9:
        return False
    length_sq = sum(value * value for value in d1)
    if length_sq <= 1e-18:
        return False
    u = (first.start.x_m, first.start.y_m, first.start.z_m)
    v = (second.start.x_m, second.start.y_m, second.start.z_m)
    w = (u[0] - v[0], u[1] - v[1], u[2] - v[2])
    projection = (w[0] * d1[0] + w[1] * d1[1] + w[2] * d1[2]) / length_sq
    closest = (u[0] - d1[0] * projection, u[1] - d1[1] * projection, u[2] - d1[2] * projection)
    if math.dist(closest, v) > 1e-6:
        return False
    unit = (
        d1[0] / math.sqrt(length_sq),
        d1[1] / math.sqrt(length_sq),
        d1[2] / math.sqrt(length_sq),
    )
    first_interval = (0.0, math.sqrt(length_sq))
    second_start = (v[0] - u[0]) * unit[0] + (v[1] - u[1]) * unit[1] + (v[2] - u[2]) * unit[2]
    second_end = second_start + math.sqrt(sum(value * value for value in d2))
    return (
        min(first_interval[1], max(second_start, second_end))
        - max(first_interval[0], min(second_start, second_end))
        > 1e-6
    )


def geometry_warnings(parameters: CustomAntennaParameters) -> tuple[Diagnostic, ...]:
    warnings: list[Diagnostic] = []
    wires = parameters.wires
    for wire in wires:
        if wire.length_m < 0.01:
            warnings.append(
                Diagnostic(
                    code="custom.wire.short",
                    severity=Severity.WARNING,
                    message=f"wire {wire.id} is shorter than 1 cm",
                    field="wires",
                )
            )
    for index, first in enumerate(wires):
        for second in wires[index + 1 :]:
            if _collinear_overlap(first, second):
                warnings.append(
                    Diagnostic(
                        code="custom.wires.overlap",
                        severity=Severity.WARNING,
                        message=f"wires {first.id} and {second.id} overlap",
                        field="wires",
                    )
                )
            elif _segment_distance(first, second) < 1e-6:
                warnings.append(
                    Diagnostic(
                        code="custom.wires.cross",
                        severity=Severity.WARNING,
                        message=f"wires {first.id} and {second.id} cross",
                        field="wires",
                    )
                )
    return tuple(warnings)
