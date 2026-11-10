# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Collision-aware screen layout for construction dimensions."""

from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QFontMetricsF

from .scene import AngularDimension, Dimension, GeometryScene, ScenePoint


@dataclass(frozen=True, slots=True)
class SceneTransform:
    """Map scene metres to screen pixels with a uniform scale."""

    center_scene: ScenePoint
    center_screen: QPointF
    scale: float
    pan: QPointF

    def to_screen(self, point: ScenePoint) -> QPointF:
        return QPointF(
            self.center_screen.x()
            + (point.x_m - self.center_scene.x_m) * self.scale
            + self.pan.x(),
            self.center_screen.y()
            - (point.y_m - self.center_scene.y_m) * self.scale
            + self.pan.y(),
        )


@dataclass(frozen=True, slots=True)
class PlacedAngularDimension:
    dimension: AngularDimension
    center: QPointF
    arc_rect: QRectF
    start_angle_deg: float
    span_angle_deg: float
    extension_lines: tuple[tuple[QPointF, QPointF], ...]
    text_center: QPointF
    text_rect: QRectF


@dataclass(frozen=True, slots=True)
class PlacedDimension:
    dimension: Dimension
    line_start: QPointF
    line_end: QPointF
    extension_lines: tuple[tuple[QPointF, QPointF], ...]
    text_center: QPointF
    text_rect: QRectF
    leader_only: bool
    text_angle: float = 0.0


_OFFSETS = (18.0, 30.0, 44.0, 60.0, 78.0, 98.0, 120.0, 145.0, 175.0, 210.0)


def _inflate(rect: QRectF, amount: float = 2.0) -> QRectF:
    return rect.adjusted(-amount, -amount, amount, amount)


def _line_rect(start: QPointF, end: QPointF) -> QRectF:
    return QRectF(start, end).normalized().adjusted(-1.0, -1.0, 1.0, 1.0)


def _text_rect(center: QPointF, text: str, metrics: QFontMetricsF) -> QRectF:
    bounds = metrics.boundingRect(text)
    width = bounds.width() + 8.0
    height = bounds.height() + 4.0
    return QRectF(center.x() - width / 2.0, center.y() - height / 2.0, width, height)


def dimension_text(dimension: Dimension) -> str:
    """Return the label and value shown for a dimension."""

    if dimension.label:
        return f"{dimension.label} {dimension.text}"
    return dimension.text


def _candidate_directions(
    dimension: Dimension,
    start: QPointF,
    end: QPointF,
    geometry_center: QPointF,
) -> tuple[QPointF, ...]:
    side = dimension.side
    if side == "left":
        return (QPointF(-1.0, 0.0),)
    if side == "right":
        return (QPointF(1.0, 0.0),)
    if side == "above":
        return (QPointF(0.0, -1.0),)
    if side == "below":
        return (QPointF(0.0, 1.0),)

    dx = end.x() - start.x()
    dy = end.y() - start.y()
    midpoint = QPointF((start.x() + end.x()) / 2.0, (start.y() + end.y()) / 2.0)
    if abs(dx) >= abs(dy):
        preferred = QPointF(0.0, -1.0 if midpoint.y() <= geometry_center.y() else 1.0)
    else:
        preferred = QPointF(-1.0 if midpoint.x() <= geometry_center.x() else 1.0, 0.0)
    return (preferred, QPointF(-preferred.x(), -preferred.y()))


