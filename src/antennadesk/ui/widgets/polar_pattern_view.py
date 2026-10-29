# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Polar visualization of a far-field elevation cut."""

from __future__ import annotations

import math

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPaintEvent, QPen, QPolygonF
from PySide6.QtWidgets import QSizePolicy, QWidget

from ..i18n import Translator
from ..theme import theme_colors


class PolarPatternView(QWidget):
    def __init__(
        self,
        translator: Translator,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._points: tuple[tuple[float, float], ...] = ()
        self._colors = theme_colors(self.palette())
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def sizeHint(self) -> QSize:
        return QSize(420, 320)

    def set_points(self, points: tuple[tuple[float, float], ...]) -> None:
        self._points = points
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
        self._colors = theme_colors(self.palette())
        painter.fillRect(self.rect(), self._colors.background)
        rect = QRectF(self.rect())
        if rect.width() < 120.0 or rect.height() < 100.0:
            return

        points = [
            (theta, gain) for theta, gain in self._points if math.isfinite(gain) and gain > -100.0
        ]
        if len(points) < 2:
            painter.setPen(self._colors.secondary_text)
            painter.setFont(QFont("Sans Serif", 9))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._translator.t("pattern.none"))
            return

        gains = [gain for _, gain in points]
        min_gain = math.floor(min(gains) / 5.0) * 5.0
        max_gain = math.ceil(max(gains) / 5.0) * 5.0
        if max_gain <= min_gain:
            max_gain = min_gain + 5.0

        center = QPointF(rect.center().x(), rect.center().y() + 8.0)
        radius = min(rect.width() * 0.36, rect.height() * 0.42)
        if radius < 30.0:
            return

        painter.setFont(QFont("Sans Serif", 8))
        painter.setPen(QPen(self._colors.light_line, 1.0))
        for step in range(4):
            ratio = (step + 1) / 4.0
            ring = radius * ratio
            painter.drawEllipse(center, ring, ring)
        painter.setPen(QPen(self._colors.light_line, 1.0, Qt.PenStyle.DashLine))
        for angle_deg in range(0, 360, 30):
            angle = math.radians(angle_deg)
            end = QPointF(
                center.x() + math.sin(angle) * radius,
                center.y() - math.cos(angle) * radius,
            )
            painter.drawLine(center, end)
            label = QPointF(
                center.x() + math.sin(angle) * (radius + 15.0),
                center.y() - math.cos(angle) * (radius + 15.0),
            )
            self._draw_label(painter, label, f"{angle_deg}°")

        mirror = max(theta for theta, _ in points) <= 180.0
        if mirror:
            mirrored = [(-theta, gain) for theta, gain in points if theta > 0.0]
            points = points + mirrored

        def to_xy(theta_deg: float, gain: float) -> QPointF:
            ratio = (gain - min_gain) / (max_gain - min_gain)
            distance = radius * min(max(ratio, 0.0), 1.0)
            angle = math.radians(theta_deg)
            return QPointF(
                center.x() + math.sin(angle) * distance,
                center.y() - math.cos(angle) * distance,
            )

        polygon = QPolygonF([to_xy(theta, gain) for theta, gain in points])
        painter.setPen(QPen(self._colors.pattern, 2.0))
        painter.setBrush(
            QColor(
                self._colors.pattern.red(),
                self._colors.pattern.green(),
                self._colors.pattern.blue(),
                35,
            )
        )
        painter.drawPolygon(polygon)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        best_theta, best_gain = max(points, key=lambda item: item[1])
        best = to_xy(best_theta, best_gain)
        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.setBrush(self._colors.feed)
        painter.drawEllipse(best, 4.0, 4.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        self._draw_label(
            painter,
            QPointF(best.x() + 18.0, best.y() - 10.0),
            f"{best_gain:.2f} dBi",
            color=self._colors.feed,
        )

        painter.setPen(self._colors.secondary_text)
        painter.setFont(QFont("Sans Serif", 8))
        painter.drawText(
            QRectF(rect.left() + 14.0, rect.top() + 8.0, rect.width() - 28.0, 18.0),
            self._translator.t("pattern.polar"),
        )
        painter.drawText(
            QRectF(rect.left() + 14.0, rect.bottom() - 22.0, rect.width() - 28.0, 16.0),
            f"{self._translator.t('pattern.gain')}: {max_gain:g} dBi",
        )

    def _draw_label(
        self,
        painter: QPainter,
        center: QPointF,
        text: str,
        *,
        color: QColor | None = None,
    ) -> None:
        font = QFont("Sans Serif", 7)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        width = metrics.horizontalAdvance(text) + 6.0
        rect = QRectF(center.x() - width / 2.0, center.y() - 8.0, width, 16.0)
        painter.fillRect(rect, self._colors.background)
        painter.setPen(color or self._colors.secondary_text)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
