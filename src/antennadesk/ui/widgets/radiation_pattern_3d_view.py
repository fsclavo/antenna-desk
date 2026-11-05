# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Isometric 3D radiation-pattern wireframe."""

from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QWheelEvent,
)
from PySide6.QtWidgets import QApplication, QSizePolicy, QWidget

from ...domain.simulation.pattern import takeoff_angle_deg
from ..fonts import scaled_font
from ..i18n import Translator
from ..theme import theme_colors

GAIN_COLOR_BINS = 24
GAIN_LINE_ALPHA = 190
INTERACTION_DELAY_MS = 120
FULL_MESH_THRESHOLD = 4_000
# The stored far-field pattern is unchanged. The high-resolution paint mesh
# uses a 40% coarser angular step to keep the 3D view responsive on slower PCs.
FULL_MESH_RESOLUTION_SCALE = 1.4


def gain_color(normalized: float, alpha: int = GAIN_LINE_ALPHA) -> QColor:
    """Map a 0..1 normalized gain to green, yellow, or red."""

    value = min(max(normalized, 0.0), 1.0)
    if value <= 0.5:
        ratio = value * 2.0
        start = (34, 197, 94)
        end = (250, 204, 21)
    else:
        ratio = (value - 0.5) * 2.0
        start = (250, 204, 21)
        end = (239, 68, 68)
    return QColor(
        round(start[0] + (end[0] - start[0]) * ratio),
        round(start[1] + (end[1] - start[1]) * ratio),
        round(start[2] + (end[2] - start[2]) * ratio),
        alpha,
    )


@dataclass(frozen=True, slots=True)
class _MeshVertex:
    x: float
    y: float
    z: float
    normalized_gain: float
    theta_deg: float
    phi_deg: float
    theta_index: int
    phi_index: int


@dataclass(frozen=True, slots=True)
class _Mesh:
    vertices: tuple[_MeshVertex, ...]
    segments: tuple[tuple[int, int, int], ...]
    raw_min_gain: float
    raw_max_gain: float
    min_gain: float
    max_gain: float
    uniform_gain: bool
    max_point: tuple[float, float, float]


def _segment_bin(first: float, second: float) -> int:
    normalized = (first + second) / 2.0
    return min(int(normalized * GAIN_COLOR_BINS), GAIN_COLOR_BINS - 1)


