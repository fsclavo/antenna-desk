# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Coordinates and primitives for the geometry presentation layer.

The scene is expressed in metres in a two-dimensional projection.  It contains
no Qt objects, so the projection and annotation model can be tested without a
GUI.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ScenePoint:
    """A point in the selected orthographic projection, in metres."""

    x_m: float
    y_m: float

    def distance_to(self, other: ScenePoint) -> float:
        return math.hypot(self.x_m - other.x_m, self.y_m - other.y_m)

    def midpoint(self, other: ScenePoint) -> ScenePoint:
        return ScenePoint((self.x_m + other.x_m) / 2.0, (self.y_m + other.y_m) / 2.0)

    def offset(self, dx: float, dy: float) -> ScenePoint:
        return ScenePoint(self.x_m + dx, self.y_m + dy)


@dataclass(frozen=True, slots=True)
class ScenePolyline:
    """A projected conductor or construction line."""

    points: tuple[ScenePoint, ...]
    role: str = "wire"
    style: str = "solid"
    width: float = 2.5

    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise ValueError("a polyline needs at least two points")


@dataclass(frozen=True, slots=True)
class SceneMarker:
    """A projected feature marker (feed point, load, or endpoint)."""

    point: ScenePoint
    kind: str
    label: str | None = None
    priority: int = 50


@dataclass(frozen=True, slots=True)
class Dimension:
    """A linear dimension request in scene coordinates.

    ``side`` is a hint for the layout engine: ``auto``, ``left``, ``right``,
    ``above`` or ``below``.
    """

    start: ScenePoint
    end: ScenePoint
    text: str
    side: str = "auto"
    priority: int = 50
    label: str | None = None


@dataclass(frozen=True, slots=True)
class AngularDimension:
    """An angle annotation centred on ``center`` between two directions."""

    center: ScenePoint
    first: ScenePoint
    second: ScenePoint
    text: str
    radius_px: float = 44.0
    priority: int = 60


@dataclass(frozen=True, slots=True)
class SceneInset:
    """A detail or secondary view shown in a corner of the main sketch."""

    label: str
    polylines: tuple[ScenePolyline, ...] = ()
    markers: tuple[SceneMarker, ...] = ()
    dimensions: tuple[Dimension, ...] = ()
    show_ground: bool = False


@dataclass(frozen=True, slots=True)
class GeometryScene:
    """A complete, renderer-neutral construction sketch."""

    polylines: tuple[ScenePolyline, ...] = ()
    markers: tuple[SceneMarker, ...] = ()
    dimensions: tuple[Dimension, ...] = ()
    angular_dimensions: tuple[AngularDimension, ...] = ()
    summary: str = ""
    notes: tuple[str, ...] = ()
    show_ground: bool = False
    ground_y_m: float | None = None
    is_plan: bool = False
    azimuth_deg: float | None = None
    insets: tuple[SceneInset, ...] = ()
    height_exaggeration: float = 1.0
    projection_name: str = ""
    metadata: dict[str, object] = field(default_factory=dict)

    def points(self) -> tuple[ScenePoint, ...]:
        points: list[ScenePoint] = []
        for polyline in self.polylines:
            points.extend(polyline.points)
        points.extend(marker.point for marker in self.markers)
        return tuple(points)

    def bounds(self) -> tuple[ScenePoint, ScenePoint] | None:
        points = self.points()
        if not points:
            return None
        min_x = min(point.x_m for point in points)
        max_x = max(point.x_m for point in points)
        min_y = min(point.y_m for point in points)
        max_y = max(point.y_m for point in points)
        if self.show_ground and self.ground_y_m is not None:
            min_y = min(min_y, self.ground_y_m)
        return ScenePoint(min_x, min_y), ScenePoint(max_x, max_y)

    def with_summary(self, summary: str) -> GeometryScene:
        return GeometryScene(
            polylines=self.polylines,
            markers=self.markers,
            dimensions=self.dimensions,
            angular_dimensions=self.angular_dimensions,
            summary=summary,
            notes=self.notes,
            show_ground=self.show_ground,
            ground_y_m=self.ground_y_m,
            is_plan=self.is_plan,
            azimuth_deg=self.azimuth_deg,
            insets=self.insets,
            height_exaggeration=self.height_exaggeration,
            projection_name=self.projection_name,
            metadata=self.metadata,
        )
