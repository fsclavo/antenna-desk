# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction-sketch style geometry view for a wire antenna."""

from __future__ import annotations

import math
from enum import StrEnum
from pathlib import Path

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QPolygonF,
    QWheelEvent,
)
from PySide6.QtWidgets import QSizePolicy, QWidget

from ...domain.antennas.antenna import AntennaModel
from ...domain.antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE
from ...domain.antennas.folded_dipole import ANTENNA_TYPE_FOLDED_DIPOLE
from ...domain.antennas.geometry import Point3D
from ...domain.antennas.j_pole import ANTENNA_TYPE_J_POLE
from ...domain.antennas.loop import ANTENNA_TYPE_LOOP
from ...domain.antennas.wire import Wire
from ..i18n import Translator
from ..theme import theme_colors
from ..units import UnitSystem, length_from_m, length_unit_key


class GeometryViewMode(StrEnum):
    ELEVATION = "elevation"
    PLAN = "plan"
    THREE_D = "3d"


class GeometryView(QWidget):
    """A dimensioned side elevation that reads like a construction sketch."""

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
        self._antenna_type: str | None = None
        self._mode = GeometryViewMode.ELEVATION
        self._height_exaggeration = 1.0
        self._zoom = 1.0
        self._pan = QPointF(0.0, 0.0)
        self._dragging = False
        self._drag_origin = QPointF(0.0, 0.0)
        self._drag_pan = QPointF(0.0, 0.0)
        self._suppress_header = False
        self._last_summary: str | None = None
        self._colors = theme_colors(self.palette())
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def sizeHint(self) -> QSize:
        return QSize(700, 330)

    def minimumSizeHint(self) -> QSize:
        return QSize(360, 240)

    def save_image(self, path: Path) -> None:
        pixmap = self.grab()
        if pixmap.isNull() or not pixmap.save(str(path), "PNG"):
            raise OSError(f"could not write geometry image: {path}")

    def set_model(
        self,
        model: AntennaModel | None,
        *,
        antenna_type: str | None = None,
    ) -> None:
        self._model = model
        self._antenna_type = antenna_type if antenna_type is not None else self._infer_type(model)
        self._pan = QPointF(0.0, 0.0)
        self.update()

    @staticmethod
    def _infer_type(model: AntennaModel | None) -> str | None:
        if model is None:
            return None
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
        self.update()

    def set_view_mode(self, mode: GeometryViewMode) -> None:
        if mode is self._mode:
            return
        self._mode = mode
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
            delta = event.position() - self._drag_origin
            self._pan = QPointF(self._drag_pan.x() + delta.x(), self._drag_pan.y() + delta.y())
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
            self.set_zoom(1.0)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def set_height_exaggeration(self, factor: float) -> None:
        if not math.isfinite(factor) or factor <= 0.0:
            raise ValueError("height exaggeration must be positive and finite")
        if math.isclose(factor, self._height_exaggeration):
            return
        self._height_exaggeration = factor
        self.update()

    def retranslate(self) -> None:
        self.update()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.PaletteChange:
            self._colors = theme_colors(self.palette())
            self.update()
        super().changeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.fillRect(self.rect(), self._colors.background)
        rect = QRectF(self.rect())
        if rect.width() < 120.0 or rect.height() < 80.0:
            return

        if self._model is None:
            self._draw_header(painter, rect, None)
            painter.setPen(self._colors.secondary_text)
            painter.setFont(QFont("Sans Serif", 10))
            painter.drawText(
                rect, Qt.AlignmentFlag.AlignCenter, self._translator.t("geometry.none")
            )
            return

        self._suppress_header = True
        self._last_summary = None
        painter.save()
        painter.translate(self._pan)
        if self._mode is GeometryViewMode.PLAN:
            self._paint_plan(painter, rect)
        elif self._mode is GeometryViewMode.THREE_D:
            self._paint_three_d(painter, rect)
        else:
            self._paint_elevation(painter, rect)
        painter.restore()
        self._suppress_header = False
        self._draw_header(painter, rect, self._last_summary)

    def _paint_three_d(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        xs = [point.x_m for wire in self._model.wires for point in (wire.start, wire.end)]
        ys = [point.y_m for wire in self._model.wires for point in (wire.start, wire.end)]
        zs = [point.z_m for wire in self._model.wires for point in (wire.start, wire.end)]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        max_z = max(zs)
        unit = self._translator.t(length_unit_key(self._unit_system))
        type_label = self._type_label()
        summary = self._translator.t(
            "geometry.3d_summary",
            type=type_label or self._translator.t("antenna_type.wire_dipole"),
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
        yaw = math.radians(42.0)
        pitch = math.radians(24.0)
        cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
        cos_pitch, sin_pitch = math.cos(pitch), math.sin(pitch)

        projected: list[tuple[float, float]] = []
        for wire in self._model.wires:
            for point in (wire.start, wire.end):
                projected.append(
                    self._project_3d(
                        point.x_m, point.y_m, point.z_m, cos_yaw, sin_yaw, cos_pitch, sin_pitch
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

    def _paint_elevation(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        if self._antenna_type == ANTENNA_TYPE_LOOP:
            self._paint_loop_elevation(painter, rect)
            return
        if self._antenna_type == ANTENNA_TYPE_J_POLE:
            self._paint_j_pole_elevation(painter, rect)
            return
        if len(self._model.wires) == 1:
            wire = self._model.wires[0]
            dx = wire.end.x_m - wire.start.x_m
            dy = wire.end.y_m - wire.start.y_m
            if math.hypot(dx, dy) < 1e-9:
                self._draw_vertical_sketch(painter, rect, wire)
                return
        zs = [point.z_m for wire in self._model.wires for point in (wire.start, wire.end)]
        if len(self._model.wires) > 1 and max(zs) - min(zs) > 1e-6:
            self._paint_multi_wire_elevation(painter, rect)
            return
        self._paint_installation_elevation(painter, rect)

    @staticmethod
    def _vertical_wires(model: AntennaModel) -> tuple[Wire, ...]:
        return tuple(
            wire
            for wire in model.wires
            if math.hypot(
                wire.end.x_m - wire.start.x_m,
                wire.end.y_m - wire.start.y_m,
            )
            < 1e-9
        )

    def _paint_j_pole_elevation(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        verticals = self._vertical_wires(self._model)
        if len(verticals) < 2:
            self._paint_multi_wire_elevation(painter, rect)
            return
        radiator = max(verticals, key=lambda wire: wire.length_m)
        stub = min(verticals, key=lambda wire: wire.length_m)
        base_z = min(point.z_m for wire in self._model.wires for point in (wire.start, wire.end))
        top_z = max(point.z_m for wire in self._model.wires for point in (wire.start, wire.end))
        min_x = min(point.x_m for wire in self._model.wires for point in (wire.start, wire.end))
        max_x = max(point.x_m for wire in self._model.wires for point in (wire.start, wire.end))
        span_m = max(max_x - min_x, 1e-9)
        unit = self._translator.t(length_unit_key(self._unit_system))
        summary = self._translator.t(
            "geometry.j_pole_elevation",
            template=self._model.name,
            radiator=f"{length_from_m(radiator.length_m, self._unit_system):.2f} {unit}",
            stub=f"{length_from_m(stub.length_m, self._unit_system):.2f} {unit}",
            spacing=f"{length_from_m(span_m, self._unit_system):.2f} {unit}",
        )
        if not math.isclose(self._height_exaggeration, 1.0):
            summary = (
                summary
                + " · "
                + self._translator.t(
                    "geometry.vertical_exaggeration",
                    factor=f"{self._height_exaggeration:g}",
                )
            )
        self._draw_header(painter, rect, summary)
        draw_rect = QRectF(
            rect.left() + 110.0,
            rect.top() + 84.0,
            rect.width() - 110.0 - 120.0,
            rect.height() - 84.0 - 86.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 50.0:
            return
        z_draw = max(top_z * self._height_exaggeration, 0.5)
        scale = (
            min(
                draw_rect.width() / span_m,
                max(draw_rect.height() - 46.0, 24.0) / z_draw,
            )
            * self._zoom
        )
        if scale <= 0.0:
            return
        ground_y = draw_rect.bottom()
        x_left = draw_rect.center().x() - span_m * scale / 2.0
        x_right = draw_rect.center().x() + span_m * scale / 2.0

        def screen(x_m: float, z_m: float) -> QPointF:
            return QPointF(
                x_left + (x_m - min_x) * scale,
                ground_y - z_m * self._height_exaggeration * scale,
            )

        self._draw_ground(painter, x_left - 34.0, x_right + 34.0, ground_y)
        painter.setPen(QPen(self._colors.wire, 2.5))
        for wire in self._model.wires:
            painter.drawLine(
                screen(wire.start.x_m, wire.start.z_m),
                screen(wire.end.x_m, wire.end.z_m),
            )
        feed_wire = self._model.feed_wire
        ratio = min(max(self._model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
        feed_z = feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * ratio
        feed = screen(feed_wire.start.x_m, feed_z)
        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.setBrush(self._colors.feed)
        painter.drawEllipse(feed, 4.0, 4.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        feed_label_x = (
            feed.x() - 52.0 if stub.start.x_m > (min_x + max_x) / 2.0 else feed.x() + 20.0
        )
        self._draw_centered_label(
            painter,
            QPointF(feed_label_x, feed.y() - 12.0),
            self._translator.t("geometry.feed"),
            color=self._colors.feed,
        )

        radiator_x = radiator.start.x_m
        stub_x = stub.start.x_m
        self._draw_plan_dimension(
            painter,
            screen(radiator_x, radiator.start.z_m),
            screen(radiator_x, radiator.end.z_m),
            QPointF(-34.0, 0.0),
            f"{length_from_m(radiator.length_m, self._unit_system):.2f} {unit}",
        )
        self._draw_plan_dimension(
            painter,
            screen(stub_x, stub.start.z_m),
            screen(stub_x, stub.end.z_m),
            QPointF(34.0, 0.0),
            f"{length_from_m(stub.length_m, self._unit_system):.2f} {unit}",
        )
        self._draw_plan_dimension(
            painter,
            screen(min_x, base_z),
            screen(max_x, base_z),
            QPointF(0.0, 30.0),
            f"{length_from_m(span_m, self._unit_system):.2f} {unit}",
        )
        self._draw_scale_bar(
            painter,
            x_left=x_left,
            bar_y=ground_y + 44.0,
            scale=scale,
            unit=unit,
        )

    def _paint_j_pole_plan(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        verticals = self._vertical_wires(self._model)
        if len(verticals) < 2:
            self._paint_multi_wire_plan(painter, rect)
            return
        radiator = max(verticals, key=lambda wire: wire.length_m)
        stub = min(verticals, key=lambda wire: wire.length_m)
        min_x = min(radiator.start.x_m, stub.start.x_m)
        max_x = max(radiator.start.x_m, stub.start.x_m)
        span_m = max(max_x - min_x, 1e-9)
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._draw_header(
            painter,
            rect,
            self._translator.t(
                "geometry.j_pole_plan",
                template=self._model.name,
                spacing=f"{length_from_m(span_m, self._unit_system):.2f} {unit}",
            ),
        )
        draw_rect = QRectF(
            rect.left() + 100.0,
            rect.top() + 90.0,
            rect.width() - 100.0 - 110.0,
            rect.height() - 90.0 - 120.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 50.0:
            return
        scale = draw_rect.width() / max(span_m * 2.2, 1e-9) * self._zoom
        center = draw_rect.center()
        left = center.x() - span_m * scale / 2.0
        right = center.x() + span_m * scale / 2.0
        y = center.y()
        painter.setPen(QPen(self._colors.wire, 2.5))
        painter.drawLine(QPointF(left, y), QPointF(right, y))
        for x, wire, label in (
            (left, radiator, self._translator.t("geometry.radiator")),
            (right, stub, self._translator.t("geometry.stub")),
        ):
            painter.setPen(
                QPen(self._colors.feed if wire is self._model.feed_wire else self._colors.wire, 2.0)
            )
            painter.setBrush(
                self._colors.feed if wire is self._model.feed_wire else self._colors.wire
            )
            painter.drawEllipse(QPointF(x, y), 6.0, 6.0)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            self._draw_centered_label(painter, QPointF(x, y - 18.0), label)
        self._draw_plan_dimension(
            painter,
            QPointF(left, y),
            QPointF(right, y),
            QPointF(0.0, 30.0),
            f"{length_from_m(span_m, self._unit_system):.2f} {unit}",
        )
        self._draw_scale_bar(
            painter,
            x_left=draw_rect.left(),
            bar_y=draw_rect.bottom() + 50.0,
            scale=scale,
            unit=unit,
        )

    def _paint_multi_wire_elevation(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        xs = [point.x_m for wire in self._model.wires for point in (wire.start, wire.end)]
        ys = [point.y_m for wire in self._model.wires for point in (wire.start, wire.end)]
        use_x = max(xs) - min(xs) >= max(ys) - min(ys)
        horizontal = xs if use_x else ys
        min_h, max_h = min(horizontal), max(horizontal)
        span_m = max(max_h - min_h, 1e-9)
        max_z = max(point.z_m for wire in self._model.wires for point in (wire.start, wire.end))
        unit = self._translator.t(length_unit_key(self._unit_system))
        summary = self._translator.t(
            "geometry.multi_wire_elevation",
            count=len(self._model.wires),
            span=f"{length_from_m(span_m, self._unit_system):.2f} {unit}",
            height=f"{length_from_m(max_z, self._unit_system):.2f} {unit}",
        )
        if not math.isclose(self._height_exaggeration, 1.0):
            summary = (
                summary
                + " · "
                + self._translator.t(
                    "geometry.vertical_exaggeration",
                    factor=f"{self._height_exaggeration:g}",
                )
            )
        self._draw_header(painter, rect, summary)

        draw_rect = QRectF(
            rect.left() + 96.0,
            rect.top() + 84.0,
            rect.width() - 96.0 - 96.0,
            rect.height() - 84.0 - 82.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 50.0:
            return
        z_draw = max(max_z * self._height_exaggeration, 0.5)
        scale = (
            min(
                draw_rect.width() / span_m,
                max(draw_rect.height() - 42.0, 24.0) / z_draw,
            )
            * self._zoom
        )
        if scale <= 0.0:
            return
        ground_y = draw_rect.bottom()
        x_left = draw_rect.center().x() - span_m * scale / 2.0
        x_right = draw_rect.center().x() + span_m * scale / 2.0

        def screen(x_m: float, y_m: float, z_m: float) -> QPointF:
            coordinate = x_m if use_x else y_m
            return QPointF(
                x_left + (coordinate - min_h) * scale,
                ground_y - z_m * self._height_exaggeration * scale,
            )

        self._draw_ground(painter, x_left - 28.0, x_right + 28.0, ground_y)
        painter.setPen(QPen(self._colors.wire, 2.5))
        for wire in self._model.wires:
            painter.drawLine(
                screen(wire.start.x_m, wire.start.y_m, wire.start.z_m),
                screen(wire.end.x_m, wire.end.y_m, wire.end.z_m),
            )
        feed_wire = self._model.feed_wire
        ratio = min(max(self._model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
        feed = screen(
            feed_wire.start.x_m + (feed_wire.end.x_m - feed_wire.start.x_m) * ratio,
            feed_wire.start.y_m + (feed_wire.end.y_m - feed_wire.start.y_m) * ratio,
            feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * ratio,
        )
        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.setBrush(self._colors.feed)
        painter.drawEllipse(feed, 4.0, 4.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        self._draw_centered_label(
            painter,
            QPointF(feed.x() + 22.0, feed.y() - 12.0),
            self._translator.t("geometry.feed"),
            color=self._colors.feed,
        )
        self._draw_plan_dimension(
            painter,
            QPointF(x_left, ground_y - max_z * self._height_exaggeration * scale),
            QPointF(x_right, ground_y - max_z * self._height_exaggeration * scale),
            QPointF(0.0, -30.0),
            f"{length_from_m(span_m, self._unit_system):.2f} {unit}",
        )
        self._draw_height_dimension(
            painter,
            x_left=x_left,
            ground_y=ground_y,
            wire_y=ground_y - max_z * self._height_exaggeration * scale,
            value=f"{length_from_m(max_z, self._unit_system):.2f} {unit}",
        )
        self._draw_scale_bar(
            painter,
            x_left=x_left,
            bar_y=ground_y + 40.0,
            scale=scale,
            unit=unit,
        )

    def _paint_loop_elevation(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        zs = [point.z_m for wire in self._model.wires for point in (wire.start, wire.end)]
        bottom_z = min(zs)
        top_z = max(zs)
        diameter_m = max(top_z - bottom_z, 1e-9)
        unit = self._translator.t(length_unit_key(self._unit_system))
        bottom_text = f"{length_from_m(bottom_z, self._unit_system):.2f} {unit}"
        diameter_text = f"{length_from_m(diameter_m, self._unit_system):.2f} {unit}"
        summary = self._translator.t(
            "geometry.loop_elevation_summary",
            bottom=bottom_text,
            diameter=diameter_text,
        )
        if not math.isclose(self._height_exaggeration, 1.0):
            summary = (
                summary
                + " · "
                + self._translator.t(
                    "geometry.vertical_exaggeration",
                    factor=f"{self._height_exaggeration:g}",
                )
            )
        self._draw_header(painter, rect, summary)

        draw_rect = QRectF(
            rect.left() + 110.0,
            rect.top() + 84.0,
            rect.width() - 110.0 - 110.0,
            rect.height() - 84.0 - 84.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 60.0:
            return
        draw_top = top_z * self._height_exaggeration
        scale = (draw_rect.height() - 42.0) / max(draw_top, 0.5) * self._zoom
        if scale <= 0.0:
            return
        ground_y = draw_rect.bottom()
        x_center = draw_rect.center().x()
        bottom_y = ground_y - bottom_z * self._height_exaggeration * scale
        top_y = ground_y - top_z * self._height_exaggeration * scale
        feed_wire = self._model.feed_wire
        feed_ratio = min(max(self._model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
        feed_z = feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * feed_ratio
        feed_y = ground_y - feed_z * self._height_exaggeration * scale

        self._draw_ground(painter, x_center - 72.0, x_center + 72.0, ground_y)
        self._draw_height_dimension(
            painter,
            x_left=x_center - 26.0,
            ground_y=ground_y,
            wire_y=bottom_y,
            value=bottom_text,
        )
        self._draw_feed_height_dimension(
            painter,
            x_right=x_center + 26.0,
            ground_y=bottom_y,
            feed_y=top_y,
            value=(f"{self._translator.t('geometry.diameter')} {diameter_text}"),
        )

        gap = 9.0
        lower_end = feed_y + gap / 2.0
        upper_start = feed_y - gap / 2.0
        pen = QPen(self._colors.wire, 3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(x_center, top_y), QPointF(x_center, upper_start))
        painter.drawLine(QPointF(x_center, lower_end), QPointF(x_center, bottom_y))
        painter.setPen(QPen(self._colors.wire, 2.0))
        painter.drawLine(QPointF(x_center - 7.0, top_y), QPointF(x_center + 7.0, top_y))
        painter.drawLine(QPointF(x_center - 7.0, bottom_y), QPointF(x_center + 7.0, bottom_y))
        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.drawLine(QPointF(x_center - 8.0, upper_start), QPointF(x_center + 8.0, upper_start))
        painter.drawLine(QPointF(x_center - 8.0, lower_end), QPointF(x_center + 8.0, lower_end))
        painter.setBrush(self._colors.feed)
        painter.setPen(QPen(self._colors.feed, 1.0))
        painter.drawEllipse(QPointF(x_center + 14.0, feed_y), 3.0, 3.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        self._draw_centered_label(
            painter,
            QPointF(x_center + 32.0, feed_y),
            self._translator.t("geometry.feed"),
            color=self._colors.feed,
        )
        self._draw_scale_bar(
            painter,
            x_left=rect.left() + 110.0,
            bar_y=rect.bottom() - 42.0,
            scale=scale,
            unit=unit,
        )

    def _paint_installation_elevation(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        xs = [point.x_m for wire in self._model.wires for point in (wire.start, wire.end)]
        ys = [point.y_m for wire in self._model.wires for point in (wire.start, wire.end)]
        width_m = max(max(xs) - min(xs), 1e-9)
        depth_m = max(max(ys) - min(ys), 1e-9)
        span_m = max(width_m, depth_m)
        height_m = max(max(wire.start.z_m, wire.end.z_m) for wire in self._model.wires)
        feed_wire = self._model.feed_wire
        feed_ratio_wire = self._model.feed.offset_m / feed_wire.length_m
        feed_z = feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * feed_ratio_wire
        unit = self._translator.t(length_unit_key(self._unit_system))
        height_text = f"{length_from_m(height_m, self._unit_system):.2f} {unit}"
        feed_text = f"{length_from_m(feed_z, self._unit_system):.2f} {unit}"
        summary = self._installation_summary(height_m, feed_z)
        if not math.isclose(self._height_exaggeration, 1.0):
            summary = (
                summary
                + " · "
                + self._translator.t(
                    "geometry.vertical_exaggeration",
                    factor=f"{self._height_exaggeration:g}",
                )
            )
        self._draw_header(painter, rect, summary)

        draw_rect = QRectF(
            rect.left() + 92.0,
            rect.top() + 84.0,
            rect.width() - 92.0 - 92.0,
            rect.height() - 84.0 - 82.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 50.0:
            return

        z_draw = max(height_m * self._height_exaggeration, 0.5)
        reserve_above = 58.0
        available_height = max(draw_rect.height() - reserve_above, 24.0)
        scale = min(draw_rect.width() / span_m, available_height / z_draw) * self._zoom
        if scale <= 0.0:
            return

        ground_y = draw_rect.bottom()
        wire_y = ground_y - height_m * self._height_exaggeration * scale
        origin_x = draw_rect.center().x() - span_m * scale / 2.0
        x_left = origin_x
        x_right = origin_x + span_m * scale
        if len(self._model.wires) == 1:
            feed_ratio = feed_ratio_wire
        elif width_m >= depth_m:
            feed_x = (
                feed_wire.start.x_m + (feed_wire.end.x_m - feed_wire.start.x_m) * feed_ratio_wire
            )
            feed_ratio = (feed_x - min(xs)) / width_m if width_m > 1e-9 else 0.5
        else:
            feed_y = (
                feed_wire.start.y_m + (feed_wire.end.y_m - feed_wire.start.y_m) * feed_ratio_wire
            )
            feed_ratio = (feed_y - min(ys)) / depth_m if depth_m > 1e-9 else 0.5
        feed_ratio = min(max(feed_ratio, 0.0), 1.0)
        x_feed = x_left + (x_right - x_left) * feed_ratio
        gap = 9.0

        self._draw_ground(painter, x_left - 32.0, x_right + 32.0, ground_y)
        self._draw_height_dimension(
            painter,
            x_left=x_left,
            ground_y=ground_y,
            wire_y=wire_y,
            value=height_text,
        )
        self._draw_wire(
            painter,
            x_left=x_left,
            x_feed=x_feed,
            x_right=x_right,
            wire_y=wire_y,
            ground_y=ground_y,
            gap=gap,
            center_label=abs(feed_ratio - 0.5) < 1e-9,
            show_ends=self._antenna_type != ANTENNA_TYPE_LOOP,
        )
        if self._antenna_type == ANTENNA_TYPE_LOOP:
            self._draw_plan_dimension(
                painter,
                QPointF(x_left, wire_y),
                QPointF(x_right, wire_y),
                QPointF(0.0, -30.0),
                (
                    f"{self._translator.t('geometry.diameter')} "
                    f"{length_from_m(span_m, self._unit_system):.2f} {unit}"
                ),
            )
        if self._antenna_type == ANTENNA_TYPE_FOLDED_DIPOLE:
            spacing_m = self._folded_spacing_m()
            self._draw_folded_section(painter, rect, spacing_m)
        if abs(feed_z - height_m) > 1e-6:
            self._draw_feed_height_dimension(
                painter,
                x_right=x_right,
                ground_y=ground_y,
                feed_y=ground_y - feed_z * self._height_exaggeration * scale,
                value=feed_text,
            )
        self._draw_scale_bar(
            painter,
            x_left=x_left,
            bar_y=ground_y + 40.0,
            scale=scale,
            unit=unit,
        )

    def _installation_summary(self, height_m: float, feed_z_m: float) -> str:
        unit = self._translator.t(length_unit_key(self._unit_system))
        height_text = f"{length_from_m(height_m, self._unit_system):.2f} {unit}"
        feed_text = f"{length_from_m(feed_z_m, self._unit_system):.2f} {unit}"
        type_label = self._type_label()
        if type_label is None:
            return self._translator.t(
                "geometry.elevation_summary",
                height=height_text,
                feed=feed_text,
            )
        return self._translator.t(
            "geometry.elevation_summary_typed",
            type=type_label,
            height=height_text,
            feed=feed_text,
        )

    def _type_label(self) -> str | None:
        key = {
            ANTENNA_TYPE_WIRE_DIPOLE: "antenna_type.wire_dipole",
            ANTENNA_TYPE_FOLDED_DIPOLE: "antenna_type.folded_dipole",
            ANTENNA_TYPE_LOOP: "antenna_type.loop",
        }.get(self._antenna_type)
        return self._translator.t(key) if key is not None else None

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

    def _paint_plan(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        if len(self._model.wires) > 1:
            if self._antenna_type == ANTENNA_TYPE_FOLDED_DIPOLE:
                self._paint_folded_plan(painter, rect)
            elif self._antenna_type == ANTENNA_TYPE_LOOP:
                self._paint_loop_plan(painter, rect)
            elif self._antenna_type == ANTENNA_TYPE_J_POLE:
                self._paint_j_pole_plan(painter, rect)
            else:
                self._paint_multi_wire_plan(painter, rect)
            return
        wire = self._model.wires[0]
        dx = wire.end.x_m - wire.start.x_m
        dy = wire.end.y_m - wire.start.y_m
        horizontal = math.hypot(dx, dy)
        if horizontal < 1e-9:
            self._draw_vertical_plan_message(painter, rect, wire)
            return

        azimuth = math.degrees(math.atan2(dy, dx)) % 360.0
        length_display = length_from_m(horizontal, self._unit_system)
        unit = self._translator.t(length_unit_key(self._unit_system))
        summary = self._translator.t(
            "geometry.plan_summary",
            length=f"{length_display:.2f} {unit}",
            azimuth=f"{azimuth:.1f}",
        )
        self._draw_header(painter, rect, summary)
        self._draw_compass(painter, rect, azimuth)

        draw_rect = QRectF(
            rect.left() + 86.0,
            rect.top() + 82.0,
            rect.width() - 86.0 - 92.0,
            rect.height() - 82.0 - 106.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 50.0:
            return

        scale_candidates: list[float] = []
        if abs(dx) > 1e-9:
            scale_candidates.append(draw_rect.width() * 0.78 / abs(dx))
        if abs(dy) > 1e-9:
            scale_candidates.append(draw_rect.height() * 0.78 / abs(dy))
        scale = (min(scale_candidates) if scale_candidates else 1.0) * self._zoom
        if scale <= 0.0:
            return

        center = draw_rect.center()
        mid_x = dx / 2.0
        mid_y = dy / 2.0
        start = QPointF(center.x() - mid_x * scale, center.y() + mid_y * scale)
        end = QPointF(center.x() + mid_x * scale, center.y() - mid_y * scale)
        line = end - start
        line_length = math.hypot(line.x(), line.y())
        if line_length < 1.0:
            return
        ux = line.x() / line_length
        uy = line.y() / line_length
        perp = QPointF(-uy, ux)
        label_dir = perp if perp.y() < 0.0 else QPointF(-perp.x(), -perp.y())
        dim_dir = QPointF(-label_dir.x(), -label_dir.y())

        painter.setPen(QPen(self._colors.light_line, 1.0, Qt.PenStyle.DashDotLine))
        painter.drawLine(
            QPointF(center.x() - 16.0, center.y()),
            QPointF(center.x() + 16.0, center.y()),
        )
        painter.drawLine(
            QPointF(center.x(), center.y() - 16.0),
            QPointF(center.x(), center.y() + 16.0),
        )

        feed_ratio = self._model.feed.offset_m / wire.length_m
        feed_ratio = min(max(feed_ratio, 0.0), 1.0)
        feed = QPointF(
            start.x() + line.x() * feed_ratio,
            start.y() + line.y() * feed_ratio,
        )
        gap = 9.0
        left_end = QPointF(feed.x() - ux * gap / 2.0, feed.y() - uy * gap / 2.0)
        right_start = QPointF(feed.x() + ux * gap / 2.0, feed.y() + uy * gap / 2.0)

        pen = QPen(self._colors.wire, 3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(start, left_end)
        painter.drawLine(right_start, end)

        painter.setPen(QPen(self._colors.wire, 2.0))
        painter.drawLine(
            QPointF(start.x() - perp.x() * 7.0, start.y() - perp.y() * 7.0),
            QPointF(start.x() + perp.x() * 7.0, start.y() + perp.y() * 7.0),
        )
        painter.drawLine(
            QPointF(end.x() - perp.x() * 7.0, end.y() - perp.y() * 7.0),
            QPointF(end.x() + perp.x() * 7.0, end.y() + perp.y() * 7.0),
        )

        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.drawLine(
            QPointF(
                left_end.x() - perp.x() * 8.0,
                left_end.y() - perp.y() * 8.0,
            ),
            QPointF(
                left_end.x() + perp.x() * 8.0,
                left_end.y() + perp.y() * 8.0,
            ),
        )
        painter.drawLine(
            QPointF(
                right_start.x() - perp.x() * 8.0,
                right_start.y() - perp.y() * 8.0,
            ),
            QPointF(
                right_start.x() + perp.x() * 8.0,
                right_start.y() + perp.y() * 8.0,
            ),
        )
        painter.setBrush(self._colors.feed)
        painter.setPen(QPen(self._colors.feed, 1.0))
        painter.drawEllipse(
            QPointF(feed.x() + label_dir.x() * 10.0, feed.y() + label_dir.y() * 10.0),
            3.0,
            3.0,
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)

        self._draw_centered_label(
            painter,
            QPointF(feed.x() + label_dir.x() * 20.0, feed.y() + label_dir.y() * 20.0),
            self._translator.t("geometry.feed"),
            color=self._colors.feed,
        )
        if abs(feed_ratio - 0.5) < 1e-9:
            self._draw_centered_label(
                painter,
                QPointF(
                    feed.x() - label_dir.x() * 20.0,
                    feed.y() - label_dir.y() * 20.0,
                ),
                self._translator.t("geometry.center"),
            )
        self._draw_centered_label(
            painter,
            QPointF(start.x() + label_dir.x() * 17.0, start.y() + label_dir.y() * 17.0),
            self._translator.t("geometry.end"),
        )
        self._draw_centered_label(
            painter,
            QPointF(end.x() + label_dir.x() * 17.0, end.y() + label_dir.y() * 17.0),
            self._translator.t("geometry.end"),
        )
        for _load, label, load_ratio in self._load_marks():
            load_point = QPointF(
                start.x() + line.x() * load_ratio,
                start.y() + line.y() * load_ratio,
            )
            self._draw_load_marker(painter, load_point, label)

        dim_offset = 30.0
        dim_start = QPointF(
            start.x() + dim_dir.x() * dim_offset,
            start.y() + dim_dir.y() * dim_offset,
        )
        dim_end = QPointF(
            end.x() + dim_dir.x() * dim_offset,
            end.y() + dim_dir.y() * dim_offset,
        )
        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.drawLine(start, dim_start)
        painter.drawLine(end, dim_end)
        painter.setPen(QPen(self._colors.dimension, 1.0))
        painter.drawLine(dim_start, dim_end)
        self._draw_arrowhead(painter, dim_start, QPointF(-ux, -uy))
        self._draw_arrowhead(painter, dim_end, QPointF(ux, uy))
        angle = math.degrees(math.atan2(dim_end.y() - dim_start.y(), dim_end.x() - dim_start.x()))
        self._draw_rotated_label(
            painter,
            QPointF(
                (dim_start.x() + dim_end.x()) / 2.0 + dim_dir.x() * 10.0,
                (dim_start.y() + dim_end.y()) / 2.0 + dim_dir.y() * 10.0,
            ),
            f"{length_display:.2f} {unit}",
            angle,
        )
        self._draw_plan_leg_dimensions(
            painter,
            start=start,
            feed=feed,
            end=end,
            dim_dir=dim_dir,
            ux=ux,
            uy=uy,
            left_value=f"{length_display * feed_ratio:.2f} {unit}",
            right_value=f"{length_display * (1.0 - feed_ratio):.2f} {unit}",
            offset=56.0,
        )

        self._draw_scale_bar(
            painter,
            x_left=rect.left() + 110.0,
            bar_y=rect.bottom() - 42.0,
            scale=scale,
            unit=unit,
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

    def _draw_plan_leg_dimensions(
        self,
        painter: QPainter,
        *,
        start: QPointF,
        feed: QPointF,
        end: QPointF,
        dim_dir: QPointF,
        ux: float,
        uy: float,
        left_value: str,
        right_value: str,
        offset: float,
    ) -> None:
        start_dim = QPointF(start.x() + dim_dir.x() * offset, start.y() + dim_dir.y() * offset)
        feed_dim = QPointF(feed.x() + dim_dir.x() * offset, feed.y() + dim_dir.y() * offset)
        end_dim = QPointF(end.x() + dim_dir.x() * offset, end.y() + dim_dir.y() * offset)

        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.drawLine(start, start_dim)
        painter.drawLine(feed, feed_dim)
        painter.drawLine(end, end_dim)

        painter.setPen(QPen(self._colors.dimension, 1.0))
        for first, second, value, direction in (
            (start_dim, feed_dim, left_value, (-ux, -uy)),
            (feed_dim, end_dim, right_value, (ux, uy)),
        ):
            if math.hypot(second.x() - first.x(), second.y() - first.y()) < 36.0:
                continue
            painter.drawLine(first, second)
            self._draw_arrowhead(painter, first, QPointF(direction[0], direction[1]))
            self._draw_arrowhead(painter, second, QPointF(-direction[0], -direction[1]))
            angle = math.degrees(math.atan2(second.y() - first.y(), second.x() - first.x()))
            self._draw_rotated_label(
                painter,
                QPointF(
                    (first.x() + second.x()) / 2.0 + dim_dir.x() * 9.0,
                    (first.y() + second.y()) / 2.0 + dim_dir.y() * 9.0,
                ),
                value,
                angle,
            )

    def _draw_plan_dimension(
        self,
        painter: QPainter,
        start: QPointF,
        end: QPointF,
        offset: QPointF,
        value: str,
    ) -> None:
        start_dim = QPointF(start.x() + offset.x(), start.y() + offset.y())
        end_dim = QPointF(end.x() + offset.x(), end.y() + offset.y())
        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.drawLine(start, start_dim)
        painter.drawLine(end, end_dim)
        painter.setPen(QPen(self._colors.dimension, 1.0))
        painter.drawLine(start_dim, end_dim)
        dx = end_dim.x() - start_dim.x()
        dy = end_dim.y() - start_dim.y()
        distance = math.hypot(dx, dy)
        if distance < 1.0:
            return
        ux = dx / distance
        uy = dy / distance
        self._draw_arrowhead(painter, start_dim, QPointF(-ux, -uy))
        self._draw_arrowhead(painter, end_dim, QPointF(ux, uy))
        angle = math.degrees(math.atan2(dy, dx))
        offset_length = math.hypot(offset.x(), offset.y())
        label_offset = QPointF(0.0, 0.0)
        if offset_length > 0.0:
            label_offset = QPointF(
                offset.x() / offset_length * 9.0, offset.y() / offset_length * 9.0
            )
        self._draw_rotated_label(
            painter,
            QPointF(
                (start_dim.x() + end_dim.x()) / 2.0 + label_offset.x(),
                (start_dim.y() + end_dim.y()) / 2.0 + label_offset.y(),
            ),
            value,
            angle,
        )

    def _paint_folded_plan(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        unit = self._translator.t(length_unit_key(self._unit_system))
        long_wires = sorted(self._model.wires, key=lambda wire: wire.length_m, reverse=True)[:2]
        element = long_wires[0]
        other = long_wires[1]
        length_m = element.length_m
        element_dx = element.end.x_m - element.start.x_m
        element_dy = element.end.y_m - element.start.y_m
        element_length = math.hypot(element_dx, element_dy)
        if element_length < 1e-9:
            return
        ux_model = element_dx / element_length
        uy_model = element_dy / element_length
        spacing_m = abs(
            (other.start.x_m - element.start.x_m) * (-uy_model)
            + (other.start.y_m - element.start.y_m) * ux_model
        )
        summary = self._multi_wire_plan_summary(length_m, spacing_m, unit)
        self._draw_header(painter, rect, summary)
        azimuth = math.degrees(math.atan2(element_dy, element_dx)) % 360.0
        self._draw_compass(painter, rect, azimuth)

        draw_rect = QRectF(
            rect.left() + 86.0,
            rect.top() + 82.0,
            rect.width() - 86.0 - 92.0,
            rect.height() - 82.0 - 106.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 50.0:
            return
        scale = draw_rect.width() * 0.68 / length_m * self._zoom
        if scale <= 0.0:
            return
        center = draw_rect.center()
        dx = math.cos(math.radians(azimuth))
        dy = -math.sin(math.radians(azimuth))
        direction = QPointF(dx, dy)
        perpendicular = QPointF(-dy, dx)
        half_length = length_m * scale / 2.0
        start_center = QPointF(
            center.x() - direction.x() * half_length,
            center.y() - direction.y() * half_length,
        )
        end_center = QPointF(
            center.x() + direction.x() * half_length,
            center.y() + direction.y() * half_length,
        )
        actual_gap = spacing_m * scale
        gap = min(max(actual_gap, 22.0), 48.0)
        offset = QPointF(perpendicular.x() * gap / 2.0, perpendicular.y() * gap / 2.0)
        first_start = QPointF(start_center.x() + offset.x(), start_center.y() + offset.y())
        first_end = QPointF(end_center.x() + offset.x(), end_center.y() + offset.y())
        second_start = QPointF(start_center.x() - offset.x(), start_center.y() - offset.y())
        second_end = QPointF(end_center.x() - offset.x(), end_center.y() - offset.y())

        painter.setPen(QPen(self._colors.wire, 2.5))
        painter.drawLine(first_start, first_end)
        painter.drawLine(second_start, second_end)
        pen = QPen(self._colors.wire, 2.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(first_start, second_start)
        painter.drawLine(first_end, second_end)

        feed_wire = self._model.feed_wire
        driven_is_first = feed_wire.length_m >= other.length_m and feed_wire.id == element.id
        feed_start = first_start if driven_is_first else second_start
        feed_end = first_end if driven_is_first else second_end
        feed_ratio = min(max(self._model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
        feed = QPointF(
            feed_start.x() + (feed_end.x() - feed_start.x()) * feed_ratio,
            feed_start.y() + (feed_end.y() - feed_start.y()) * feed_ratio,
        )
        gap_px = 9.0
        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.setBrush(self._colors.background)
        painter.drawLine(
            QPointF(
                feed.x() - direction.x() * gap_px / 2.0, feed.y() - direction.y() * gap_px / 2.0
            ),
            QPointF(
                feed.x() + direction.x() * gap_px / 2.0, feed.y() + direction.y() * gap_px / 2.0
            ),
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self._colors.feed, 1.5))
        painter.setBrush(self._colors.feed)
        painter.drawEllipse(feed, 4.0, 4.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        self._draw_centered_label(
            painter,
            QPointF(feed.x() + perpendicular.x() * 17.0, feed.y() + perpendicular.y() * 17.0),
            self._translator.t("geometry.feed"),
            color=self._colors.feed,
        )

        length_value = f"{length_from_m(length_m, self._unit_system):.2f} {unit}"
        length_text = f"{self._translator.t('field.element_length')} {length_value}"
        self._draw_plan_dimension(
            painter,
            first_start,
            first_end,
            QPointF(perpendicular.x() * 30.0, perpendicular.y() * 30.0),
            length_text,
        )
        spacing_value = f"{length_from_m(spacing_m, self._unit_system):.2f} {unit}"
        spacing_text = f"{self._translator.t('field.spacing')} {spacing_value}"
        self._draw_plan_dimension(
            painter,
            first_end,
            second_end,
            QPointF(direction.x() * 28.0, direction.y() * 28.0),
            spacing_text,
        )
        if not math.isclose(gap, actual_gap, rel_tol=0.05, abs_tol=1.0):
            painter.setPen(self._colors.secondary_text)
            painter.setFont(QFont("Sans Serif", 8))
            painter.drawText(
                QRectF(
                    rect.left() + 16.0,
                    rect.bottom() - 20.0,
                    rect.width() - 32.0,
                    18.0,
                ),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                self._translator.t("geometry.spacing_exaggerated"),
            )
        self._draw_scale_bar(
            painter,
            x_left=rect.left() + 110.0,
            bar_y=rect.bottom() - 42.0,
            scale=scale,
            unit=unit,
        )

    def _paint_loop_plan(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        unit = self._translator.t(length_unit_key(self._unit_system))
        xs = [point.x_m for wire in self._model.wires for point in (wire.start, wire.end)]
        ys = [point.y_m for wire in self._model.wires for point in (wire.start, wire.end)]
        width_m = max(max(xs) - min(xs), 1e-9)
        depth_m = max(max(ys) - min(ys), 1e-9)
        summary = self._multi_wire_plan_summary(width_m, depth_m, unit)
        self._draw_header(painter, rect, summary)
        first_wire = self._model.wires[0]
        azimuth = (
            math.degrees(
                math.atan2(
                    first_wire.end.y_m - first_wire.start.y_m,
                    first_wire.end.x_m - first_wire.start.x_m,
                )
            )
            % 360.0
        )
        self._draw_compass(painter, rect, azimuth)

        draw_rect = QRectF(
            rect.left() + 86.0,
            rect.top() + 82.0,
            rect.width() - 86.0 - 92.0,
            rect.height() - 82.0 - 106.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 50.0:
            return
        points = [
            (point.x_m, point.y_m) for wire in self._model.wires for point in (wire.start, wire.end)
        ]
        diameter_m = max(math.dist(first, second) for first in points for second in points)
        scale = (
            min(draw_rect.width(), draw_rect.height()) / max(diameter_m, 1e-9) * 0.78 * self._zoom
        )
        if scale <= 0.0:
            return
        center = draw_rect.center()
        mid_x = (min(xs) + max(xs)) / 2.0
        mid_y = (min(ys) + max(ys)) / 2.0
        radius_px = diameter_m * scale / 2.0

        painter.setPen(QPen(self._colors.wire, 3.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius_px, radius_px)

        painter.setPen(QPen(self._colors.light_line, 1.0, Qt.PenStyle.DashDotLine))
        painter.drawLine(
            QPointF(center.x() - radius_px - 12.0, center.y()),
            QPointF(center.x() + radius_px + 12.0, center.y()),
        )
        painter.drawLine(
            QPointF(center.x(), center.y() - radius_px - 12.0),
            QPointF(center.x(), center.y() + radius_px + 12.0),
        )

        feed_wire = self._model.feed_wire
        feed_ratio = min(max(self._model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
        feed_x_m = feed_wire.start.x_m + (feed_wire.end.x_m - feed_wire.start.x_m) * feed_ratio
        feed_y_m = feed_wire.start.y_m + (feed_wire.end.y_m - feed_wire.start.y_m) * feed_ratio
        feed_angle = math.atan2(feed_y_m - mid_y, feed_x_m - mid_x)
        feed = QPointF(
            center.x() + math.cos(feed_angle) * radius_px,
            center.y() - math.sin(feed_angle) * radius_px,
        )
        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.setBrush(self._colors.feed)
        painter.drawEllipse(feed, 4.0, 4.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        label_direction = QPointF(math.cos(feed_angle), -math.sin(feed_angle))
        self._draw_centered_label(
            painter,
            QPointF(
                feed.x() + label_direction.x() * 18.0,
                feed.y() + label_direction.y() * 18.0,
            ),
            self._translator.t("geometry.feed"),
            color=self._colors.feed,
        )

        diameter_y = center.y() - radius_px - 14.0
        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.drawLine(
            QPointF(center.x() - radius_px, center.y() - radius_px),
            QPointF(center.x() - radius_px, diameter_y - 3.0),
        )
        painter.drawLine(
            QPointF(center.x() + radius_px, center.y() - radius_px),
            QPointF(center.x() + radius_px, diameter_y - 3.0),
        )
        painter.setPen(QPen(self._colors.dimension, 1.0))
        painter.drawLine(
            QPointF(center.x() - radius_px, diameter_y),
            QPointF(center.x() + radius_px, diameter_y),
        )
        self._draw_arrowhead(
            painter, QPointF(center.x() - radius_px, diameter_y), QPointF(-1.0, 0.0)
        )
        self._draw_arrowhead(
            painter, QPointF(center.x() + radius_px, diameter_y), QPointF(1.0, 0.0)
        )
        self._draw_centered_label(
            painter,
            QPointF(center.x(), diameter_y - 9.0),
            (
                f"{self._translator.t('geometry.diameter')} "
                f"{length_from_m(diameter_m, self._unit_system):.2f} {unit}"
            ),
        )
        self._draw_scale_bar(
            painter,
            x_left=rect.left() + 110.0,
            bar_y=rect.bottom() - 42.0,
            scale=scale,
            unit=unit,
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

    def _paint_multi_wire_plan(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        xs = [point.x_m for wire in self._model.wires for point in (wire.start, wire.end)]
        ys = [point.y_m for wire in self._model.wires for point in (wire.start, wire.end)]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width_m = max(max_x - min_x, 1e-9)
        depth_m = max(max_y - min_y, 1e-9)
        unit = self._translator.t(length_unit_key(self._unit_system))
        width_text = f"{length_from_m(width_m, self._unit_system):.2f} {unit}"
        depth_text = f"{length_from_m(depth_m, self._unit_system):.2f} {unit}"
        summary = self._multi_wire_plan_summary(width_m, depth_m, unit)
        self._draw_header(painter, rect, summary)
        first_wire = self._model.wires[0]
        azimuth = (
            math.degrees(
                math.atan2(
                    first_wire.end.y_m - first_wire.start.y_m,
                    first_wire.end.x_m - first_wire.start.x_m,
                )
            )
            % 360.0
        )
        self._draw_compass(painter, rect, azimuth)

        draw_rect = QRectF(
            rect.left() + 86.0,
            rect.top() + 82.0,
            rect.width() - 86.0 - 92.0,
            rect.height() - 82.0 - 106.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 50.0:
            return
        scale = min(draw_rect.width() / width_m, draw_rect.height() / depth_m) * 0.82 * self._zoom
        if scale <= 0.0:
            return
        center = draw_rect.center()
        mid_x = (min_x + max_x) / 2.0
        mid_y = (min_y + max_y) / 2.0

        def screen(point_x: float, point_y: float) -> QPointF:
            return QPointF(
                center.x() + (point_x - mid_x) * scale,
                center.y() - (point_y - mid_y) * scale,
            )

        painter.setPen(QPen(self._colors.wire, 2.5))
        for wire in self._model.wires:
            painter.drawLine(
                screen(wire.start.x_m, wire.start.y_m),
                screen(wire.end.x_m, wire.end.y_m),
            )

        feed_wire = self._model.feed_wire
        feed_ratio = self._model.feed.offset_m / feed_wire.length_m
        feed = screen(
            feed_wire.start.x_m + (feed_wire.end.x_m - feed_wire.start.x_m) * feed_ratio,
            feed_wire.start.y_m + (feed_wire.end.y_m - feed_wire.start.y_m) * feed_ratio,
        )
        painter.setPen(QPen(self._colors.feed, 1.5))
        painter.setBrush(self._colors.feed)
        painter.drawEllipse(feed, 4.0, 4.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        self._draw_centered_label(
            painter,
            QPointF(feed.x() + 18.0, feed.y() - 12.0),
            self._translator.t("geometry.feed"),
            color=self._colors.feed,
        )
        for load, label, _ratio in self._load_marks():
            self._draw_load_marker(
                painter,
                screen(load.x_m, load.y_m),
                label,
            )
        self._draw_plan_box_dimensions(
            painter,
            left=screen(min_x, 0.0).x(),
            right=screen(max_x, 0.0).x(),
            top=screen(0.0, max_y).y(),
            bottom=screen(0.0, min_y).y(),
            width_text=f"{self._translator.t('geometry.width')} {width_text}",
            depth_text=f"{self._translator.t('geometry.depth')} {depth_text}",
        )
        self._draw_scale_bar(
            painter,
            x_left=rect.left() + 110.0,
            bar_y=rect.bottom() - 42.0,
            scale=scale,
            unit=unit,
        )

    def _draw_plan_box_dimensions(
        self,
        painter: QPainter,
        *,
        left: float,
        right: float,
        top: float,
        bottom: float,
        width_text: str,
        depth_text: str,
    ) -> None:
        if right - left < 2.0 and bottom - top < 2.0:
            return

        width_y = bottom + 24.0
        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.drawLine(QPointF(left, bottom), QPointF(left, width_y + 4.0))
        painter.drawLine(QPointF(right, bottom), QPointF(right, width_y + 4.0))
        if right - left > 24.0:
            painter.setPen(QPen(self._colors.dimension, 1.0))
            painter.drawLine(QPointF(left, width_y), QPointF(right, width_y))
            self._draw_arrowhead(painter, QPointF(left, width_y), QPointF(-1.0, 0.0))
            self._draw_arrowhead(painter, QPointF(right, width_y), QPointF(1.0, 0.0))
            self._draw_centered_label(
                painter,
                QPointF((left + right) / 2.0, width_y + 10.0),
                width_text,
            )

        depth_x = left - 26.0
        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.drawLine(QPointF(left, top), QPointF(depth_x - 4.0, top))
        painter.drawLine(QPointF(left, bottom), QPointF(depth_x - 4.0, bottom))
        if bottom - top > 24.0:
            painter.setPen(QPen(self._colors.dimension, 1.0))
            painter.drawLine(QPointF(depth_x, top), QPointF(depth_x, bottom))
            self._draw_arrowhead(painter, QPointF(depth_x, top), QPointF(0.0, -1.0))
            self._draw_arrowhead(painter, QPointF(depth_x, bottom), QPointF(0.0, 1.0))
            self._draw_rotated_label(
                painter,
                QPointF(depth_x - 9.0, (top + bottom) / 2.0),
                depth_text,
                90.0,
            )

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
        if summary is not None:
            painter.setPen(self._colors.secondary_text)
            painter.setFont(QFont("Sans Serif", 8))
            painter.drawText(
                QRectF(rect.left() + 16.0, rect.top() + 29.0, rect.width() - 32.0, 18.0),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                summary,
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

    def _draw_folded_section(
        self,
        painter: QPainter,
        rect: QRectF,
        spacing_m: float,
    ) -> None:
        unit = self._translator.t(length_unit_key(self._unit_system))
        center = QPointF(rect.right() - 62.0, rect.bottom() - 104.0)
        gap_px = 24.0
        left = QPointF(center.x() - gap_px / 2.0, center.y())
        right = QPointF(center.x() + gap_px / 2.0, center.y())

        painter.setPen(QPen(self._colors.light_line, 1.0, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(QRectF(center.x() - 48.0, center.y() - 35.0, 96.0, 76.0))
        painter.setPen(QPen(self._colors.dimension, 1.0))
        for point in (left, right):
            painter.setBrush(self._colors.background)
            painter.drawEllipse(point, 5.0, 5.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(
            QPointF(left.x(), left.y() + 11.0),
            QPointF(right.x(), right.y() + 11.0),
        )
        self._draw_arrowhead(painter, left, QPointF(-1.0, 0.0), size=4.0)
        self._draw_arrowhead(painter, right, QPointF(1.0, 0.0), size=4.0)
        self._draw_centered_label(
            painter,
            QPointF(center.x(), center.y() - 24.0),
            self._translator.t("geometry.section"),
            font_size=8,
        )
        self._draw_centered_label(
            painter,
            QPointF(center.x(), center.y() + 25.0),
            f"{self._translator.t('field.spacing')} "
            f"{length_from_m(spacing_m, self._unit_system):.2f} {unit}",
            font_size=7,
        )
        self._draw_centered_label(
            painter,
            QPointF(center.x(), center.y() + 39.0),
            self._translator.t("geometry.two_conductors"),
            font_size=7,
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

    def _draw_height_dimension(
        self,
        painter: QPainter,
        *,
        x_left: float,
        ground_y: float,
        wire_y: float,
        value: str,
    ) -> None:
        if abs(ground_y - wire_y) < 2.0:
            return
        dim_x = x_left - 34.0
        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.drawLine(QPointF(x_left, wire_y), QPointF(dim_x - 4.0, wire_y))
        painter.drawLine(QPointF(x_left, ground_y), QPointF(dim_x - 4.0, ground_y))

        painter.setPen(QPen(self._colors.dimension, 1.0))
        painter.drawLine(QPointF(dim_x, ground_y), QPointF(dim_x, wire_y))
        self._draw_arrowhead(painter, QPointF(dim_x, wire_y), QPointF(0.0, -1.0))
        self._draw_arrowhead(painter, QPointF(dim_x, ground_y), QPointF(0.0, 1.0))

        font = QFont("Sans Serif", 8)
        painter.setFont(font)
        text_rect = QRectF(dim_x - 78.0, (ground_y + wire_y) / 2.0 - 9.0, 68.0, 18.0)
        painter.fillRect(text_rect.adjusted(-2.0, 0.0, 2.0, 0.0), self._colors.background)
        painter.setPen(self._colors.text)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            value,
        )

    def _draw_feed_height_dimension(
        self,
        painter: QPainter,
        *,
        x_right: float,
        ground_y: float,
        feed_y: float,
        value: str,
    ) -> None:
        if abs(ground_y - feed_y) < 2.0:
            return
        dim_x = x_right + 34.0
        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.drawLine(QPointF(x_right, feed_y), QPointF(dim_x + 4.0, feed_y))
        painter.drawLine(QPointF(x_right, ground_y), QPointF(dim_x + 4.0, ground_y))
        painter.setPen(QPen(self._colors.dimension, 1.0))
        painter.drawLine(QPointF(dim_x, ground_y), QPointF(dim_x, feed_y))
        self._draw_arrowhead(painter, QPointF(dim_x, feed_y), QPointF(0.0, -1.0))
        self._draw_arrowhead(painter, QPointF(dim_x, ground_y), QPointF(0.0, 1.0))
        self._draw_rotated_label(
            painter,
            QPointF(dim_x + 12.0, (ground_y + feed_y) / 2.0),
            value,
            90.0,
        )

    def _draw_wire(
        self,
        painter: QPainter,
        *,
        x_left: float,
        x_feed: float,
        x_right: float,
        wire_y: float,
        ground_y: float,
        gap: float,
        center_label: bool,
        show_ends: bool = True,
    ) -> None:
        pen = QPen(self._colors.wire, 3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(x_left, wire_y), QPointF(x_feed - gap / 2.0, wire_y))
        painter.drawLine(QPointF(x_feed + gap / 2.0, wire_y), QPointF(x_right, wire_y))

        painter.setPen(QPen(self._colors.wire, 2.0))
        painter.drawLine(QPointF(x_left, wire_y - 7.0), QPointF(x_left, wire_y + 7.0))
        painter.drawLine(QPointF(x_right, wire_y - 7.0), QPointF(x_right, wire_y + 7.0))

        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.drawLine(
            QPointF(x_feed - gap / 2.0, wire_y - 8.0),
            QPointF(x_feed - gap / 2.0, wire_y + 8.0),
        )
        painter.drawLine(
            QPointF(x_feed + gap / 2.0, wire_y - 8.0),
            QPointF(x_feed + gap / 2.0, wire_y + 8.0),
        )
        painter.setBrush(self._colors.feed)
        painter.setPen(QPen(self._colors.feed, 1.0))
        painter.drawEllipse(QPointF(x_feed, wire_y - 12.0), 3.0, 3.0)

        centerline_pen = QPen(self._colors.light_line, 1.0, Qt.PenStyle.DashDotLine)
        painter.setPen(centerline_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(QPointF(x_feed, wire_y + 12.0), QPointF(x_feed, ground_y - 2.0))

        self._draw_centered_label(
            painter,
            QPointF(x_feed, wire_y - 22.0),
            self._translator.t("geometry.feed"),
            color=self._colors.feed,
        )

        if ground_y - wire_y > 26.0:
            if show_ends:
                self._draw_centered_label(
                    painter,
                    QPointF(x_left, wire_y + 15.0),
                    self._translator.t("geometry.end"),
                )
                self._draw_centered_label(
                    painter,
                    QPointF(x_right, wire_y + 15.0),
                    self._translator.t("geometry.end"),
                )
            if center_label:
                self._draw_centered_label(
                    painter,
                    QPointF(x_feed, ground_y - 14.0),
                    self._translator.t("geometry.center"),
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
        candidates = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0]
        max_pixels = max(self.width() * 0.45, 40.0)
        fitting = [value for value in candidates if value * px_per_display_unit <= max_pixels]
        if not fitting:
            fitting = [candidates[0]]
        ideal = min(fitting, key=lambda value: abs(value * px_per_display_unit - 110.0))
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
            QRectF(x_left - 65.0, bar_y - 10.0, 58.0, 20.0),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            self._translator.t("geometry.scale"),
        )
        self._draw_centered_label(
            painter,
            QPointF(x_left + bar_length / 2.0, bar_y - 10.0),
            f"{ideal:g} {unit}",
            font_size=8,
        )

    def _draw_compass(self, painter: QPainter, rect: QRectF, azimuth: float) -> None:
        center = QPointF(rect.right() - 48.0, rect.top() + 46.0)
        radius = 17.0
        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)
        painter.setFont(QFont("Sans Serif", 7))
        painter.setPen(self._colors.secondary_text)
        painter.drawText(
            QRectF(center.x() - 8.0, center.y() - radius - 14.0, 16.0, 12.0),
            Qt.AlignmentFlag.AlignCenter,
            "N",
        )
        painter.drawText(
            QRectF(center.x() + radius + 3.0, center.y() - 7.0, 12.0, 14.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "E",
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
        painter.drawText(
            QRectF(background),
            Qt.AlignmentFlag.AlignCenter,
            text,
        )

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

    def _draw_vertical_sketch(
        self,
        painter: QPainter,
        rect: QRectF,
        wire: Wire,
    ) -> None:
        base_z = min(wire.start.z_m, wire.end.z_m)
        top_z = max(wire.start.z_m, wire.end.z_m)
        length = wire.length_m
        if length <= 0.0:
            return
        feed_ratio = min(max(self._model.feed.offset_m / length, 0.0), 1.0)
        feed_z = wire.start.z_m + (wire.end.z_m - wire.start.z_m) * feed_ratio
        unit = self._translator.t(length_unit_key(self._unit_system))
        length_display = length_from_m(length, self._unit_system)
        base_display = length_from_m(base_z, self._unit_system)
        summary = self._translator.t(
            "geometry.summary",
            length=f"{length_display:.2f} {unit}",
            height=f"{base_display:.2f} {unit}",
            azimuth="—",
        )
        self._draw_header(painter, rect, summary)

        draw_rect = QRectF(
            rect.left() + 110.0,
            rect.top() + 74.0,
            rect.width() - 110.0 - 110.0,
            rect.height() - 74.0 - 84.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 60.0:
            return
        scale = (draw_rect.height() - 52.0) / max(top_z, 0.5) * self._zoom
        if scale <= 0.0:
            return
        ground_y = draw_rect.bottom()
        x_center = draw_rect.center().x()
        base_y = ground_y - base_z * scale
        top_y = ground_y - top_z * scale
        feed_y = ground_y - feed_z * scale

        self._draw_ground(painter, x_center - 70.0, x_center + 70.0, ground_y)

        if base_y < ground_y - 2.0:
            dim_x = x_center - 42.0
            painter.setPen(QPen(self._colors.light_line, 1.0))
            painter.drawLine(QPointF(x_center, base_y), QPointF(dim_x - 4.0, base_y))
            painter.drawLine(QPointF(dim_x, ground_y), QPointF(dim_x, base_y))
            painter.setPen(QPen(self._colors.dimension, 1.0))
            painter.drawLine(QPointF(dim_x, ground_y), QPointF(dim_x, base_y))
            self._draw_arrowhead(painter, QPointF(dim_x, base_y), QPointF(0.0, -1.0))
            self._draw_arrowhead(painter, QPointF(dim_x, ground_y), QPointF(0.0, 1.0))
            self._draw_centered_label(
                painter,
                QPointF(dim_x - 38.0, (ground_y + base_y) / 2.0),
                f"{base_display:.2f} {unit}",
            )

        dim_x = x_center + 54.0
        painter.setPen(QPen(self._colors.light_line, 1.0))
        painter.drawLine(QPointF(x_center, base_y), QPointF(dim_x + 4.0, base_y))
        painter.drawLine(QPointF(x_center, top_y), QPointF(dim_x + 4.0, top_y))
        painter.setPen(QPen(self._colors.dimension, 1.0))
        painter.drawLine(QPointF(dim_x, base_y), QPointF(dim_x, top_y))
        self._draw_arrowhead(painter, QPointF(dim_x, top_y), QPointF(0.0, -1.0))
        self._draw_arrowhead(painter, QPointF(dim_x, base_y), QPointF(0.0, 1.0))
        self._draw_rotated_label(
            painter,
            QPointF(dim_x + 12.0, (base_y + top_y) / 2.0),
            f"{length_display:.2f} {unit}",
            90.0,
        )

        gap = 9.0
        lower_end = feed_y + gap / 2.0
        upper_start = feed_y - gap / 2.0
        pen = QPen(self._colors.wire, 3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(x_center, base_y), QPointF(x_center, lower_end))
        painter.drawLine(QPointF(x_center, upper_start), QPointF(x_center, top_y))

        painter.setPen(QPen(self._colors.wire, 2.0))
        painter.drawLine(QPointF(x_center - 7.0, base_y), QPointF(x_center + 7.0, base_y))
        painter.drawLine(QPointF(x_center - 7.0, top_y), QPointF(x_center + 7.0, top_y))

        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.drawLine(QPointF(x_center - 8.0, lower_end), QPointF(x_center + 8.0, lower_end))
        painter.drawLine(QPointF(x_center - 8.0, upper_start), QPointF(x_center + 8.0, upper_start))
        painter.setBrush(self._colors.feed)
        painter.setPen(QPen(self._colors.feed, 1.0))
        painter.drawEllipse(QPointF(x_center + 15.0, feed_y), 3.0, 3.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        self._draw_centered_label(
            painter,
            QPointF(x_center + 30.0, feed_y),
            self._translator.t("geometry.feed"),
            color=self._colors.feed,
        )
        if abs(feed_ratio - 0.5) < 1e-9:
            self._draw_centered_label(
                painter,
                QPointF(x_center - 28.0, feed_y),
                self._translator.t("geometry.center"),
            )
        self._draw_centered_label(
            painter,
            QPointF(x_center - 24.0, base_y),
            self._translator.t("geometry.end"),
        )
        self._draw_centered_label(
            painter,
            QPointF(x_center - 24.0, top_y),
            self._translator.t("geometry.end"),
        )

        self._draw_scale_bar(
            painter,
            x_left=rect.left() + 110.0,
            bar_y=rect.bottom() - 42.0,
            scale=scale,
            unit=unit,
        )

    def _draw_vertical_plan_message(
        self,
        painter: QPainter,
        rect: QRectF,
        wire: Wire,
    ) -> None:
        height_m = max(wire.start.z_m, wire.end.z_m)
        unit = self._translator.t(length_unit_key(self._unit_system))
        summary = self._translator.t(
            "geometry.summary",
            length=f"{length_from_m(wire.length_m, self._unit_system):.2f} {unit}",
            height=f"{length_from_m(height_m, self._unit_system):.2f} {unit}",
            azimuth="—",
        )
        self._draw_header(painter, rect, summary)
        painter.setPen(self._colors.secondary_text)
        painter.setFont(QFont("Sans Serif", 9))
        painter.drawText(
            QRectF(rect.left(), rect.center().y(), rect.width(), 20.0),
            Qt.AlignmentFlag.AlignCenter,
            self._translator.t("geometry.vertical"),
        )