def _build_mesh(points: tuple[tuple[float, float, float], ...]) -> _Mesh | None:
    filtered = [
        (theta, phi, gain) for theta, phi, gain in points if math.isfinite(gain) and gain > -100.0
    ]
    if len(filtered) < 4:
        return None

    gains = [gain for _, _, gain in filtered]
    raw_min_gain = min(gains)
    raw_max_gain = max(gains)
    uniform_gain = math.isclose(raw_max_gain, raw_min_gain)
    min_gain = raw_min_gain
    max_gain = raw_max_gain if not uniform_gain else raw_min_gain + 1.0
    span = max(max_gain - min_gain, 1e-9)

    def normalized_gain(gain: float) -> float:
        if uniform_gain:
            return 0.5
        return min(max((gain - min_gain) / span, 0.0), 1.0)

    theta_values = sorted({theta for theta, _, _ in filtered})
    phi_values = sorted({phi for _, phi, _ in filtered})
    theta_index = {value: index for index, value in enumerate(theta_values)}
    phi_index = {value: index for index, value in enumerate(phi_values)}
    gain_by_grid: dict[tuple[int, int], float] = {}
    for theta, phi, gain in filtered:
        gain_by_grid[(theta_index[theta], phi_index[phi])] = gain

    vertices: list[_MeshVertex] = []
    vertex_by_grid: dict[tuple[int, int], int] = {}
    for theta_position, theta in enumerate(theta_values):
        theta_rad = math.radians(theta)
        sin_theta = math.sin(theta_rad)
        cos_theta = math.cos(theta_rad)
        for phi_position, phi in enumerate(phi_values):
            grid_gain = gain_by_grid.get((theta_position, phi_position))
            if grid_gain is None:
                continue
            phi_rad = math.radians(phi)
            vertex_by_grid[(theta_position, phi_position)] = len(vertices)
            vertices.append(
                _MeshVertex(
                    x=sin_theta * math.cos(phi_rad),
                    y=sin_theta * math.sin(phi_rad),
                    z=cos_theta,
                    normalized_gain=normalized_gain(grid_gain),
                    theta_deg=theta,
                    phi_deg=phi,
                    theta_index=theta_position,
                    phi_index=phi_position,
                )
            )

    segments: list[tuple[int, int, int]] = []
    for phi_position in range(len(phi_values)):
        previous: tuple[int, float] | None = None
        for theta_position in range(len(theta_values)):
            vertex_index = vertex_by_grid.get((theta_position, phi_position))
            if vertex_index is None:
                previous = None
                continue
            current = (vertex_index, vertices[vertex_index].normalized_gain)
            if previous is not None:
                segments.append((previous[0], current[0], _segment_bin(previous[1], current[1])))
            previous = current

    for theta_position in range(len(theta_values)):
        previous = None
        for phi_position in range(len(phi_values)):
            vertex_index = vertex_by_grid.get((theta_position, phi_position))
            if vertex_index is None:
                previous = None
                continue
            current = (vertex_index, vertices[vertex_index].normalized_gain)
            if previous is not None:
                segments.append((previous[0], current[0], _segment_bin(previous[1], current[1])))
            previous = current

    return _Mesh(
        vertices=tuple(vertices),
        segments=tuple(segments),
        raw_min_gain=raw_min_gain,
        raw_max_gain=raw_max_gain,
        min_gain=min_gain,
        max_gain=max_gain,
        uniform_gain=uniform_gain,
        max_point=max(filtered, key=lambda item: item[2]),
    )


def _retained_positions(count: int, target_count: int) -> tuple[int, ...]:
    """Return evenly distributed grid positions, including both endpoints."""

    if count <= target_count:
        return tuple(range(count))
    target_count = max(2, target_count)
    return tuple(
        sorted({round(index * (count - 1) / (target_count - 1)) for index in range(target_count)})
    )


def _resampled_mesh(
    mesh: _Mesh,
    theta_positions: tuple[int, ...],
    phi_positions: tuple[int, ...],
) -> _Mesh:
    """Return a mesh retaining only the requested grid positions."""

    vertex_by_grid = {(vertex.theta_index, vertex.phi_index): vertex for vertex in mesh.vertices}
    vertices: list[_MeshVertex] = []
    index_by_grid: dict[tuple[int, int], int] = {}
    for theta_position in theta_positions:
        for phi_position in phi_positions:
            vertex = vertex_by_grid.get((theta_position, phi_position))
            if vertex is None:
                continue
            index_by_grid[(theta_position, phi_position)] = len(vertices)
            vertices.append(vertex)
    if len(vertices) < 4:
        return mesh

    segments: list[tuple[int, int, int]] = []
    for phi_position in phi_positions:
        previous: tuple[int, float] | None = None
        for theta_position in theta_positions:
            index = index_by_grid.get((theta_position, phi_position))
            if index is None:
                previous = None
                continue
            current = (index, vertices[index].normalized_gain)
            if previous is not None:
                segments.append((previous[0], current[0], _segment_bin(previous[1], current[1])))
            previous = current
    for theta_position in theta_positions:
        previous = None
        for phi_position in phi_positions:
            index = index_by_grid.get((theta_position, phi_position))
            if index is None:
                previous = None
                continue
            current = (index, vertices[index].normalized_gain)
            if previous is not None:
                segments.append((previous[0], current[0], _segment_bin(previous[1], current[1])))
            previous = current

    return _Mesh(
        vertices=tuple(vertices),
        segments=tuple(segments),
        raw_min_gain=mesh.raw_min_gain,
        raw_max_gain=mesh.raw_max_gain,
        min_gain=mesh.min_gain,
        max_gain=mesh.max_gain,
        uniform_gain=mesh.uniform_gain,
        max_point=mesh.max_point,
    )