def layout_dimensions(
    scene: GeometryScene,
    transform: SceneTransform,
    safe_rect: QRectF,
    geometry_rect: QRectF,
    reserved: tuple[QRectF, ...],
    metrics: QFontMetricsF,
    *,
    offset_scale: float = 1.0,
) -> tuple[PlacedDimension, ...]:
    """Place scene dimensions in screen space, avoiding overlaps when possible."""

    placed: list[PlacedDimension] = []
    label_obstacles = [_inflate(rect, 1.0) for rect in reserved]
    line_obstacles = [_inflate(rect, 1.0) for rect in reserved]
    placed_label_obstacles: list[QRectF] = []
    geometry_obstacle = _inflate(geometry_rect, 2.0)
    offsets = tuple(value * offset_scale for value in _OFFSETS)

    for dimension in sorted(scene.dimensions, key=lambda item: item.priority, reverse=True):
        text = dimension_text(dimension)
        if not text:
            continue
        start = transform.to_screen(dimension.start)
        end = transform.to_screen(dimension.end)
        geometry_center = geometry_rect.center()
        best: tuple[int, PlacedDimension] | None = None
        for direction in _candidate_directions(dimension, start, end, geometry_center):
            for offset in offsets:
                line_start = QPointF(
                    start.x() + direction.x() * offset,
                    start.y() + direction.y() * offset,
                )
                line_end = QPointF(
                    end.x() + direction.x() * offset,
                    end.y() + direction.y() * offset,
                )
                leader_only = (
                    math.hypot(
                        line_end.x() - line_start.x(),
                        line_end.y() - line_start.y(),
                    )
                    < 14.0
                )
                label_center = QPointF(
                    (line_start.x() + line_end.x()) / 2.0 + direction.x() * 11.0,
                    (line_start.y() + line_end.y()) / 2.0 + direction.y() * 11.0,
                )
                text_rect = _text_rect(label_center, text, metrics)
                if not safe_rect.contains(text_rect):
                    continue
                # Overlapping labels are a hard failure: drop the dimension
                # instead of drawing unreadable text. Reserved areas remain
                # soft obstacles so the most important labels can still win.
                if any(text_rect.intersects(obstacle) for obstacle in placed_label_obstacles):
                    continue
                if leader_only:
                    line_rect = _line_rect(
                        QPointF((start.x() + end.x()) / 2.0, (start.y() + end.y()) / 2.0),
                        label_center,
                    )
                else:
                    line_rect = _line_rect(line_start, line_end)
                # The painter clips to safe_rect; keep the label inside but let
                # the dimension line run past the edge when the text still fits.
                if not safe_rect.intersects(line_rect):
                    continue

                score = 0
                for obstacle in label_obstacles:
                    if text_rect.intersects(obstacle):
                        score += 4
                for obstacle in line_obstacles:
                    if line_rect.intersects(obstacle):
                        score += 2
                if text_rect.intersects(geometry_obstacle):
                    score += 1
                if score == 0:
                    best = (
                        0,
                        PlacedDimension(
                            dimension=dimension,
                            line_start=line_start,
                            line_end=line_end,
                            extension_lines=(
                                (start, line_start),
                                (end, line_end),
                            ),
                            text_center=label_center,
                            text_rect=text_rect,
                            leader_only=leader_only,
                        ),
                    )
                    break
                if best is None or score < best[0]:
                    best = (
                        score,
                        PlacedDimension(
                            dimension=dimension,
                            line_start=line_start,
                            line_end=line_end,
                            extension_lines=(
                                (start, line_start),
                                (end, line_end),
                            ),
                            text_center=label_center,
                            text_rect=text_rect,
                            leader_only=leader_only,
                        ),
                    )
            if best is not None and best[0] == 0:
                break
        if best is None or (best[0] > 0 and dimension.priority < 60):
            continue
        placed.append(best[1])
        label_obstacles.append(_inflate(best[1].text_rect, 1.0))
        placed_label_obstacles.append(_inflate(best[1].text_rect, 1.0))
        line_obstacles.append(_inflate(_line_rect(best[1].line_start, best[1].line_end), 1.0))

    return tuple(placed)


def _screen_angle(center: QPointF, point: QPointF) -> float:
    return math.degrees(math.atan2(-(point.y() - center.y()), point.x() - center.x()))


def _arc_point(center: QPointF, radius: float, angle_deg: float) -> QPointF:
    angle = math.radians(angle_deg)
    return QPointF(
        center.x() + math.cos(angle) * radius,
        center.y() - math.sin(angle) * radius,
    )


