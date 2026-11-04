# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dimensioned construction sketch for a wire antenna.

The widget is deliberately a renderer: the shape and the dimension requests
come from :mod:`antennadesk.ui.geometry`, which has no Qt dependency.  This
keeps antenna interpretation out of the painting code and lets the same scene
be exported or tested without a GUI.
"""

from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QEvent, QPointF, QRect, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QMouseEvent,
    QPageSize,
    QPainter,
    QPaintEvent,
    QPdfWriter,
    QPen,
    QPolygonF,
    QWheelEvent,
)
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QSizePolicy, QWidget

from ...domain.antennas.antenna import AntennaModel
from ...domain.antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE
from ...domain.antennas.folded_dipole import ANTENNA_TYPE_FOLDED_DIPOLE
from ...domain.antennas.geometry import Point3D
from ...domain.antennas.j_pole import ANTENNA_TYPE_J_POLE
from ...domain.antennas.loop import ANTENNA_TYPE_LOOP
from ..geometry.builder import build_scene, effective_antenna_type, type_label
from ..geometry.dxf_export import write_dxf
from ..geometry.layout import (
    PlacedAngularDimension,
    PlacedDimension,
    SceneTransform,
    layout_angular_dimensions,
    layout_dimensions,
)
from ..geometry.scene import GeometryScene, SceneInset, ScenePoint
from ..geometry.views import GeometryViewMode, recommended_view
from ..i18n import Translator
from ..theme import theme_colors
from ..units import UnitSystem, length_from_m, length_unit_key

__all__ = ["GeometryView", "GeometryViewMode"]


class GeometryView(QWidget):
    """A dimensioned construction sketch driven by the canonical model."""

    ZOOM_STEPS = (0.5, 1.0, 2.0, 4.0, 8.0)
    zoom_changed = Signal(float)

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem = UnitSystem.METRIC,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._model: AntennaModel | None = None
        self._parameters: object | None = None
        self._antenna_type: str | None = None
        self._display_name: str | None = None
        self._mode = GeometryViewMode.ELEVATION
        self._height_exaggeration = 1.0
        self._zoom = 1.0
        self._pan = QPointF(0.0, 0.0)
        self._three_d_yaw_deg = 42.0
        self._three_d_pitch_deg = 24.0
        self._dragging = False
        self._drag_origin = QPointF(0.0, 0.0)
        self._drag_pan = QPointF(0.0, 0.0)
        self._suppress_header = False
        self._last_summary: str | None = None
        self._scene: GeometryScene | None = None
        self._colors = theme_colors(self.palette())
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def sizeHint(self) -> QSize:
        return QSize(700, 330)

    def minimumSizeHint(self) -> QSize:
        return QSize(360, 240)

    @property
    def mode(self) -> GeometryViewMode:
        return self._mode

    @property
    def scene(self) -> GeometryScene | None:
        return self._scene

    def clear_model(self) -> None:
        self._model = None
        self._parameters = None
        self._antenna_type = None
        self._display_name = None
        self._scene = None
        self._last_summary = None
        self.update()

    def save_image(self, path: Path) -> None:
        pixmap = self.grab()
        if pixmap.isNull() or not pixmap.save(str(path), "PNG"):
            raise OSError(f"could not write geometry image: {path}")

    def save_svg(self, path: Path) -> None:
        generator = QSvgGenerator()
        generator.setFileName(str(path))
        generator.setSize(self.size())
        generator.setViewBox(QRect(0, 0, self.width(), self.height()))
        generator.setTitle(self._translator.t("panel.geometry"))
        painter = QPainter(generator)
        try:
            self._render(painter, QRectF(0.0, 0.0, self.width(), self.height()))
        finally:
            painter.end()
        if not path.is_file() or path.stat().st_size == 0:
            raise OSError(f"could not write geometry SVG: {path}")

    def save_pdf(self, path: Path) -> None:
        writer = QPdfWriter(str(path))
        writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        writer.setResolution(96)
        painter = QPainter(writer)
        try:
            page = QRectF(0.0, 0.0, writer.width(), writer.height())
            painter.fillRect(page, self._colors.background)
            scale = (
                min(
                    page.width() / max(self.width(), 1),
                    page.height() / max(self.height(), 1),
                )
                * 0.92
            )
            painter.translate(
                (page.width() - self.width() * scale) / 2.0,
                (page.height() - self.height() * scale) / 2.0,
            )
            painter.scale(scale, scale)
            self._render(painter, QRectF(0.0, 0.0, self.width(), self.height()))
        finally:
            painter.end()
        if not path.is_file() or path.stat().st_size == 0:
            raise OSError(f"could not write geometry PDF: {path}")

    def save_dxf(self, path: Path) -> None:
        scene = self._ensure_scene()
        if scene is None:
            raise OSError("no geometry model to export")
        write_dxf(
            scene,
            path,
            scene.summary or self._translator.t("panel.geometry"),
        )

    def set_model(
        self,
        model: AntennaModel | None,
        *,
        antenna_type: str | None = None,
        display_name: str | None = None,
        parameters: object | None = None,
    ) -> None:
        self._model = model
        self._parameters = parameters
        self._antenna_type = antenna_type if antenna_type is not None else self._infer_type(model)
        self._display_name = display_name
        self._pan = QPointF(0.0, 0.0)
        self._zoom = 1.0
        self._height_exaggeration = 1.0
        self._three_d_yaw_deg = 42.0
        self._three_d_pitch_deg = 24.0
        self._scene = None
        self._mode = recommended_view(model) if model is not None else GeometryViewMode.ELEVATION
        self.zoom_changed.emit(1.0)
        self.update()

    def recommended_mode(self) -> GeometryViewMode:
        if self._model is None:
            return GeometryViewMode.ELEVATION
        return recommended_view(self._model)

    @staticmethod
    def _infer_type(model: AntennaModel | None) -> str | None:
        if model is None:
            return None
        if any(wire.id == "top-connector" for wire in model.wires):
            return ANTENNA_TYPE_J_POLE
        if any(wire.id.startswith("ring-") for wire in model.wires):
            return "ringo"
        if any(wire.id.startswith("element-") for wire in model.wires):
            return "yagi"
        if len(model.wires) == 1:
            return ANTENNA_TYPE_WIRE_DIPOLE
        if len(model.wires) == 4:
            lengths = sorted(wire.length_m for wire in model.wires)
            if math.isclose(lengths[0], lengths[1], rel_tol=1e-6) and (
                lengths[2] > lengths[1] * 1.5
            ):
                return ANTENNA_TYPE_FOLDED_DIPOLE
            return ANTENNA_TYPE_LOOP
        if len(model.wires) >= 3:
            return ANTENNA_TYPE_LOOP
        return None

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        self._unit_system = unit_system
        self._scene = None
        self.update()

    def set_view_mode(self, mode: GeometryViewMode) -> None:
        if mode is self._mode:
            return
        self._mode = mode
        self._scene = None
        self.update()

    def set_zoom(self, factor: float) -> None:
        if not math.isfinite(factor):
            raise ValueError("zoom must be finite")
        factor = min(max(factor, 0.25), 8.0)
        if math.isclose(factor, self._zoom):
            return
        self._zoom = factor
        if math.isclose(factor, 1.0):
            self._pan = QPointF(0.0, 0.0)
        self.zoom_changed.emit(factor)
        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        if delta == 0:
            return
        steps = self.ZOOM_STEPS
        current = min(steps, key=lambda step: abs(step - self._zoom))
        index = steps.index(current) + (1 if delta > 0 else -1)
        index = min(max(index, 0), len(steps) - 1)
        self.set_zoom(steps[index])
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._model is not None:
            self._dragging = True
            self._drag_origin = event.position()
            self._drag_pan = QPointF(self._pan)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            if self._mode is GeometryViewMode.THREE_D:
                delta = event.position() - self._drag_origin
                self._drag_origin = event.position()
                self._three_d_yaw_deg = (self._three_d_yaw_deg + delta.x() * 0.45) % 360.0
                self._three_d_pitch_deg = min(
                    max(self._three_d_pitch_deg + delta.y() * 0.35, -85.0),
                    85.0,
                )
            else:
                delta = event.position() - self._drag_origin
                self._pan = QPointF(
                    self._drag_pan.x() + delta.x(),
                    self._drag_pan.y() + delta.y(),
                )
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._dragging and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pan = QPointF(0.0, 0.0)
            self._zoom = 1.0
            if self._mode is GeometryViewMode.THREE_D:
                self._three_d_yaw_deg = 42.0
                self._three_d_pitch_deg = 24.0
            self.zoom_changed.emit(1.0)
            self.update()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def set_height_exaggeration(self, factor: float) -> None:
        if not math.isfinite(factor) or factor <= 0.0:
            raise ValueError("height exaggeration must be positive and finite")
        if math.isclose(factor, self._height_exaggeration):
            return
        self._height_exaggeration = factor
        self._scene = None
        self.update()

    def retranslate(self) -> None:
        self._scene = None
        self.update()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.PaletteChange:
            self._colors = theme_colors(self.palette())
            self.update()
        super().changeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        self._render(painter, QRectF(self.rect()))

    def _render(self, painter: QPainter, rect: QRectF) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.fillRect(rect, self._colors.background)
        if rect.width() < 120.0 or rect.height() < 80.0:
            return

        if self._model is None:
            self._draw_header(painter, rect, None)
            painter.setPen(self._colors.secondary_text)
            painter.setFont(QFont("Sans Serif", 10))
            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignCenter,
                self._translator.t("geometry.none"),
            )
            return

        if self._mode is GeometryViewMode.THREE_D:
            self._suppress_header = True
            self._last_summary = None
            painter.save()
            painter.translate(self._pan)
            self._paint_three_d(painter, rect)
            painter.restore()
            self._suppress_header = False
            self._draw_header(painter, rect, self._last_summary)
            return

        scene = self._ensure_scene()
        if scene is None:
            self._draw_header(painter, rect, None)
            return
        self._paint_scene(painter, rect, scene)

    def _ensure_scene(self) -> GeometryScene | None:
        if self._scene is not None:
            return self._scene
        if self._model is None:
            return None
        self._scene = build_scene(
            self._model,
            antenna_type=self._antenna_type,
            parameters=self._parameters,
            display_name=self._display_name,
            mode=self._mode,
            translator=self._translator,
            unit_system=self._unit_system,
            height_exaggeration=self._height_exaggeration,
        )
        return self._scene

    def _paint_scene(self, painter: QPainter, rect: QRectF, scene: GeometryScene) -> None:
        self._last_summary = scene.summary
        header_height = 54.0
        safe_rect = QRectF(
            rect.left() + 12.0,
            rect.top() + header_height,
            rect.width() - 24.0,
            rect.height() - header_height - 54.0,
        )
        if safe_rect.width() < 80.0 or safe_rect.height() < 60.0:
            self._draw_header(painter, rect, scene.summary)
            return
        bounds = scene.bounds()
        if bounds is None:
            self._draw_header(painter, rect, scene.summary)
            return
        min_point, max_point = bounds
        span_x = max(max_point.x_m - min_point.x_m, 1e-6)
        span_y = max(max_point.y_m - min_point.y_m, 1e-6)
        margin_x = min(max(38.0, safe_rect.width() * 0.10), 90.0)
        available = QRectF(
            safe_rect.left() + margin_x,
            safe_rect.top() + 12.0,
            safe_rect.width() - 2.0 * margin_x,
            safe_rect.height() - 54.0,
        )
        if available.width() < 30.0 or available.height() < 30.0:
            self._draw_header(painter, rect, scene.summary)
            return
        scale = min(available.width() / span_x, available.height() / span_y) * self._zoom
        center_scene = ScenePoint(
            (min_point.x_m + max_point.x_m) / 2.0,
            (min_point.y_m + max_point.y_m) / 2.0,
        )
        transform = SceneTransform(
            center_scene=center_scene,
            center_screen=available.center(),
            scale=scale,
            pan=self._pan,
        )
        geometry_rect = self._scene_bounds(scene, transform)
        reserved = list(self._reserved_rects(safe_rect, scene))
        if scene.show_ground and scene.ground_y_m is not None:
            ground_y = transform.to_screen(ScenePoint(0.0, scene.ground_y_m)).y()
            if ground_y < safe_rect.bottom():
                reserved.append(
                    QRectF(
                        safe_rect.left(),
                        ground_y + 1.0,
                        safe_rect.width(),
                        max(safe_rect.bottom() - ground_y - 1.0, 0.0),
                    )
                )
        reserved_tuple = tuple(reserved)
        font_metrics = QFontMetricsF(QFont("Sans Serif", 8))
        placed = layout_dimensions(
            scene,
            transform,
            safe_rect,
            geometry_rect,
            reserved_tuple,
            font_metrics,
        )
        placed_angular = layout_angular_dimensions(
            scene,
            transform,
            safe_rect,
            reserved_tuple,
            tuple(item.text_rect for item in placed),
            font_metrics,
        )
        hidden = (
            len(scene.dimensions)
            - len(placed)
            + len(scene.angular_dimensions)
            - len(placed_angular)
        )
        display_summary = scene.summary
        if hidden > 0:
            key = "geometry.dimension_hidden" if hidden == 1 else "geometry.dimensions_hidden"
            display_summary = f"{display_summary} · {self._translator.t(key, count=hidden)}"
        self._last_summary = display_summary
        painter.save()
        painter.setClipRect(safe_rect)
        if scene.show_ground and scene.ground_y_m is not None:
            self._draw_scene_ground(painter, transform, safe_rect, scene.ground_y_m)
        self._draw_dimension_lines(painter, placed)
        self._draw_polylines(painter, scene, transform)
        self._draw_markers(painter, scene, transform, placed, reserved_tuple)
        self._draw_dimension_labels(painter, placed)
        self._draw_angular_dimensions(painter, placed_angular)
        painter.restore()
        self._draw_insets(painter, scene, safe_rect)
        self._draw_scale_bar(
            painter,
            x_left=safe_rect.left() + 8.0,
            bar_y=safe_rect.bottom() - 14.0,
            scale=scale,
            unit=self._translator.t(length_unit_key(self._unit_system)),
        )
        if scene.is_plan:
            self._draw_compass(
                painter,
                QRectF(safe_rect.right() - 58.0, safe_rect.top() + 4.0, 54.0, 54.0),
                scene.azimuth_deg or 0.0,
            )
        self._draw_header(painter, rect, display_summary)

    def _scene_bounds(self, scene: GeometryScene, transform: SceneTransform) -> QRectF:
        points = [transform.to_screen(point) for point in scene.points()]
        if not points:
            return QRectF()
        return QRectF(
            min(point.x() for point in points),
            min(point.y() for point in points),
            max(point.x() for point in points) - min(point.x() for point in points),
            max(point.y() for point in points) - min(point.y() for point in points),
        )

    def _reserved_rects(self, safe_rect: QRectF, scene: GeometryScene) -> tuple[QRectF, ...]:
        rects: list[QRectF] = [
            QRectF(
                safe_rect.left(),
                safe_rect.bottom() - 34.0,
                min(230.0, safe_rect.width() * 0.5),
                34.0,
            ),
        ]
        if scene.is_plan:
            rects.append(QRectF(safe_rect.right() - 62.0, safe_rect.top(), 62.0, 60.0))
        for index, _inset in enumerate(reversed(scene.insets)):
            rects.append(
                QRectF(
                    safe_rect.right() - 172.0,
                    safe_rect.bottom() - 142.0 - index * 138.0,
                    168.0,
                    134.0,
                )
            )
        return tuple(rects)

    def _draw_scene_ground(
        self,
        painter: QPainter,
        transform: SceneTransform,
        safe_rect: QRectF,
        ground_y_m: float,
    ) -> None:
        y = transform.to_screen(ScenePoint(0.0, ground_y_m)).y()
        if y < safe_rect.top() or y > safe_rect.bottom():
            return
        painter.setPen(QPen(self._colors.ground, 2.0))
        painter.drawLine(QPointF(safe_rect.left(), y), QPointF(safe_rect.right(), y))
        painter.setPen(QPen(self._colors.light_line, 1.0))
        clip = QRectF(safe_rect.left(), y, safe_rect.width(), 16.0)
        painter.save()
        painter.setClipRect(clip)
        x = safe_rect.left()
        while x <= safe_rect.right() + 10.0:
            painter.drawLine(QPointF(x, y), QPointF(x - 9.0, y + 9.0))
            x += 14.0
        painter.restore()

    def _draw_polylines(
        self,
        painter: QPainter,
        scene: GeometryScene,
        transform: SceneTransform,
    ) -> None:
        for polyline in scene.polylines:
            if polyline.style == "dashed":
                pen = QPen(self._colors.light_line, polyline.width, Qt.PenStyle.DashLine)
            elif polyline.style == "construction":
                pen = QPen(self._colors.light_line, polyline.width, Qt.PenStyle.DashDotLine)
            else:
                pen = QPen(self._colors.wire, polyline.width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            points = [transform.to_screen(point) for point in polyline.points]
            painter.drawPolyline(QPolygonF(points))

    def _draw_dimension_lines(
        self,
        painter: QPainter,
        placed: tuple[PlacedDimension, ...],
    ) -> None:
        painter.setPen(QPen(self._colors.light_line, 1.0))
        for item in placed:
            for first, second in item.extension_lines:
                painter.drawLine(first, second)
        painter.setPen(QPen(self._colors.dimension, 1.0))
        for item in placed:
            if item.leader_only:
                midpoint = QPointF(
                    (item.extension_lines[0][0].x() + item.extension_lines[1][0].x()) / 2.0,
                    (item.extension_lines[0][0].y() + item.extension_lines[1][0].y()) / 2.0,
                )
                painter.drawLine(midpoint, item.text_center)
                self._draw_arrowhead(painter, item.text_center, QPointF(-1.0, 0.0), size=4.0)
                continue
            painter.drawLine(item.line_start, item.line_end)
            dx = item.line_end.x() - item.line_start.x()
            dy = item.line_end.y() - item.line_start.y()
            distance = math.hypot(dx, dy)
            if distance <= 1e-9:
                continue
            ux = dx / distance
            uy = dy / distance
            self._draw_arrowhead(painter, item.line_start, QPointF(-ux, -uy))
            self._draw_arrowhead(painter, item.line_end, QPointF(ux, uy))

    def _draw_dimension_labels(
        self,
        painter: QPainter,
        placed: tuple[PlacedDimension, ...],
    ) -> None:
        painter.setFont(QFont("Sans Serif", 8))
        for item in placed:
            painter.fillRect(item.text_rect, self._colors.background)
            painter.setPen(self._colors.text)
            painter.drawText(
                item.text_rect,
                Qt.AlignmentFlag.AlignCenter,
                item.dimension.text,
            )

    def _draw_angular_dimensions(
        self,
        painter: QPainter,
        placed: tuple[PlacedAngularDimension, ...],
    ) -> None:
        painter.setFont(QFont("Sans Serif", 8))
        for item in placed:
            painter.setPen(QPen(self._colors.light_line, 1.0))
            for first, second in item.extension_lines:
                painter.drawLine(first, second)
            painter.setPen(QPen(self._colors.dimension, 1.0))
            painter.drawArc(
                item.arc_rect,
                round(item.start_angle_deg * 16.0),
                round(item.span_angle_deg * 16.0),
            )
            painter.fillRect(item.text_rect, self._colors.background)
            painter.setPen(self._colors.text)
            painter.drawText(
                item.text_rect,
                Qt.AlignmentFlag.AlignCenter,
                item.dimension.text,
            )

    def _draw_markers(
        self,
        painter: QPainter,
        scene: GeometryScene,
        transform: SceneTransform,
        placed: tuple[PlacedDimension, ...],
        reserved: tuple[QRectF, ...],
    ) -> None:
        obstacles = [item.text_rect for item in placed] + list(reserved)
        for marker in scene.markers:
            point = transform.to_screen(marker.point)
            if marker.kind == "feed":
                painter.setPen(QPen(self._colors.feed, 2.0))
                painter.setBrush(self._colors.feed)
                painter.drawEllipse(point, 4.0, 4.0)
                painter.setBrush(Qt.BrushStyle.NoBrush)
            elif marker.kind == "load":
                self._draw_load_marker(painter, point, marker.label or "")
                continue
            if marker.label:
                self._draw_marker_label(
                    painter,
                    point,
                    marker.label,
                    obstacles,
                    color=self._colors.feed if marker.kind == "feed" else self._colors.text,
                )
                obstacles.append(QRectF(point.x() + 6.0, point.y() - 16.0, 70.0, 14.0))

    def _draw_marker_label(
        self,
        painter: QPainter,
        point: QPointF,
        text: str,
        obstacles: list[QRectF],
        *,
        color: QColor | None = None,
    ) -> None:
        font = QFont("Sans Serif", 8)
        painter.setFont(font)
        metrics = QFontMetricsF(font)
        text_rect = QRectF(
            point.x() + 10.0,
            point.y() - 18.0,
            metrics.horizontalAdvance(text) + 8.0,
            16.0,
        )
        for candidate in (
            QRectF(point.x() + 10.0, point.y() - 18.0, text_rect.width(), 16.0),
            QRectF(point.x() - 10.0 - text_rect.width(), point.y() - 18.0, text_rect.width(), 16.0),
            QRectF(point.x() + 10.0, point.y() + 4.0, text_rect.width(), 16.0),
            QRectF(point.x() - 10.0 - text_rect.width(), point.y() + 4.0, text_rect.width(), 16.0),
        ):
            if not any(candidate.intersects(obstacle) for obstacle in obstacles):
                text_rect = candidate
                break
        painter.fillRect(text_rect, self._colors.background)
        painter.setPen(color or self._colors.text)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_insets(
        self,
        painter: QPainter,
        scene: GeometryScene,
        safe_rect: QRectF,
    ) -> None:
        for index, inset in enumerate(reversed(scene.insets)):
            outer = QRectF(
                safe_rect.right() - 172.0,
                safe_rect.bottom() - 142.0 - index * 138.0,
                168.0,
                134.0,
            )
            painter.setPen(QPen(self._colors.light_line, 1.0, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(outer)
            painter.setPen(self._colors.secondary_text)
            painter.setFont(QFont("Sans Serif", 7))
            painter.drawText(
                QRectF(outer.left() + 6.0, outer.top() + 3.0, outer.width() - 12.0, 14.0),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                inset.label,
            )
            self._paint_inset(painter, inset, outer.adjusted(8.0, 20.0, -8.0, -8.0))

    def _paint_inset(self, painter: QPainter, inset: SceneInset, rect: QRectF) -> None:
        points = [
            ScenePoint(point.x_m, point.y_m)
            for polyline in inset.polylines
            for point in polyline.points
        ]
        extents = None
        if points:
            extents = (
                min(point.x_m for point in points),
                max(point.x_m for point in points),
                min(point.y_m for point in points),
                max(point.y_m for point in points),
            )
        if extents is None:
            return
        min_x, max_x, min_y, max_y = extents
        span_x = max(max_x - min_x, 1e-9)
        span_y = max(max_y - min_y, 1e-9)
        scale = min(rect.width() / span_x, rect.height() / span_y) * 0.72
        transform = SceneTransform(
            center_scene=ScenePoint((min_x + max_x) / 2.0, (min_y + max_y) / 2.0),
            center_screen=rect.center(),
            scale=scale,
            pan=QPointF(0.0, 0.0),
        )
        painter.save()
        painter.setClipRect(rect)
        for polyline in inset.polylines:
            pen = QPen(
                self._colors.light_line if polyline.style != "solid" else self._colors.wire,
                max(polyline.width, 1.0),
                Qt.PenStyle.DashLine if polyline.style == "dashed" else Qt.PenStyle.SolidLine,
            )
            painter.setPen(pen)
            painter.drawPolyline(
                QPolygonF([transform.to_screen(point) for point in polyline.points])
            )
        for marker in inset.markers:
            point = transform.to_screen(marker.point)
            painter.setPen(QPen(self._colors.feed, 1.5))
            painter.setBrush(self._colors.feed)
            painter.drawEllipse(point, 2.5, 2.5)
            painter.setBrush(Qt.BrushStyle.NoBrush)
        metrics = QFontMetricsF(QFont("Sans Serif", 7))
        placed = layout_dimensions(
            GeometryScene(
                polylines=inset.polylines,
                markers=inset.markers,
                dimensions=inset.dimensions,
            ),
            transform,
            rect,
            rect,
            (),
            metrics,
        )
        painter.setPen(QPen(self._colors.light_line, 1.0))
        for item in placed:
            for first, second in item.extension_lines:
                painter.drawLine(first, second)
        painter.setPen(QPen(self._colors.dimension, 1.0))
        for item in placed:
            if item.leader_only:
                midpoint = QPointF(
                    (item.extension_lines[0][0].x() + item.extension_lines[1][0].x()) / 2.0,
                    (item.extension_lines[0][0].y() + item.extension_lines[1][0].y()) / 2.0,
                )
                painter.drawLine(midpoint, item.text_center)
            else:
                painter.drawLine(item.line_start, item.line_end)
                dx = item.line_end.x() - item.line_start.x()
                dy = item.line_end.y() - item.line_start.y()
                distance = math.hypot(dx, dy)
                if distance > 1e-9:
                    ux = dx / distance
                    uy = dy / distance
                    self._draw_arrowhead(painter, item.line_start, QPointF(-ux, -uy), size=4.0)
                    self._draw_arrowhead(painter, item.line_end, QPointF(ux, uy), size=4.0)
            painter.fillRect(item.text_rect, self._colors.background)
            painter.setPen(self._colors.text)
            painter.setFont(QFont("Sans Serif", 7))
            painter.drawText(
                item.text_rect,
                Qt.AlignmentFlag.AlignCenter,
                item.dimension.text,
            )
        painter.restore()

    def _draw_header(
        self,
        painter: QPainter,
        rect: QRectF,
        summary: str | None,
    ) -> None:
        self._last_summary = summary
        if self._suppress_header:
            return
        painter.setPen(self._colors.text)
        painter.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        painter.drawText(
            QRectF(rect.left() + 16.0, rect.top() + 8.0, rect.width() - 32.0, 20.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self._translator.t("panel.geometry"),
        )
        if summary:
            font = QFont("Sans Serif", 8)
            painter.setFont(font)
            metrics = QFontMetricsF(font)
            text = metrics.elidedText(
                summary,
                Qt.TextElideMode.ElideRight,
                int(rect.width() - 32.0),
            )
            painter.setPen(self._colors.secondary_text)
            painter.drawText(
                QRectF(rect.left() + 16.0, rect.top() + 29.0, rect.width() - 32.0, 18.0),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                text,
            )

    def _paint_three_d(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        xs = [point.x_m for wire in self._model.wires for point in (wire.start, wire.end)]
        ys = [point.y_m for wire in self._model.wires for point in (wire.start, wire.end)]
        zs = [point.z_m for wire in self._model.wires for point in (wire.start, wire.end)]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        max_z = max(zs)
        unit = self._translator.t(length_unit_key(self._unit_system))
        type_label_text = self._type_label()
        summary = self._translator.t(
            "geometry.3d_summary",
            type=type_label_text or self._translator.t("antenna_type.wire_dipole"),
            count=len(self._model.wires),
            height=f"{length_from_m(max_z, self._unit_system):.2f} {unit}",
        )
        self._draw_header(painter, rect, summary)

        draw_rect = QRectF(
            rect.left() + 72.0,
            rect.top() + 82.0,
            rect.width() - 72.0 - 88.0,
            rect.height() - 82.0 - 82.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 50.0:
            return

        yaw = math.radians(self._three_d_yaw_deg)
        pitch = math.radians(self._three_d_pitch_deg)
        cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
        cos_pitch, sin_pitch = math.cos(pitch), math.sin(pitch)

        projected: list[tuple[float, float]] = []
        for wire in self._model.wires:
            for point in (wire.start, wire.end):
                projected.append(
                    self._project_3d(
                        point.x_m,
                        point.y_m,
                        point.z_m,
                        cos_yaw,
                        sin_yaw,
                        cos_pitch,
                        sin_pitch,
                    )
                )
        projected.extend(
            [
                self._project_3d(min_x, min_y, 0.0, cos_yaw, sin_yaw, cos_pitch, sin_pitch),
                self._project_3d(max_x, min_y, 0.0, cos_yaw, sin_yaw, cos_pitch, sin_pitch),
                self._project_3d(min_x, max_y, 0.0, cos_yaw, sin_yaw, cos_pitch, sin_pitch),
                self._project_3d(max_x, max_y, 0.0, cos_yaw, sin_yaw, cos_pitch, sin_pitch),
            ]
        )
        proj_x = [point[0] for point in projected]
        proj_y = [point[1] for point in projected]
        span_x = max(max(proj_x) - min(proj_x), 1e-9)
        span_y = max(max(proj_y) - min(proj_y), 1e-9)
        scale = min(draw_rect.width() / span_x, draw_rect.height() / span_y) * 0.76 * self._zoom
        if scale <= 0.0:
            return
        center_proj_x = (min(proj_x) + max(proj_x)) / 2.0
        center_proj_y = (min(proj_y) + max(proj_y)) / 2.0
        center = draw_rect.center()

        def screen(x_m: float, y_m: float, z_m: float) -> QPointF:
            px, py = self._project_3d(x_m, y_m, z_m, cos_yaw, sin_yaw, cos_pitch, sin_pitch)
            return QPointF(
                center.x() + (px - center_proj_x) * scale,
                center.y() - (py - center_proj_y) * scale,
            )

        painter.setPen(QPen(self._colors.light_line, 1.0, Qt.PenStyle.DotLine))
        for index in range(5):
            ratio = index / 4.0
            x = min_x + (max_x - min_x) * ratio
            y = min_y + (max_y - min_y) * ratio
            painter.drawLine(screen(x, min_y, 0.0), screen(x, max_y, 0.0))
            painter.drawLine(screen(min_x, y, 0.0), screen(max_x, y, 0.0))

        painter.setPen(QPen(self._colors.wire, 2.5))
        for wire in self._model.wires:
            painter.drawLine(
                screen(wire.start.x_m, wire.start.y_m, wire.start.z_m),
                screen(wire.end.x_m, wire.end.y_m, wire.end.z_m),
            )

        feed_wire = self._model.feed_wire
        feed_ratio = min(max(self._model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
        feed = screen(
            feed_wire.start.x_m + (feed_wire.end.x_m - feed_wire.start.x_m) * feed_ratio,
            feed_wire.start.y_m + (feed_wire.end.y_m - feed_wire.start.y_m) * feed_ratio,
            feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * feed_ratio,
        )
        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.setBrush(self._colors.feed)
        painter.drawEllipse(feed, 4.0, 4.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        self._draw_centered_label(
            painter,
            QPointF(feed.x() + 20.0, feed.y() - 12.0),
            self._translator.t("geometry.feed"),
            color=self._colors.feed,
        )
        for load, label, _ratio in self._load_marks():
            self._draw_load_marker(
                painter,
                screen(load.x_m, load.y_m, load.z_m),
                label,
            )

        origin = screen(0.0, 0.0, 0.0)
        painter.setPen(QPen(self._colors.axis, 1.5))
        for end, label in (
            (screen(1.0, 0.0, 0.0), "X"),
            (screen(0.0, 1.0, 0.0), "Y"),
            (screen(0.0, 0.0, 1.0), "Z"),
        ):
            painter.drawLine(origin, end)
            self._draw_centered_label(painter, end, label, font_size=7)

        self._draw_scale_bar(
            painter,
            x_left=rect.left() + 96.0,
            bar_y=rect.bottom() - 38.0,
            scale=scale,
            unit=unit,
        )

    @staticmethod
    def _project_3d(
        x_m: float,
        y_m: float,
        z_m: float,
        cos_yaw: float,
        sin_yaw: float,
        cos_pitch: float,
        sin_pitch: float,
    ) -> tuple[float, float]:
        rotated_x = x_m * cos_yaw - y_m * sin_yaw
        rotated_y = x_m * sin_yaw + y_m * cos_yaw
        return rotated_x, rotated_y * sin_pitch + z_m * cos_pitch

    def _type_label(self) -> str | None:
        return type_label(
            self._translator,
            effective_antenna_type(self._antenna_type, self._parameters),
            self._parameters,
            self._display_name,
        )

    def _load_marks(self) -> tuple[tuple[Point3D, str, float], ...]:
        assert self._model is not None
        marks: list[tuple[Point3D, str, float]] = []
        for index, load in enumerate(self._model.loads, start=1):
            wire = self._model.wire_by_id(load.wire_id)
            ratio = min(max(load.offset_m / wire.length_m, 0.0), 1.0)
            point = Point3D(
                x_m=wire.start.x_m + (wire.end.x_m - wire.start.x_m) * ratio,
                y_m=wire.start.y_m + (wire.end.y_m - wire.start.y_m) * ratio,
                z_m=wire.start.z_m + (wire.end.z_m - wire.start.z_m) * ratio,
            )
            marks.append((point, f"L{index}", ratio))
        return tuple(marks)

    def _installation_summary(self, height_m: float, feed_z_m: float) -> str:
        unit = self._translator.t(length_unit_key(self._unit_system))
        height_text = f"{length_from_m(height_m, self._unit_system):.2f} {unit}"
        feed_text = f"{length_from_m(feed_z_m, self._unit_system):.2f} {unit}"
        type_label_text = self._type_label()
        if type_label_text is None:
            return self._translator.t(
                "geometry.elevation_summary",
                height=height_text,
                feed=feed_text,
            )
        return self._translator.t(
            "geometry.elevation_summary_typed",
            type=type_label_text,
            height=height_text,
            feed=feed_text,
        )

    def _multi_wire_plan_summary(self, width_m: float, depth_m: float, unit: str) -> str:
        assert self._model is not None
        if self._antenna_type == ANTENNA_TYPE_FOLDED_DIPOLE:
            long_wires = sorted(self._model.wires, key=lambda wire: wire.length_m, reverse=True)[:2]
            element_m = long_wires[0].length_m
            spacing_m = math.dist(
                (long_wires[0].start.x_m, long_wires[0].start.y_m),
                (long_wires[1].start.x_m, long_wires[1].start.y_m),
            )
            total_conductor_m = 2.0 * element_m + 2.0 * spacing_m
            return self._translator.t(
                "geometry.plan_summary_folded",
                element=f"{length_from_m(element_m, self._unit_system):.2f} {unit}",
                spacing=f"{length_from_m(spacing_m, self._unit_system):.2f} {unit}",
                total=f"{length_from_m(total_conductor_m, self._unit_system):.2f} {unit}",
            )
        if self._antenna_type == ANTENNA_TYPE_LOOP:
            circumference_m = sum(wire.length_m for wire in self._model.wires)
            points = [
                (point.x_m, point.y_m)
                for wire in self._model.wires
                for point in (wire.start, wire.end)
            ]
            diameter_m = max(math.dist(first, second) for first in points for second in points)
            return self._translator.t(
                "geometry.plan_summary_loop",
                circumference=f"{length_from_m(circumference_m, self._unit_system):.2f} {unit}",
                diameter=f"{length_from_m(diameter_m, self._unit_system):.2f} {unit}",
                sides=len(self._model.wires),
            )
        return self._translator.t(
            "geometry.plan_summary_multi",
            count=len(self._model.wires),
            width=f"{length_from_m(width_m, self._unit_system):.2f} {unit}",
            depth=f"{length_from_m(depth_m, self._unit_system):.2f} {unit}",
        )

    def _folded_spacing_m(self) -> float:
        assert self._model is not None
        long_wires = sorted(self._model.wires, key=lambda wire: wire.length_m, reverse=True)[:2]
        if len(long_wires) < 2:
            return 0.0
        first, second = long_wires
        dx = first.end.x_m - first.start.x_m
        dy = first.end.y_m - first.start.y_m
        length = math.hypot(dx, dy)
        if length < 1e-9:
            return 0.0
        return abs(
            (second.start.x_m - first.start.x_m) * (-dy / length)
            + (second.start.y_m - first.start.y_m) * (dx / length)
        )

    def _draw_load_marker(self, painter: QPainter, point: QPointF, label: str) -> None:
        painter.setPen(QPen(self._colors.reactance, 1.5))
        painter.setBrush(self._colors.reactance)
        painter.drawPolygon(
            QPolygonF(
                [
                    QPointF(point.x(), point.y() - 5.0),
                    QPointF(point.x() + 5.0, point.y()),
                    QPointF(point.x(), point.y() + 5.0),
                    QPointF(point.x() - 5.0, point.y()),
                ]
            )
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        self._draw_centered_label(
            painter,
            QPointF(point.x() + 13.0, point.y() - 10.0),
            label,
            color=self._colors.reactance,
            font_size=7,
        )

    def _draw_scale_bar(
        self,
        painter: QPainter,
        *,
        x_left: float,
        bar_y: float,
        scale: float,
        unit: str,
    ) -> None:
        px_per_display_unit = scale * (1.0 if self._unit_system is UnitSystem.METRIC else 0.3048)
        candidates = [
            0.01,
            0.02,
            0.05,
            0.1,
            0.2,
            0.5,
            1.0,
            2.0,
            5.0,
            10.0,
            20.0,
            50.0,
            100.0,
            200.0,
        ]
        max_pixels = max(self.width() * 0.35, 40.0)
        fitting = [value for value in candidates if value * px_per_display_unit <= max_pixels]
        if not fitting:
            fitting = [candidates[0]]
        ideal = min(fitting, key=lambda value: abs(value * px_per_display_unit - 100.0))
        bar_length = ideal * px_per_display_unit
        painter.setPen(QPen(self._colors.dimension, 1.0))
        painter.drawLine(QPointF(x_left, bar_y), QPointF(x_left + bar_length, bar_y))
        painter.drawLine(QPointF(x_left, bar_y - 5.0), QPointF(x_left, bar_y + 5.0))
        painter.drawLine(
            QPointF(x_left + bar_length, bar_y - 5.0),
            QPointF(x_left + bar_length, bar_y + 5.0),
        )
        painter.setFont(QFont("Sans Serif", 8))
        painter.setPen(self._colors.secondary_text)
        painter.drawText(
            QRectF(x_left, bar_y - 22.0, 120.0, 16.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"{self._translator.t('geometry.scale')} {ideal:g} {unit}",
        )

    def _draw_ground(
        self,
        painter: QPainter,
        x_left: float,
        x_right: float,
        y: float,
    ) -> None:
        painter.setPen(QPen(self._colors.ground, 2.0))
        painter.drawLine(QPointF(x_left, y), QPointF(x_right, y))
        painter.setPen(QPen(self._colors.light_line, 1.0))
        clip = QRectF(x_left, y, x_right - x_left, 18.0)
        painter.save()
        painter.setClipRect(clip)
        x = x_left
        while x <= x_right + 10.0:
            painter.drawLine(QPointF(x, y), QPointF(x - 9.0, y + 9.0))
            x += 14.0
        painter.restore()

    def _draw_compass(self, painter: QPainter, rect: QRectF, azimuth: float) -> None:
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2.0 - 3.0
        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)
        painter.setFont(QFont("Sans Serif", 7))
        painter.setPen(self._colors.secondary_text)
        painter.drawText(
            QRectF(center.x() - 8.0, center.y() - radius - 12.0, 16.0, 12.0),
            Qt.AlignmentFlag.AlignCenter,
            "Y",
        )
        painter.drawText(
            QRectF(center.x() + radius + 3.0, center.y() - 7.0, 12.0, 14.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "X",
        )
        angle = math.radians(azimuth)
        direction = QPointF(math.cos(angle), -math.sin(angle))
        end = QPointF(
            center.x() + direction.x() * (radius - 2.0),
            center.y() + direction.y() * (radius - 2.0),
        )
        painter.setPen(QPen(self._colors.wire, 2.0))
        painter.drawLine(center, end)
        painter.setBrush(self._colors.wire)
        painter.drawEllipse(end, 2.5, 2.5)
        painter.setBrush(Qt.BrushStyle.NoBrush)

    def _draw_centered_label(
        self,
        painter: QPainter,
        center: QPointF,
        text: str,
        *,
        color: QColor | None = None,
        font_size: int = 8,
    ) -> None:
        if color is None:
            color = self._colors.text
        font = QFont("Sans Serif", font_size)
        painter.setFont(font)
        metrics = QFontMetricsF(font)
        text_rect = metrics.boundingRect(text)
        background = QRectF(
            center.x() - text_rect.width() / 2.0 - 3.0,
            center.y() - text_rect.height() / 2.0 - 1.0,
            text_rect.width() + 6.0,
            text_rect.height() + 2.0,
        )
        painter.fillRect(background, self._colors.background)
        painter.setPen(color)
        painter.drawText(background, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_rotated_label(
        self,
        painter: QPainter,
        center: QPointF,
        text: str,
        angle: float,
        *,
        color: QColor | None = None,
        font_size: int = 8,
    ) -> None:
        if color is None:
            color = self._colors.text
        while angle > 90.0:
            angle -= 180.0
        while angle < -90.0:
            angle += 180.0
        font = QFont("Sans Serif", font_size)
        painter.save()
        painter.translate(center)
        painter.rotate(angle)
        painter.setFont(font)
        metrics = QFontMetricsF(font)
        text_rect = metrics.boundingRect(text)
        background = QRectF(
            -text_rect.width() / 2.0 - 3.0,
            -text_rect.height() / 2.0 - 1.0,
            text_rect.width() + 6.0,
            text_rect.height() + 2.0,
        )
        painter.fillRect(background, self._colors.background)
        painter.setPen(color)
        painter.drawText(background, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

    def _draw_arrowhead(
        self,
        painter: QPainter,
        tip: QPointF,
        direction: QPointF,
        *,
        size: float = 5.0,
    ) -> None:
        length = math.hypot(direction.x(), direction.y())
        if length <= 0.0:
            return
        unit_x = direction.x() / length
        unit_y = direction.y() / length
        base_x = tip.x() - unit_x * size
        base_y = tip.y() - unit_y * size
        perpendicular_x = -unit_y * size * 0.45
        perpendicular_y = unit_x * size * 0.45
        polygon = QPolygonF(
            [
                tip,
                QPointF(base_x + perpendicular_x, base_y + perpendicular_y),
                QPointF(base_x - perpendicular_x, base_y - perpendicular_y),
            ]
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._colors.dimension)
        painter.drawPolygon(polygon)
        painter.setBrush(Qt.BrushStyle.NoBrush)
