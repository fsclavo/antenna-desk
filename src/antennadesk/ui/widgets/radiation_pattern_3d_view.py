# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Isometric 3D radiation-pattern wireframe."""

from __future__ import annotations

import math

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPaintEvent, QPen, QWheelEvent
from PySide6.QtWidgets import QSizePolicy, QWidget

from ..i18n import Translator
from ..theme import theme_colors


class RadiationPattern3DView(QWidget):
    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._points: tuple[tuple[float, float, float], ...] = ()
        self._ground = False
        self._yaw_deg = 38.0
        self._pitch_deg = 26.0
        self._zoom = 1.0
        self._dragging = False
        self._last_pos = QPointF(0.0, 0.0)
        self._colors = theme_colors(self.palette())
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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
        self._ground = ground
        self.update()

    def reset_view(self) -> None:
        self._yaw_deg = 38.0
        self._pitch_deg = 26.0
        self._zoom = 1.0
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_pos = event.position()
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
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._dragging and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.reset_view()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        if delta == 0:
            return
        self._zoom = min(max(self._zoom * (1.1 if delta > 0 else 1.0 / 1.1), 0.5), 4.0)
        self.update()
        event.accept()

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
        if rect.width() < 160.0 or rect.height() < 120.0:
            return

        points = [
            (theta, phi, gain)
            for theta, phi, gain in self._points
            if math.isfinite(gain) and gain > -100.0
        ]
        if len(points) < 4:
            painter.setPen(self._colors.secondary_text)
            painter.setFont(QFont("Sans Serif", 9))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._translator.t("pattern.none"))
            return

        gains = [gain for _, _, gain in points]
        min_gain = min(gains)
        max_gain = max(gains)
        if math.isclose(max_gain, min_gain):
            max_gain = min_gain + 1.0

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

        projected = [project(theta, phi, gain) for theta, phi, gain in points]
        min_px = min(point[0] for point in projected)
        max_px = max(point[0] for point in projected)
        min_py = min(point[1] for point in projected)
        max_py = max(point[1] for point in projected)
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

        theta_values = sorted({theta for theta, _, _ in points})
        phi_values = sorted({phi for _, phi, _ in points})
        gain_by_coord = {(round(theta, 6), round(phi, 6)): gain for theta, phi, gain in points}

        pen = QPen(
            QColor(
                self._colors.pattern.red(),
                self._colors.pattern.green(),
                self._colors.pattern.blue(),
                110,
            ),
            1.0,
        )
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for phi in phi_values:
            previous: QPointF | None = None
            for theta in theta_values:
                gain = gain_by_coord.get((round(theta, 6), round(phi, 6)))
                if gain is None:
                    previous = None
                    continue
                current = screen(theta, phi, gain)
                if previous is not None:
                    painter.drawLine(previous, current)
                previous = current
        for theta in theta_values:
            previous = None
            for phi in phi_values:
                gain = gain_by_coord.get((round(theta, 6), round(phi, 6)))
                if gain is None:
                    previous = None
                    continue
                current = screen(theta, phi, gain)
                if previous is not None:
                    painter.drawLine(previous, current)
                previous = current

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
            painter.setFont(QFont("Sans Serif", 7))
            label = screen_world(0.0, -0.88, 0.0)
            painter.drawText(
                QRectF(label.x() - 30.0, label.y() + 4.0, 60.0, 14.0),
                Qt.AlignmentFlag.AlignCenter,
                self._translator.t("pattern.ground"),
            )

        max_point = max(points, key=lambda item: item[2])
        marker = screen(*max_point)
        painter.setPen(QPen(self._colors.feed, 2.0))
        painter.setBrush(self._colors.feed)
        painter.drawEllipse(marker, 3.5, 3.5)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setFont(QFont("Sans Serif", 8))
        painter.setPen(self._colors.feed)
        painter.drawText(
            QRectF(marker.x() + 8.0, marker.y() - 16.0, 100.0, 16.0),
            f"{max_point[2]:.2f} dBi",
        )

        origin = screen(0.0, 0.0, min_gain)
        painter.setPen(QPen(self._colors.axis, 1.5))
        for theta, phi, label in ((90.0, 0.0, "X"), (90.0, 90.0, "Y"), (0.0, 0.0, "Z")):
            end = screen(theta, phi, max_gain)
            painter.drawLine(origin, end)
            painter.setFont(QFont("Sans Serif", 7))
            painter.setPen(self._colors.secondary_text)
            painter.drawText(
                QRectF(end.x() + 4.0, end.y() - 8.0, 16.0, 16.0),
                label,
            )

        painter.setPen(self._colors.secondary_text)
        painter.setFont(QFont("Sans Serif", 8))
        painter.drawText(
            QRectF(rect.left() + 14.0, rect.top() + 8.0, rect.width() - 28.0, 18.0),
            self._translator.t("pattern.3d_polar"),
        )
        painter.drawText(
            QRectF(rect.left() + 14.0, rect.bottom() - 22.0, rect.width() - 28.0, 16.0),
            self._translator.t("pattern.3d_hint"),
        )