def layout_angular_dimensions(
    scene: GeometryScene,
    transform: SceneTransform,
    safe_rect: QRectF,
    reserved: tuple[QRectF, ...],
    occupied_labels: tuple[QRectF, ...],
    metrics: QFontMetricsF,
    *,
    radius_scale: float = 1.0,
) -> tuple[PlacedAngularDimension, ...]:
    """Place angle arcs and labels in screen space."""

    placed: list[PlacedAngularDimension] = []
    label_obstacles = [_inflate(rect, 1.0) for rect in (*reserved, *occupied_labels)]
    line_obstacles = [_inflate(rect, 1.0) for rect in reserved]
    placed_label_obstacles = [_inflate(rect, 1.0) for rect in occupied_labels]
    radii = tuple(value * radius_scale for value in (32.0, 44.0, 58.0, 74.0, 92.0))

    for dimension in sorted(
        scene.angular_dimensions,
        key=lambda item: item.priority,
        reverse=True,
    ):
        center = transform.to_screen(dimension.center)
        first = transform.to_screen(dimension.first)
        second = transform.to_screen(dimension.second)
        angle_first = _screen_angle(center, first)
        angle_second = _screen_angle(center, second)
        span = (angle_second - angle_first) % 360.0
        if span > 180.0:
            angle_first, angle_second = angle_second, angle_first
            span = 360.0 - span
        text = dimension.text
        text_size = metrics.boundingRect(text)
        width = text_size.width() + 8.0
        height = text_size.height() + 4.0
        best: tuple[int, PlacedAngularDimension] | None = None

        for radius in (dimension.radius_px * radius_scale, *radii):
            arc_rect = QRectF(
                center.x() - radius,
                center.y() - radius,
                radius * 2.0,
                radius * 2.0,
            )
            mid_angle = angle_first + span / 2.0
            label_center = _arc_point(center, radius + 13.0, mid_angle)
            text_rect = QRectF(
                label_center.x() - width / 2.0,
                label_center.y() - height / 2.0,
                width,
                height,
            )
            if not safe_rect.contains(text_rect):
                continue
            if not safe_rect.intersects(arc_rect):
                continue
            if any(text_rect.intersects(obstacle) for obstacle in placed_label_obstacles):
                continue
            score = 0
            for obstacle in label_obstacles:
                if text_rect.intersects(obstacle):
                    score += 4
            for obstacle in line_obstacles:
                if arc_rect.intersects(obstacle):
                    score += 1
            if score == 0:
                best = (
                    0,
                    PlacedAngularDimension(
                        dimension=dimension,
                        center=center,
                        arc_rect=arc_rect,
                        start_angle_deg=angle_first,
                        span_angle_deg=span,
                        extension_lines=(
                            (center, _arc_point(center, radius, angle_first)),
                            (center, _arc_point(center, radius, angle_second)),
                        ),
                        text_center=label_center,
                        text_rect=text_rect,
                    ),
                )
                break
            if best is None or score < best[0]:
                best = (
                    score,
                    PlacedAngularDimension(
                        dimension=dimension,
                        center=center,
                        arc_rect=arc_rect,
                        start_angle_deg=angle_first,
                        span_angle_deg=span,
                        extension_lines=(
                            (center, _arc_point(center, radius, angle_first)),
                            (center, _arc_point(center, radius, angle_second)),
                        ),
                        text_center=label_center,
                        text_rect=text_rect,
                    ),
                )
        if best is None or (best[0] > 0 and dimension.priority < 60):
            continue
        placed.append(best[1])
        label_obstacles.append(_inflate(best[1].text_rect, 1.0))
        placed_label_obstacles.append(_inflate(best[1].text_rect, 1.0))
        line_obstacles.append(_inflate(best[1].arc_rect, 1.0))

    return tuple(placed)
