# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Orthographic view selection for the geometry sketch."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ...domain.antennas.antenna import AntennaModel
from ...domain.antennas.geometry import Point3D


class GeometryViewMode(StrEnum):
    """A projected view or the user-facing construction view.

    ``CONSTRUCTION`` is the only 2D mode exposed by the main window.  It
    resolves to the projection that best shows the antenna's construction
    shape.  ``ELEVATION`` and ``PLAN`` remain available for the scene builder,
    exports, and tests.
    """

    CONSTRUCTION = "construction"
    ELEVATION = "elevation"
    PLAN = "plan"
    THREE_D = "3d"


@dataclass(frozen=True, slots=True)
class Projection:
    """An orthographic basis and its plane normal."""

    origin: tuple[float, float, float]
    u: tuple[float, float, float]
    v: tuple[float, float, float]
    normal: tuple[float, float, float]
    vertical: bool
    name: str

    def project(self, point: Point3D) -> tuple[float, float]:
        dx = point.x_m - self.origin[0]
        dy = point.y_m - self.origin[1]
        dz = point.z_m - self.origin[2]
        return (
            dx * self.u[0] + dy * self.u[1] + dz * self.u[2],
            dx * self.v[0] + dy * self.v[1] + dz * self.v[2],
        )


def _normalize(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    length = math.sqrt(sum(value * value for value in vector))
    if length <= 1e-15:
        return (0.0, 0.0, 1.0)
    return (vector[0] / length, vector[1] / length, vector[2] / length)


def _cross(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def _model_points(model: AntennaModel) -> tuple[Point3D, ...]:
    points: list[Point3D] = []
    for wire in model.wires:
        points.append(wire.start)
        points.append(wire.end)
    return tuple(points)


def _centroid(points: tuple[Point3D, ...]) -> tuple[float, float, float]:
    if not points:
        return (0.0, 0.0, 0.0)
    return (
        sum(point.x_m for point in points) / len(points),
        sum(point.y_m for point in points) / len(points),
        sum(point.z_m for point in points) / len(points),
    )


def _plane_normal(points: tuple[Point3D, ...]) -> tuple[float, float, float]:
    """Return a normal inferred from the first two non-parallel wire directions."""

    directions: list[tuple[float, float, float]] = []
    for index, first in enumerate(points):
        for second in points[index + 1 :]:
            direction = (
                second.x_m - first.x_m,
                second.y_m - first.y_m,
                second.z_m - first.z_m,
            )
            length = math.sqrt(sum(value * value for value in direction))
            if length > 1e-9:
                directions.append(
                    (direction[0] / length, direction[1] / length, direction[2] / length)
                )
            if len(directions) >= 8:
                break
        if len(directions) >= 8:
            break
    for index, first_direction in enumerate(directions):
        for second_direction in directions[index + 1 :]:
            normal = _cross(first_direction, second_direction)
            if math.sqrt(sum(value * value for value in normal)) > 1e-6:
                return _normalize(normal)
    first_direction = directions[0] if directions else (1.0, 0.0, 0.0)
    normal = _cross(first_direction, (0.0, 0.0, 1.0))
    if math.sqrt(sum(value * value for value in normal)) <= 1e-6:
        return (0.0, 1.0, 0.0)
    return _normalize(normal)


def _planarity(
    points: tuple[Point3D, ...], normal: tuple[float, float, float]
) -> tuple[bool, float]:
    if not points:
        return True, 0.0
    origin = _centroid(points)
    distances = [
        abs(
            (point.x_m - origin[0]) * normal[0]
            + (point.y_m - origin[1]) * normal[1]
            + (point.z_m - origin[2]) * normal[2]
        )
        for point in points
    ]
    xs = [point.x_m for point in points]
    ys = [point.y_m for point in points]
    zs = [point.z_m for point in points]
    span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 1.0)
    return max(distances) <= span * 1e-4, max(distances)


def _principal_horizontal(points: tuple[Point3D, ...]) -> tuple[float, float, float]:
    xs = [point.x_m for point in points]
    ys = [point.y_m for point in points]
    if not points:
        return (1.0, 0.0, 0.0)
    if max(xs) - min(xs) >= max(ys) - min(ys):
        return (1.0, 0.0, 0.0)
    return (0.0, 1.0, 0.0)


def plan_projection(points: tuple[Point3D, ...]) -> Projection:
    """Return a true top view: world X to the right, world Y upward."""

    origin = _centroid(points)
    return Projection(
        origin=origin,
        u=(1.0, 0.0, 0.0),
        v=(0.0, 1.0, 0.0),
        normal=(0.0, 0.0, 1.0),
        vertical=False,
        name="plan",
    )


def front_projection(points: tuple[Point3D, ...]) -> Projection:
    """Return a front view.

    For a vertical planar antenna (a loop, for example), the view looks normal
    to the plane, so the polygon is shown with its true shape.  For horizontal
    or non-planar geometry it falls back to the principal horizontal axis and
    Z.
    """

    normal = _plane_normal(points)
    is_planar, _residual = _planarity(points, normal)
    origin = _centroid(points)
    vertical_normal = abs(normal[2]) > 0.9
    if is_planar and not vertical_normal:
        u = _normalize(_cross(normal, (0.0, 0.0, 1.0)))
        return Projection(
            origin=origin,
            u=u,
            v=(0.0, 0.0, 1.0),
            normal=normal,
            vertical=True,
            name="front",
        )
    return Projection(
        origin=origin,
        u=_principal_horizontal(points),
        v=(0.0, 0.0, 1.0),
        normal=normal,
        vertical=True,
        name="front",
    )


def is_planar(model: AntennaModel) -> bool:
    points = _model_points(model)
    normal = _plane_normal(points)
    planar, _residual = _planarity(points, normal)
    return planar


def recommended_view(model: AntennaModel) -> GeometryViewMode:
    """Choose the projection that shows the most useful shape by default."""

    if len(model.wires) <= 1:
        return GeometryViewMode.ELEVATION
    points = _model_points(model)
    normal = _plane_normal(points)
    planar, _residual = _planarity(points, normal)
    if not planar:
        return GeometryViewMode.ELEVATION
    if abs(normal[2]) > 0.85:
        return GeometryViewMode.PLAN
    return GeometryViewMode.ELEVATION


# Families whose construction layout is the boom plan even though the model is
# not a single horizontal plane.  A cubical quad is the first case: its loops
# lie in parallel vertical planes, so a generic front view is edge-on.
_CONSTRUCTION_PLAN_TYPES = frozenset({"quad_beam"})


def construction_view(
    model: AntennaModel,
    *,
    antenna_type: str | None = None,
) -> GeometryViewMode:
    """Return the projection used by the single user-facing construction view."""

    if antenna_type in _CONSTRUCTION_PLAN_TYPES:
        return GeometryViewMode.PLAN
    return recommended_view(model)
