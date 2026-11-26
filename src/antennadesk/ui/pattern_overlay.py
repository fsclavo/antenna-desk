# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Presentation snapshot for the 3D antenna wireframe overlay."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..domain.antennas.antenna import AntennaModel

OVERLAY_EXTENT_FRACTION = 0.35
AUTO_FULL_WIRE_LIMIT = 96


class OverlayMode(StrEnum):
    AUTO = "auto"
    FULL = "full"
    OUTLINE = "outline"


@dataclass(frozen=True, slots=True)
class OverlayWire:
    start: tuple[float, float, float]
    end: tuple[float, float, float]
    support: bool = False


@dataclass(frozen=True, slots=True)
class AntennaOverlay:
    wires: tuple[OverlayWire, ...]
    feed: tuple[float, float, float]

    @property
    def wire_count(self) -> int:
        return len(self.wires)


def _support_wire(wire_id: str) -> bool:
    return wire_id == "mast" or wire_id.startswith("guy-")


def overlay_from_model(model: AntennaModel | None) -> AntennaOverlay | None:
    """Return a feed-centered presentation snapshot, or None without a model."""

    if model is None:
        return None
    feed_wire = model.feed_wire
    feed = feed_wire.point_at(model.feed.offset_m)
    wires = tuple(
        OverlayWire(
            start=(wire.start.x_m, wire.start.y_m, wire.start.z_m),
            end=(wire.end.x_m, wire.end.y_m, wire.end.z_m),
            support=_support_wire(wire.id),
        )
        for wire in model.wires
    )
    if not wires:
        return None
    return AntennaOverlay(
        wires=wires,
        feed=(feed.x_m, feed.y_m, feed.z_m),
    )


def overlay_scale(overlay: AntennaOverlay) -> float:
    """Return the uniform scale that puts the largest extent at 35 % radius."""

    feed = overlay.feed
    maximum = 0.0
    for wire in overlay.wires:
        for point in (wire.start, wire.end):
            maximum = max(
                maximum,
                ((point[0] - feed[0]) ** 2 + (point[1] - feed[1]) ** 2 + (point[2] - feed[2]) ** 2)
                ** 0.5,
            )
    return OVERLAY_EXTENT_FRACTION / max(maximum, 1e-9)


def convex_hull(points: tuple[tuple[float, float], ...]) -> tuple[tuple[float, float], ...]:
    """Return the 2D convex hull in counter-clockwise order."""

    unique = sorted(set(points))
    if len(unique) <= 1:
        return tuple(unique)

    def cross(
        origin: tuple[float, float],
        first: tuple[float, float],
        second: tuple[float, float],
    ) -> float:
        return (first[0] - origin[0]) * (second[1] - origin[1]) - (first[1] - origin[1]) * (
            second[0] - origin[0]
        )

    lower: list[tuple[float, float]] = []
    for point in unique:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0.0:
            lower.pop()
        lower.append(point)
    upper: list[tuple[float, float]] = []
    for point in reversed(unique):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0.0:
            upper.pop()
        upper.append(point)
    return tuple(lower[:-1] + upper[:-1])