def _interpolated_mesh(
    mesh: _Mesh,
    theta_count: int,
    phi_count: int,
) -> _Mesh:
    """Build a regular mesh at the requested angular grid size.

    Interpolating the normalized gain keeps the displayed spacing uniform;
    selecting every Nth source index would leave alternating 1° and 2° gaps
    and make the wireframe look irregular.
    """

    theta_count = max(2, theta_count)
    phi_count = max(2, phi_count)
    source_theta_count = max(vertex.theta_index for vertex in mesh.vertices) + 1
    source_phi_count = max(vertex.phi_index for vertex in mesh.vertices) + 1
    theta_min = min(vertex.theta_deg for vertex in mesh.vertices)
    theta_max = max(vertex.theta_deg for vertex in mesh.vertices)
    phi_min = min(vertex.phi_deg for vertex in mesh.vertices)
    phi_max = max(vertex.phi_deg for vertex in mesh.vertices)
    gain_by_grid = {
        (vertex.theta_index, vertex.phi_index): vertex.normalized_gain for vertex in mesh.vertices
    }

    def interpolate_gain(theta_position: float, phi_position: float) -> float | None:
        theta_low = min(max(math.floor(theta_position), 0), source_theta_count - 1)
        theta_high = min(theta_low + 1, source_theta_count - 1)
        phi_low = min(max(math.floor(phi_position), 0), source_phi_count - 1)
        phi_high = min(phi_low + 1, source_phi_count - 1)
        theta_fraction = theta_position - theta_low
        phi_fraction = phi_position - phi_low
        weighted: list[tuple[float, float]] = []
        for theta_index, theta_weight in (
            (theta_low, 1.0 - theta_fraction),
            (theta_high, theta_fraction),
        ):
            for phi_index, phi_weight in (
                (phi_low, 1.0 - phi_fraction),
                (phi_high, phi_fraction),
            ):
                value = gain_by_grid.get((theta_index, phi_index))
                if value is not None and theta_weight * phi_weight > 0.0:
                    weighted.append((value, theta_weight * phi_weight))
        if not weighted:
            return None
        total_weight = sum(weight for _value, weight in weighted)
        return sum(value * weight for value, weight in weighted) / total_weight

    vertices: list[_MeshVertex] = []
    index_by_grid: dict[tuple[int, int], int] = {}
    for theta_position in range(theta_count):
        theta_deg = (
            theta_min
            if theta_count == 1
            else theta_min + (theta_max - theta_min) * theta_position / (theta_count - 1)
        )
        source_theta = theta_position * (source_theta_count - 1) / (theta_count - 1)
        theta_rad = math.radians(theta_deg)
        sin_theta = math.sin(theta_rad)
        cos_theta = math.cos(theta_rad)
        for phi_position in range(phi_count):
            phi_deg = (
                phi_min
                if phi_count == 1
                else phi_min + (phi_max - phi_min) * phi_position / (phi_count - 1)
            )
            source_phi = phi_position * (source_phi_count - 1) / (phi_count - 1)
            gain = interpolate_gain(source_theta, source_phi)
            if gain is None:
                continue
            phi_rad = math.radians(phi_deg)
            index_by_grid[(theta_position, phi_position)] = len(vertices)
            vertices.append(
                _MeshVertex(
                    x=sin_theta * math.cos(phi_rad),
                    y=sin_theta * math.sin(phi_rad),
                    z=cos_theta,
                    normalized_gain=gain,
                    theta_deg=theta_deg,
                    phi_deg=phi_deg,
                    theta_index=theta_position,
                    phi_index=phi_position,
                )
            )
    if len(vertices) < 4:
        return mesh

    segments: list[tuple[int, int, int]] = []
    for phi_position in range(phi_count):
        previous: tuple[int, float] | None = None
        for theta_position in range(theta_count):
            index = index_by_grid.get((theta_position, phi_position))
            if index is None:
                previous = None
                continue
            current = (index, vertices[index].normalized_gain)
            if previous is not None:
                segments.append((previous[0], current[0], _segment_bin(previous[1], current[1])))
            previous = current
    for theta_position in range(theta_count):
        previous = None
        for phi_position in range(phi_count):
            index = index_by_grid.get((theta_position, phi_position))
            if index is None:
                previous = None
                continue
            current = (index, vertices[index].normalized_gain)
            if previous is not None:
                segments.append((previous[0], current[0], _segment_bin(previous[1], current[1])))
            previous = current

    return _Mesh(
        vertices=tuple(vertices),
        segments=tuple(segments),
        raw_min_gain=mesh.raw_min_gain,
        raw_max_gain=mesh.raw_max_gain,
        min_gain=mesh.min_gain,
        max_gain=mesh.max_gain,
        uniform_gain=mesh.uniform_gain,
        max_point=mesh.max_point,
    )


