# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""DXF export for the projected construction sketch."""

from __future__ import annotations

import math
from pathlib import Path

import ezdxf

from .scene import Dimension, GeometryScene, ScenePoint

LAYER_WIRES = "ANTENNA_WIRES"
LAYER_MARKERS = "ANTENNA_MARKERS"
LAYER_DIMENSIONS = "ANTENNA_DIMENSIONS"
LAYER_TEXT = "ANTENNA_TEXT"


def _span(scene: GeometryScene) -> float:
    bounds = scene.bounds()
    if bounds is None:
        return 1.0
    first, second = bounds
    return max(second.x_m - first.x_m, second.y_m - first.y_m, 1.0)


def _scene_center(scene: GeometryScene) -> ScenePoint:
    bounds = scene.bounds()
    if bounds is None:
        return ScenePoint(0.0, 0.0)
    first, second = bounds
    return first.midpoint(second)


def _linear_base(dimension: Dimension, scene: GeometryScene, offset: float) -> tuple[float, float]:
    center = _scene_center(scene)
    midpoint = dimension.start.midpoint(dimension.end)
    dx = dimension.end.x_m - dimension.start.x_m
    dy = dimension.end.y_m - dimension.start.y_m
    length = math.hypot(dx, dy)
    if length <= 1e-12:
        return (midpoint.x_m, midpoint.y_m)
    normal = (-dy / length, dx / length)
    if dimension.side in {"left", "right", "above", "below"}:
        side = dimension.side
        if side == "left":
            normal = (-1.0, 0.0)
        elif side == "right":
            normal = (1.0, 0.0)
        elif side == "above":
            normal = (0.0, 1.0)
        else:
            normal = (0.0, -1.0)
    else:
        away = (
            midpoint.x_m - center.x_m,
            midpoint.y_m - center.y_m,
        )
        if normal[0] * away[0] + normal[1] * away[1] < 0.0:
            normal = (-normal[0], -normal[1])
    return (
        midpoint.x_m + normal[0] * offset,
        midpoint.y_m + normal[1] * offset,
    )


def _angular_base(
    center: ScenePoint,
    first: ScenePoint,
    second: ScenePoint,
    radius: float,
) -> tuple[float, float]:
    first_angle = math.atan2(first.y_m - center.y_m, first.x_m - center.x_m)
    second_angle = math.atan2(second.y_m - center.y_m, second.x_m - center.x_m)
    span = (second_angle - first_angle) % (2.0 * math.pi)
    if span > math.pi:
        first_angle, second_angle = second_angle, first_angle
        span = 2.0 * math.pi - span
    middle = first_angle + span / 2.0
    return (
        center.x_m + math.cos(middle) * radius,
        center.y_m + math.sin(middle) * radius,
    )


def write_dxf(scene: GeometryScene, path: Path, title: str) -> None:
    """Write the current projected scene to a layered DXF file."""

    span = _span(scene)
    text_height = max(span * 0.02, 0.03)
    offset = max(span * 0.05, 0.05)

    document = ezdxf.new("R2010", setup=True)
    document.header["$INSUNITS"] = 6
    document.header["$MEASUREMENT"] = 1
    for name, color in (
        (LAYER_WIRES, 5),
        (LAYER_MARKERS, 1),
        (LAYER_DIMENSIONS, 3),
        (LAYER_TEXT, 7),
    ):
        if name not in document.layers:
            document.layers.add(name, color=color)

    modelspace = document.modelspace()
    for polyline in scene.polylines:
        points = [(point.x_m, point.y_m) for point in polyline.points]
        modelspace.add_lwpolyline(
            points,
            close=False,
            dxfattribs={"layer": LAYER_WIRES, "lineweight": 30},
        )
    for marker in scene.markers:
        modelspace.add_circle(
            center=(marker.point.x_m, marker.point.y_m),
            radius=max(span * 0.004, 0.01),
            dxfattribs={"layer": LAYER_MARKERS},
        )
        if marker.label:
            modelspace.add_text(
                marker.label,
                height=text_height * 0.8,
                dxfattribs={
                    "layer": LAYER_TEXT,
                    "insert": (marker.point.x_m, marker.point.y_m + text_height),
                },
            )

    dimension_style = {
        "dimtxt": text_height,
        "dimasz": text_height * 0.55,
        "dimexo": text_height * 0.2,
        "dimexe": text_height * 0.3,
    }
    for dimension in scene.dimensions:
        dx = dimension.end.x_m - dimension.start.x_m
        dy = dimension.end.y_m - dimension.start.y_m
        angle = math.degrees(math.atan2(dy, dx))
        try:
            modelspace.add_linear_dim(
                base=_linear_base(dimension, scene, offset),
                p1=(dimension.start.x_m, dimension.start.y_m),
                p2=(dimension.end.x_m, dimension.end.y_m),
                angle=angle,
                text=dimension.text,
                override=dimension_style,
                dxfattribs={"layer": LAYER_DIMENSIONS},
            ).render()
        except Exception:
            modelspace.add_text(
                dimension.text,
                height=text_height,
                dxfattribs={
                    "layer": LAYER_TEXT,
                    "insert": (
                        dimension.start.midpoint(dimension.end).x_m,
                        dimension.start.midpoint(dimension.end).y_m,
                    ),
                },
            )
    for dimension in scene.angular_dimensions:
        base = _angular_base(
            dimension.center,
            dimension.first,
            dimension.second,
            max(span * 0.12, 0.1),
        )
        try:
            modelspace.add_angular_dim_3p(
                base=base,
                center=(dimension.center.x_m, dimension.center.y_m),
                p1=(dimension.first.x_m, dimension.first.y_m),
                p2=(dimension.second.x_m, dimension.second.y_m),
                text=dimension.text,
                override=dimension_style,
                dxfattribs={"layer": LAYER_DIMENSIONS},
            ).render()
        except Exception:
            modelspace.add_text(
                dimension.text,
                height=text_height,
                dxfattribs={
                    "layer": LAYER_TEXT,
                    "insert": (
                        dimension.center.x_m,
                        dimension.center.y_m + text_height,
                    ),
                },
            )

    bounds = scene.bounds()
    if bounds is not None:
        first, second = bounds
        modelspace.add_text(
            title,
            height=text_height * 1.1,
            dxfattribs={
                "layer": LAYER_TEXT,
                "insert": (first.x_m, second.y_m + text_height * 2.0),
            },
        )
    document.saveas(path)
