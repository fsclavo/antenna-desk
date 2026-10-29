# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction-sketch style geometry view for a wire antenna."""

from __future__ import annotations

import math
from enum import StrEnum

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QPainter,
    QPaintEvent,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import QSizePolicy, QWidget

from ...domain.antennas.antenna import AntennaModel
from ...domain.antennas.wire import Wire
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_unit_key

WIRE_COLOR = QColor("#1f5fa8")
FEED_COLOR = QColor("#c0392b")
DIMENSION_COLOR = QColor("#555555")
LIGHT_LINE_COLOR = QColor("#b8b8b8")
GROUND_COLOR = QColor("#777777")
TEXT_COLOR = QColor("#222222")
SECONDARY_TEXT_COLOR = QColor("#666666")
BACKGROUND_COLOR = QColor("#ffffff")


class GeometryViewMode(StrEnum):
    ELEVATION = "elevation"
    PLAN = "plan"


class GeometryView(QWidget):
    """A dimensioned side elevation that reads like a construction sketch."""

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
        self._mode = GeometryViewMode.ELEVATION
        self._height_exaggeration = 1.0
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def sizeHint(self) -> QSize:
        return QSize(700, 330)

    def minimumSizeHint(self) -> QSize:
        return QSize(360, 240)

    def set_model(self, model: AntennaModel | None) -> None:
        self._model = model
        self.update()

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

    def set_height_exaggeration(self, factor: float) -> None:
        if not math.isfinite(factor) or factor <= 0.0:
            raise ValueError("height exaggeration must be positive and finite")
        if math.isclose(factor, self._height_exaggeration):
            return
        self._height_exaggeration = factor
        self.update()

    def retranslate(self) -> None:
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.fillRect(self.rect(), BACKGROUND_COLOR)
        rect = QRectF(self.rect())
        if rect.width() < 120.0 or rect.height() < 80.0:
            return

        if self._model is None:
            self._draw_header(painter, rect, None)
            painter.setPen(SECONDARY_TEXT_COLOR)
            painter.setFont(QFont("Sans Serif", 10))
            painter.drawText(
                rect, Qt.AlignmentFlag.AlignCenter, self._translator.t("geometry.none")
            )
            return

        if self._mode is GeometryViewMode.PLAN:
            self._paint_plan(painter, rect)
        else:
            self._paint_elevation(painter, rect)

    def _paint_elevation(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        wire = self._model.wires[0]
        dx = wire.end.x_m - wire.start.x_m
        dy = wire.end.y_m - wire.start.y_m
        horizontal = math.hypot(dx, dy)
        if horizontal < 1e-9:
            self._draw_vertical_fallback(painter, rect, wire)
            return

        azimuth = math.degrees(math.atan2(dy, dx)) % 360.0
        height_m = (wire.start.z_m + wire.end.z_m) / 2.0
        length_display = length_from_m(horizontal, self._unit_system)
        height_display = length_from_m(height_m, self._unit_system)
        unit = self._translator.t(length_unit_key(self._unit_system))
        summary = self._translator.t(
            "geometry.summary",
            length=f"{length_display:.2f} {unit}",
            height=f"{height_display:.2f} {unit}",
            azimuth=f"{azimuth:.1f}",
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
        self._draw_compass(painter, rect, azimuth)
        feed_ratio = self._model.feed.offset_m / wire.length_m
        feed_ratio = min(max(feed_ratio, 0.0), 1.0)
        self._draw_horizontal_sketch(
            painter,
            rect,
            wire,
            horizontal=horizontal,
            height_m=height_m * self._height_exaggeration,
            length_display=length_display,
            height_display=height_display,
            feed_ratio=feed_ratio,
            unit=unit,
        )

    def _paint_plan(self, painter: QPainter, rect: QRectF) -> None:
        assert self._model is not None
        wire = self._model.wires[0]
        dx = wire.end.x_m - wire.start.x_m
        dy = wire.end.y_m - wire.start.y_m
        horizontal = math.hypot(dx, dy)
        if horizontal < 1e-9:
            self._draw_vertical_fallback(painter, rect, wire)
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
        scale = min(scale_candidates) if scale_candidates else 1.0
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

        painter.setPen(QPen(LIGHT_LINE_COLOR, 1.0, Qt.PenStyle.DashDotLine))
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

        pen = QPen(WIRE_COLOR, 3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(start, left_end)
        painter.drawLine(right_start, end)

        painter.setPen(QPen(WIRE_COLOR, 2.0))
        painter.drawLine(
            QPointF(start.x() - perp.x() * 7.0, start.y() - perp.y() * 7.0),
            QPointF(start.x() + perp.x() * 7.0, start.y() + perp.y() * 7.0),
        )
        painter.drawLine(
            QPointF(end.x() - perp.x() * 7.0, end.y() - perp.y() * 7.0),
            QPointF(end.x() + perp.x() * 7.0, end.y() + perp.y() * 7.0),
        )

        painter.setPen(QPen(FEED_COLOR, 2.0))
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
        painter.setBrush(FEED_COLOR)
        painter.setPen(QPen(FEED_COLOR, 1.0))
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
            color=FEED_COLOR,
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

        dim_offset = 30.0
        dim_start = QPointF(
            start.x() + dim_dir.x() * dim_offset,
            start.y() + dim_dir.y() * dim_offset,
        )
        dim_end = QPointF(
            end.x() + dim_dir.x() * dim_offset,
            end.y() + dim_dir.y() * dim_offset,
        )
        painter.setPen(QPen(LIGHT_LINE_COLOR, 1.0))
        painter.drawLine(start, dim_start)
        painter.drawLine(end, dim_end)
        painter.setPen(QPen(DIMENSION_COLOR, 1.0))
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

        self._draw_scale_bar(
            painter,
            x_left=rect.left() + 110.0,
            bar_y=rect.bottom() - 42.0,
            scale=scale,
            unit=unit,
        )

    def _draw_header(
        self,
        painter: QPainter,
        rect: QRectF,
        summary: str | None,
    ) -> None:
        painter.setPen(TEXT_COLOR)
        painter.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        painter.drawText(
            QRectF(rect.left() + 16.0, rect.top() + 8.0, rect.width() - 32.0, 20.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self._translator.t("panel.geometry"),
        )
        if summary is not None:
            painter.setPen(SECONDARY_TEXT_COLOR)
            painter.setFont(QFont("Sans Serif", 8))
            painter.drawText(
                QRectF(rect.left() + 16.0, rect.top() + 29.0, rect.width() - 32.0, 18.0),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                summary,
            )

    def _draw_horizontal_sketch(
        self,
        painter: QPainter,
        rect: QRectF,
        wire: Wire,
        *,
        horizontal: float,
        height_m: float,
        length_display: float,
        height_display: float,
        feed_ratio: float,
        unit: str,
    ) -> None:
        draw_rect = QRectF(
            rect.left() + 92.0,
            rect.top() + 84.0,
            rect.width() - 92.0 - 92.0,
            rect.height() - 84.0 - 82.0,
        )
        if draw_rect.width() < 80.0 or draw_rect.height() < 50.0:
            return

        z_max = max(height_m, 0.5)
        reserve_above = 58.0
        available_height = max(draw_rect.height() - reserve_above, 24.0)
        scale = min(
            draw_rect.width() / max(horizontal, 1e-9),
            available_height / z_max,
        )
        if scale <= 0.0:
            return

        ground_y = draw_rect.bottom()
        wire_y = ground_y - height_m * scale
        origin_x = draw_rect.center().x() - horizontal * scale / 2.0
        x_left = origin_x
        x_right = origin_x + horizontal * scale
        x_feed = x_left + (x_right - x_left) * feed_ratio
        gap = 9.0

        ground_left = x_left - 32.0
        ground_right = x_right + 32.0
        self._draw_ground(painter, ground_left, ground_right, ground_y)
        self._draw_height_dimension(
            painter,
            x_left=x_left,
            ground_y=ground_y,
            wire_y=wire_y,
            value=f"{height_display:.2f} {unit}",
        )
        self._draw_dimension_lines(
            painter,
            x_left=x_left,
            x_split=x_feed,
            x_right=x_right,
            wire_y=wire_y,
            total_value=f"{length_display:.2f} {unit}",
            left_value=f"{length_display * feed_ratio:.2f} {unit}",
            right_value=f"{length_display * (1.0 - feed_ratio):.2f} {unit}",
            gap=gap,
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
        )
        self._draw_scale_bar(
            painter,
            x_left=x_left,
            bar_y=ground_y + 40.0,
            scale=scale,
            unit=unit,
        )

    def _draw_ground(
        self,
        painter: QPainter,
        x_left: float,
        x_right: float,
        y: float,
    ) -> None:
        painter.setPen(QPen(GROUND_COLOR, 2.0))
        painter.drawLine(QPointF(x_left, y), QPointF(x_right, y))

        painter.setPen(QPen(LIGHT_LINE_COLOR, 1.0))
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
        painter.setPen(QPen(LIGHT_LINE_COLOR, 1.0))
        painter.drawLine(QPointF(x_left, wire_y), QPointF(dim_x - 4.0, wire_y))
        painter.drawLine(QPointF(x_left, ground_y), QPointF(dim_x - 4.0, ground_y))

        painter.setPen(QPen(DIMENSION_COLOR, 1.0))
        painter.drawLine(QPointF(dim_x, ground_y), QPointF(dim_x, wire_y))
        self._draw_arrowhead(painter, QPointF(dim_x, wire_y), QPointF(0.0, -1.0))
        self._draw_arrowhead(painter, QPointF(dim_x, ground_y), QPointF(0.0, 1.0))

        font = QFont("Sans Serif", 8)
        painter.setFont(font)
        text_rect = QRectF(dim_x - 78.0, (ground_y + wire_y) / 2.0 - 9.0, 68.0, 18.0)
        painter.fillRect(text_rect.adjusted(-2.0, 0.0, 2.0, 0.0), BACKGROUND_COLOR)
        painter.setPen(TEXT_COLOR)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            value,
        )

    def _draw_dimension_lines(
        self,
        painter: QPainter,
        *,
        x_left: float,
        x_split: float,
        x_right: float,
        wire_y: float,
        total_value: str,
        left_value: str,
        right_value: str,
        gap: float,
    ) -> None:
        total_y = wire_y - 58.0
        leg_y = wire_y - 30.0

        painter.setPen(QPen(LIGHT_LINE_COLOR, 1.0))
        painter.drawLine(QPointF(x_left, wire_y), QPointF(x_left, total_y - 3.0))
        painter.drawLine(QPointF(x_right, wire_y), QPointF(x_right, total_y - 3.0))
        painter.drawLine(QPointF(x_split, wire_y), QPointF(x_split, leg_y - 3.0))

        painter.setPen(QPen(DIMENSION_COLOR, 1.0))
        painter.drawLine(QPointF(x_left, total_y), QPointF(x_right, total_y))
        self._draw_arrowhead(painter, QPointF(x_left, total_y), QPointF(-1.0, 0.0))
        self._draw_arrowhead(painter, QPointF(x_right, total_y), QPointF(1.0, 0.0))
        self._draw_centered_label(
            painter,
            QPointF((x_left + x_right) / 2.0, total_y - 9.0),
            total_value,
        )

        leg_left_end = x_split - gap / 2.0
        leg_right_start = x_split + gap / 2.0
        if leg_left_end - x_left > 36.0:
            painter.drawLine(QPointF(x_left, leg_y), QPointF(leg_left_end, leg_y))
            self._draw_arrowhead(painter, QPointF(x_left, leg_y), QPointF(-1.0, 0.0))
            self._draw_arrowhead(painter, QPointF(leg_left_end, leg_y), QPointF(1.0, 0.0))
            self._draw_centered_label(
                painter,
                QPointF((x_left + leg_left_end) / 2.0, leg_y - 9.0),
                left_value,
            )
        if x_right - leg_right_start > 36.0:
            painter.drawLine(QPointF(leg_right_start, leg_y), QPointF(x_right, leg_y))
            self._draw_arrowhead(painter, QPointF(leg_right_start, leg_y), QPointF(-1.0, 0.0))
            self._draw_arrowhead(painter, QPointF(x_right, leg_y), QPointF(1.0, 0.0))
            self._draw_centered_label(
                painter,
                QPointF((leg_right_start + x_right) / 2.0, leg_y - 9.0),
                right_value,
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
    ) -> None:
        pen = QPen(WIRE_COLOR, 3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(x_left, wire_y), QPointF(x_feed - gap / 2.0, wire_y))
        painter.drawLine(QPointF(x_feed + gap / 2.0, wire_y), QPointF(x_right, wire_y))

        painter.setPen(QPen(WIRE_COLOR, 2.0))
        painter.drawLine(QPointF(x_left, wire_y - 7.0), QPointF(x_left, wire_y + 7.0))
        painter.drawLine(QPointF(x_right, wire_y - 7.0), QPointF(x_right, wire_y + 7.0))

        painter.setPen(QPen(FEED_COLOR, 2.0))
        painter.drawLine(
            QPointF(x_feed - gap / 2.0, wire_y - 8.0),
            QPointF(x_feed - gap / 2.0, wire_y + 8.0),
        )
        painter.drawLine(
            QPointF(x_feed + gap / 2.0, wire_y - 8.0),
            QPointF(x_feed + gap / 2.0, wire_y + 8.0),
        )
        painter.setBrush(FEED_COLOR)
        painter.setPen(QPen(FEED_COLOR, 1.0))
        painter.drawEllipse(QPointF(x_feed, wire_y - 12.0), 3.0, 3.0)

        centerline_pen = QPen(LIGHT_LINE_COLOR, 1.0, Qt.PenStyle.DashDotLine)
        painter.setPen(centerline_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(QPointF(x_feed, wire_y + 12.0), QPointF(x_feed, ground_y - 2.0))

        self._draw_centered_label(
            painter,
            QPointF(x_feed, wire_y - 22.0),
            self._translator.t("geometry.feed"),
            color=FEED_COLOR,
        )

        if ground_y - wire_y > 26.0:
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

        painter.setPen(QPen(DIMENSION_COLOR, 1.0))
        painter.drawLine(QPointF(x_left, bar_y), QPointF(x_left + bar_length, bar_y))
        painter.drawLine(QPointF(x_left, bar_y - 5.0), QPointF(x_left, bar_y + 5.0))
        painter.drawLine(
            QPointF(x_left + bar_length, bar_y - 5.0),
            QPointF(x_left + bar_length, bar_y + 5.0),
        )
        painter.setFont(QFont("Sans Serif", 8))
        painter.setPen(SECONDARY_TEXT_COLOR)
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
        painter.setPen(QPen(LIGHT_LINE_COLOR, 1.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)
        painter.setFont(QFont("Sans Serif", 7))
        painter.setPen(SECONDARY_TEXT_COLOR)
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
        painter.setPen(QPen(WIRE_COLOR, 2.0))
        painter.drawLine(center, end)
        painter.setBrush(WIRE_COLOR)
        painter.drawEllipse(end, 2.5, 2.5)

    def _draw_centered_label(
        self,
        painter: QPainter,
        center: QPointF,
        text: str,
        *,
        color: QColor = TEXT_COLOR,
        font_size: int = 8,
    ) -> None:
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
        painter.fillRect(background, BACKGROUND_COLOR)
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
        color: QColor = TEXT_COLOR,
        font_size: int = 8,
    ) -> None:
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
        painter.fillRect(background, BACKGROUND_COLOR)
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
        painter.setBrush(DIMENSION_COLOR)
        painter.drawPolygon(polygon)
        painter.setBrush(Qt.BrushStyle.NoBrush)

    def _draw_vertical_fallback(
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
        painter.setPen(SECONDARY_TEXT_COLOR)
        painter.setFont(QFont("Sans Serif", 9))
        painter.drawText(
            QRectF(rect.left(), rect.center().y(), rect.width(), 20.0),
            Qt.AlignmentFlag.AlignCenter,
            self._translator.t("geometry.vertical"),
        )