def _reduced_full_mesh(mesh: _Mesh) -> _Mesh:
    """Reduce the high-resolution paint mesh by 40% angular resolution."""

    if len(mesh.vertices) <= FULL_MESH_THRESHOLD:
        return mesh
    theta_count = max(vertex.theta_index for vertex in mesh.vertices) + 1
    phi_count = max(vertex.phi_index for vertex in mesh.vertices) + 1
    return _interpolated_mesh(
        mesh,
        round(theta_count / FULL_MESH_RESOLUTION_SCALE),
        round(phi_count / FULL_MESH_RESOLUTION_SCALE),
    )


def _decimated_mesh(mesh: _Mesh) -> _Mesh:
    """Return a coarser mesh for interactive rotation and zoom."""

    if len(mesh.vertices) <= FULL_MESH_THRESHOLD:
        return mesh
    theta_count = max(vertex.theta_index for vertex in mesh.vertices) + 1
    phi_count = max(vertex.phi_index for vertex in mesh.vertices) + 1
    theta_positions = _retained_positions(theta_count, min(theta_count, 19))
    phi_positions = _retained_positions(phi_count, min(phi_count, 37))
    return _resampled_mesh(mesh, theta_positions, phi_positions)


class RadiationPattern3DView(QWidget):
    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._points: tuple[tuple[float, float, float], ...] = ()
        self._full_mesh: _Mesh | None = None
        self._interactive_mesh: _Mesh | None = None
        self._ground = False
        self._yaw_deg = 38.0
        self._pitch_deg = 26.0
        self._zoom = 1.0
        self._dragging = False
        self._interacting = False
        self._last_pos = QPointF(0.0, 0.0)
        self._interaction_timer: QTimer | None = None
        self._colors = theme_colors(self.palette())
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.fontChanged.connect(self._on_application_font_changed)

    def _on_application_font_changed(self, font: QFont) -> None:
        del font
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(640, 420)

    def set_points(
        self,
        points: tuple[tuple[float, float, float], ...],
        *,
        ground: bool = False,
    ) -> None:
        if ground:
            points = tuple(point for point in points if point[0] <= 90.0 + 1e-6)
        self._points = points
        source_mesh = _build_mesh(points)
        self._full_mesh = _reduced_full_mesh(source_mesh) if source_mesh is not None else None
        self._interactive_mesh = _decimated_mesh(source_mesh) if source_mesh is not None else None
        self._ground = ground
        self._stop_interaction_timer()
        self._interacting = False
        self.update()

    def reset_view(self) -> None:
        self._stop_interaction_timer()
        self._interacting = False
        self._yaw_deg = 38.0
        self._pitch_deg = 26.0
        self._zoom = 1.0
        self.update()

    def _interaction_timer_instance(self) -> QTimer:
        if self._interaction_timer is None:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.setInterval(INTERACTION_DELAY_MS)
            timer.timeout.connect(self._end_interaction)
            self._interaction_timer = timer
        return self._interaction_timer

    def _stop_interaction_timer(self) -> None:
        if self._interaction_timer is not None:
            self._interaction_timer.stop()
            self._interaction_timer.deleteLater()
            self._interaction_timer = None

    def _begin_interaction(self) -> None:
        self._interacting = True
        self._interaction_timer_instance().start()

    def _end_interaction(self) -> None:
        self._stop_interaction_timer()
        if not self._interacting:
            return
        self._interacting = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_pos = event.position()
            self._begin_interaction()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._dragging:
            super().mouseMoveEvent(event)
            return
        delta = event.position() - self._last_pos
        self._last_pos = event.position()
        self._yaw_deg = (self._yaw_deg + delta.x() * 0.45) % 360.0
        self._pitch_deg = min(max(self._pitch_deg + delta.y() * 0.35, -85.0), 85.0)
        self._begin_interaction()
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._dragging and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.unsetCursor()
            self._interaction_timer_instance().start()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._stop_interaction_timer()
            self._interacting = False
            self.reset_view()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        if delta == 0:
            return
        self._zoom = min(max(self._zoom * (1.1 if delta > 0 else 1.0 / 1.1), 0.5), 4.0)
        self._begin_interaction()
        self.update()
        event.accept()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.PaletteChange:
            self._colors = theme_colors(self.palette())
            self.update()
        super().changeEvent(event)

    def _max_gain_label(self, point: tuple[float, float, float]) -> str:
        key = "pattern.max_gain_ground" if self._ground else "pattern.max_gain_elevation"
        return self._translator.t(
            key,
            gain=point[2],
            angle=takeoff_angle_deg(point[0]),
        )

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self._colors = theme_colors(self.palette())
        painter.fillRect(self.rect(), self._colors.background)
        rect = QRectF(self.rect())
        if rect.width() < 160.0 or rect.height() < 120.0:
            return

        mesh = self._interactive_mesh if self._interacting else self._full_mesh
        if mesh is None or len(mesh.vertices) < 4:
            painter.setPen(self._colors.secondary_text)
            painter.setFont(scaled_font(9))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._translator.t("pattern.none"))
            return

        raw_min_gain = mesh.raw_min_gain
        raw_max_gain = mesh.raw_max_gain
        uniform_gain = mesh.uniform_gain
        min_gain = mesh.min_gain
        max_gain = mesh.max_gain

        yaw = math.radians(self._yaw_deg)
        pitch = math.radians(self._pitch_deg)
        cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
        cos_pitch, sin_pitch = math.cos(pitch), math.sin(pitch)

        def pattern_point(
            theta_deg: float, phi_deg: float, gain: float
        ) -> tuple[float, float, float]:
            theta = math.radians(theta_deg)
            phi = math.radians(phi_deg)
            radial = max((gain - min_gain) / (max_gain - min_gain), 0.0)
            radius = max(radial, 0.02)
            x = math.sin(theta) * math.cos(phi) * radius
            y = math.sin(theta) * math.sin(phi) * radius
            z = math.cos(theta) * radius
            return x, y, z

        def project(theta_deg: float, phi_deg: float, gain: float) -> tuple[float, float]:
            x, y, z = pattern_point(theta_deg, phi_deg, gain)
            rotated_x = x * cos_yaw - y * sin_yaw
            rotated_y = x * sin_yaw + y * cos_yaw
            return rotated_x, rotated_y * sin_pitch + z * cos_pitch

        projected: list[tuple[float, float]] = []
        for vertex in mesh.vertices:
            radius = max(vertex.normalized_gain, 0.02)
            rotated_x = (vertex.x * cos_yaw - vertex.y * sin_yaw) * radius
            rotated_y = (vertex.x * sin_yaw + vertex.y * cos_yaw) * radius
            projected.append(
                (
                    rotated_x,
                    rotated_y * sin_pitch + vertex.z * radius * cos_pitch,
                )
            )

        extent_points = [
            *projected,
            project(*mesh.max_point),
            project(0.0, 0.0, min_gain),
            project(0.0, 0.0, max_gain),
            project(90.0, 0.0, max_gain),
            project(90.0, 90.0, max_gain),
        ]
        min_px = min(point[0] for point in extent_points)
        max_px = max(point[0] for point in extent_points)
        min_py = min(point[1] for point in extent_points)
        max_py = max(point[1] for point in extent_points)
        span_x = max(max_px - min_px, 1e-9)
        span_y = max(max_py - min_py, 1e-9)
        draw_rect = QRectF(
            rect.left() + 44.0,
            rect.top() + 34.0,
            rect.width() - 88.0,
            rect.height() - 78.0,
        )
        scale = min(draw_rect.width() / span_x, draw_rect.height() / span_y) * 0.8 * self._zoom
        if scale <= 0.0:
            return
        center = draw_rect.center()
        center_px = (min_px + max_px) / 2.0
        center_py = (min_py + max_py) / 2.0

        def screen(theta_deg: float, phi_deg: float, gain: float) -> QPointF:
            px, py = project(theta_deg, phi_deg, gain)
            return QPointF(
                center.x() + (px - center_px) * scale,
                center.y() - (py - center_py) * scale,
            )

        def screen_world(x: float, y: float, z: float) -> QPointF:
            rotated_x = x * cos_yaw - y * sin_yaw
            rotated_y = x * sin_yaw + y * cos_yaw
            px = rotated_x
            py = rotated_y * sin_pitch + z * cos_pitch
            return QPointF(
                center.x() + (px - center_px) * scale,
                center.y() - (py - center_py) * scale,
            )

        screen_points = [
            QPointF(
                center.x() + (px - center_px) * scale,
                center.y() - (py - center_py) * scale,
            )
            for px, py in projected
        ]
        gain_paths = [QPainterPath() for _ in range(GAIN_COLOR_BINS)]
        for first, second, bin_index in mesh.segments:
            path = gain_paths[bin_index]
            path.moveTo(screen_points[first])
            path.lineTo(screen_points[second])

        painter.setBrush(Qt.BrushStyle.NoBrush)
        for index, path in enumerate(gain_paths):
            if path.isEmpty():
                continue
            painter.setPen(QPen(gain_color((index + 0.5) / GAIN_COLOR_BINS), 1.0))
            painter.drawPath(path)

        if self._ground:
            ground_points = [
                screen_world(
                    0.88 * math.cos(math.radians(phi)),
                    0.88 * math.sin(math.radians(phi)),
                    0.0,
                )
                for phi in range(0, 361, 12)
            ]
            painter.setPen(QPen(self._colors.light_line, 1.0, Qt.PenStyle.DotLine))
            for index in range(1, len(ground_points)):
                painter.drawLine(ground_points[index - 1], ground_points[index])
            for phi in range(0, 360, 45):
                painter.drawLine(
                    screen_world(0.0, 0.0, 0.0),
                    screen_world(
                        0.88 * math.cos(math.radians(phi)),
                        0.88 * math.sin(math.radians(phi)),
                        0.0,
                    ),
                )
            painter.setPen(self._colors.secondary_text)
            painter.setFont(scaled_font(7))
            ground_label = screen_world(0.0, -0.88, 0.0)
            painter.drawText(
                QRectF(ground_label.x() - 30.0, ground_label.y() + 4.0, 60.0, 14.0),
                Qt.AlignmentFlag.AlignCenter,
                self._translator.t("pattern.ground"),
            )

        max_point = mesh.max_point
        marker = screen(*max_point)
        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.setBrush(self._colors.feed)
        painter.drawEllipse(marker, 3.5, 3.5)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        max_label = self._max_gain_label(max_point)
        painter.setFont(scaled_font(8))
        metrics = painter.fontMetrics()
        label_width = min(metrics.horizontalAdvance(max_label) + 10.0, rect.width() - 12.0)
        label_height = 18.0
        label_x = marker.x() + 8.0
        label_y = marker.y() - label_height - 4.0
        if label_x + label_width > rect.right() - 6.0:
            label_x = marker.x() - label_width - 8.0
        if label_y < rect.top() + 6.0:
            label_y = marker.y() + 6.0
        label_rect = QRectF(
            max(rect.left() + 6.0, label_x),
            label_y,
            label_width,
            label_height,
        )
        background = QColor(self._colors.background)
        background.setAlpha(220)
        painter.setPen(QPen(self._colors.light_line, 0.8))
        painter.setBrush(background)
        painter.drawRoundedRect(label_rect, 3.0, 3.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(self._colors.feed)
        painter.drawText(
            label_rect.adjusted(5.0, 0.0, -5.0, 0.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            max_label,
        )

        origin = screen(0.0, 0.0, min_gain)
        painter.setPen(QPen(self._colors.axis, 1.5))
        for axis_theta, axis_phi, axis_label in (
            (90.0, 0.0, "X"),
            (90.0, 90.0, "Y"),
            (0.0, 0.0, "Z"),
        ):
            end = screen(axis_theta, axis_phi, max_gain)
            painter.drawLine(origin, end)
            painter.setFont(scaled_font(7))
            painter.setPen(self._colors.secondary_text)
            painter.drawText(
                QRectF(end.x() + 4.0, end.y() - 8.0, 16.0, 16.0),
                axis_label,
            )

        self._draw_gain_legend(
            painter,
            draw_rect,
            raw_min_gain,
            raw_max_gain,
            uniform_gain,
        )

        painter.setPen(self._colors.secondary_text)
        painter.setFont(scaled_font(8))
        painter.drawText(
            QRectF(rect.left() + 14.0, rect.top() + 8.0, rect.width() - 28.0, 18.0),
            self._translator.t("pattern.3d_polar"),
        )
        painter.drawText(
            QRectF(rect.left() + 14.0, rect.bottom() - 22.0, rect.width() - 28.0, 16.0),
            self._translator.t("pattern.3d_hint"),
        )

    def _draw_gain_legend(
        self,
        painter: QPainter,
        draw_rect: QRectF,
        min_gain: float,
        max_gain: float,
        uniform: bool,
    ) -> None:
        if draw_rect.width() < 360.0 or draw_rect.height() < 180.0:
            return

        bar = QRectF(
            draw_rect.right() - 64.0,
            draw_rect.top() + 34.0,
            10.0,
            min(120.0, draw_rect.height() * 0.38),
        )
        painter.setFont(scaled_font(7))
        if uniform:
            painter.setPen(QPen(gain_color(0.5, 255), 0.8))
            painter.setBrush(gain_color(0.5, 255))
            painter.drawRoundedRect(bar, 2.0, 2.0)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(self._colors.secondary_text)
            painter.drawText(
                QRectF(bar.right() + 4.0, bar.center().y() - 7.0, 72.0, 14.0),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                f"{max_gain:.1f} dBi",
            )
            return

        gradient = QLinearGradient(bar.topLeft(), bar.bottomLeft())
        gradient.setColorAt(0.0, gain_color(1.0, 255))
        gradient.setColorAt(0.5, gain_color(0.5, 255))
        gradient.setColorAt(1.0, gain_color(0.0, 255))
        painter.setPen(QPen(self._colors.light_line, 0.8))
        painter.setBrush(gradient)
        painter.drawRoundedRect(bar, 2.0, 2.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(self._colors.secondary_text)
        painter.drawText(
            QRectF(bar.left() - 12.0, bar.top() - 18.0, 60.0, 14.0),
            Qt.AlignmentFlag.AlignCenter,
            "dBi",
        )
        painter.drawText(
            QRectF(bar.right() + 4.0, bar.top() - 7.0, 62.0, 14.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"{max_gain:.1f}",
        )
        painter.drawText(
            QRectF(bar.right() + 4.0, bar.bottom() - 7.0, 62.0, 14.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"{min_gain:.1f}",
        )
