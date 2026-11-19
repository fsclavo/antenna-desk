# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Smith-chart rendering for the impedance locus."""

from __future__ import annotations

import math
from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QFont, QImage, QMouseEvent, QPainter, QPaintEvent, QPen, QPolygonF
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QApplication, QSizePolicy, QWidget

from ...domain.design.smith_chart import (
    SmithPoint,
    constant_reactance_arc_points,
    constant_resistance_circle_points,
)
from ..fonts import scaled_font
from ..i18n import Translator
from ..theme import theme_colors

_RESISTANCE_GRID = (0.2, 0.5, 1.0, 2.0, 5.0)
_REACTANCE_GRID = (0.2, 0.5, 1.0, 2.0, 5.0)
_DRAW_LIMIT = 700
_HOVER_RADIUS_PX = 16.0


class SmithChartView(QWidget):
    """Draw a normalized impedance locus and its reference-plane markers.

    The widget receives :class:`SmithPoint` values from the domain layer.  It
    never normalizes, transforms, or otherwise calculates an impedance itself.
    """

    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._simulated: tuple[SmithPoint, ...] = ()
        self._measured: tuple[SmithPoint, ...] = ()
        self._reference_impedance_ohm = 50.0
        self._plane_label = ""
        self._measured_note = ""
        self._selected_frequency_hz: float | None = None
        self._hover: tuple[bool, int] | None = None
        self._colors = theme_colors(self.palette())
        self.setMouseTracking(True)
        self.setMinimumSize(260, 260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.fontChanged.connect(self._on_application_font_changed)

    def _on_application_font_changed(self, font: QFont) -> None:
        del font
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(520, 520)

    def set_data(
        self,
        simulated: Sequence[SmithPoint],
        *,
        measured: Sequence[SmithPoint] = (),
        reference_impedance_ohm: float = 50.0,
        plane_label: str = "",
        measured_note: str = "",
    ) -> None:
        self._simulated = tuple(simulated)
        self._measured = tuple(measured)
        self._reference_impedance_ohm = reference_impedance_ohm
        self._plane_label = plane_label
        self._measured_note = measured_note
        if self._selected_frequency_hz is None and self._simulated:
            self._selected_frequency_hz = self._simulated[0].frequency_hz
        self._hover = None
        self.update()

    def set_selected_frequency(self, frequency_hz: float | None) -> None:
        self._selected_frequency_hz = frequency_hz
        self.update()

    def simulated_points(self) -> tuple[SmithPoint, ...]:
        return self._simulated

    def measured_points(self) -> tuple[SmithPoint, ...]:
        return self._measured

    def retranslate(self) -> None:
        self.update()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.PaletteChange:
            self._colors = theme_colors(self.palette())
            self.update()
        super().changeEvent(event)

    def clear(self) -> None:
        self._simulated = ()
        self._measured = ()
        self._selected_frequency_hz = None
        self._hover = None
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        rect = self._plot_rect()
        radius = self._radius(rect)
        center = rect.center()
        if radius <= 0.0:
            self._hover = None
            self.update()
            return
        position = event.position()
        gamma = complex(
            (position.x() - center.x()) / radius,
            (center.y() - position.y()) / radius,
        )
        self._hover = self._nearest(gamma, rect)
        self.update()

    def leaveEvent(self, event: QEvent) -> None:
        self._hover = None
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self._colors = theme_colors(self.palette())
        self._paint(painter, QRectF(self.rect()))
        painter.end()

    def save_image(self, path: Path) -> None:
        """Write a deterministic PNG or SVG image."""

        suffix = path.suffix.lower()
        if suffix not in {".png", ".svg"}:
            raise ValueError("Smith chart export requires a .png or .svg suffix")
        if suffix == ".svg":
            generator = QSvgGenerator()
            generator.setFileName(str(path))
            generator.setSize(QSize(1200, 900))
            generator.setViewBox(QRectF(0.0, 0.0, 1200.0, 900.0))
            generator.setTitle(self._translator.t("plot.smith"))
            painter = QPainter(generator)
            try:
                painter.fillRect(QRectF(0.0, 0.0, 1200.0, 900.0), self._colors.background)
                self._paint(painter, QRectF(0.0, 0.0, 1200.0, 900.0))
            finally:
                painter.end()
            return
        image = QImage(1200, 900, QImage.Format.Format_ARGB32)
        image.fill(self._colors.background)
        painter = QPainter(image)
        try:
            self._paint(painter, QRectF(0.0, 0.0, 1200.0, 900.0))
        finally:
            painter.end()
        if not image.save(str(path)):
            raise OSError(f"could not write Smith chart image: {path}")

    def _paint(self, painter: QPainter, rect: QRectF) -> None:
        painter.fillRect(rect, self._colors.background)
        title = self._translator.t("plot.smith")
        painter.setFont(scaled_font(11, QFont.Weight.Bold))
        painter.setPen(self._colors.text)
        painter.drawText(
            QRectF(rect.left() + 12.0, rect.top() + 6.0, rect.width() - 24.0, 24.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            title,
        )
        if not self._simulated:
            painter.setFont(scaled_font(9))
            painter.setPen(self._colors.secondary_text)
            painter.drawText(
                rect.adjusted(12.0, 36.0, -12.0, -12.0),
                Qt.AlignmentFlag.AlignCenter,
                self._translator.t("smith.no_data"),
            )
            return

        plot_rect = self._plot_rect()
        radius = self._radius(plot_rect)
        if radius <= 20.0:
            return
        center = plot_rect.center()
        self._draw_grid(painter, center, radius)
        self._draw_measured(painter, center, radius)
        self._draw_simulated(painter, center, radius)
        self._draw_target(painter, center, radius)
        self._draw_selected(painter, center, radius)
        self._draw_hover(painter, center, radius)
        self._draw_legend(painter, rect, plot_rect)

    def _draw_grid(self, painter: QPainter, center: QPointF, radius: float) -> None:
        painter.setPen(QPen(self._colors.light_line, 0.8))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)
        painter.setPen(QPen(self._colors.grid, 1.0))
        painter.drawLine(
            self._to_screen(complex(-1.0, 0.0), center, radius),
            self._to_screen(complex(1.0, 0.0), center, radius),
        )

        painter.setPen(QPen(self._colors.light_line, 0.7))
        painter.setFont(scaled_font(7))
        for resistance in _RESISTANCE_GRID:
            points = constant_resistance_circle_points(resistance, count=121)
            painter.drawPolyline(
                QPolygonF([self._to_screen(point, center, radius) for point in points])
            )
            gamma = complex((resistance - 1.0) / (resistance + 1.0), 0.0)
            label = self._to_screen(gamma, center, radius)
            painter.setPen(self._colors.secondary_text)
            painter.drawText(
                QRectF(label.x() - 18.0, label.y() + 3.0, 36.0, 14.0),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                f"{resistance:g}",
            )
            painter.setPen(QPen(self._colors.light_line, 0.7))

        painter.setPen(QPen(self._colors.light_line, 0.7, Qt.PenStyle.DotLine))
        for reactance in _REACTANCE_GRID:
            for value in (reactance, -reactance):
                points = constant_reactance_arc_points(value, count=121)
                painter.drawPolyline(
                    QPolygonF([self._to_screen(point, center, radius) for point in points])
                )
                first = points[0]
                label = self._to_screen(first, center, radius)
                painter.setPen(self._colors.secondary_text)
                painter.drawText(
                    QRectF(label.x() - 14.0, label.y() - 15.0, 28.0, 13.0),
                    Qt.AlignmentFlag.AlignCenter,
                    f"{value:+g}j",
                )
                painter.setPen(QPen(self._colors.light_line, 0.7, Qt.PenStyle.DotLine))

        painter.setPen(self._colors.secondary_text)
        painter.setFont(scaled_font(8))
        painter.drawText(
            QRectF(center.x() - 60.0, center.y() + radius + 4.0, 120.0, 16.0),
            Qt.AlignmentFlag.AlignCenter,
            self._translator.t("smith.axis_hint"),
        )

    def _draw_simulated(self, painter: QPainter, center: QPointF, radius: float) -> None:
        points = _decimated(self._simulated, _DRAW_LIMIT)
        if len(points) >= 2:
            painter.setPen(QPen(self._colors.resistance, 2.0))
            painter.drawPolyline(
                QPolygonF([self._to_screen(point.gamma, center, radius) for point in points])
            )
        painter.setPen(QPen(self._colors.resistance, 0.8))
        painter.setBrush(self._colors.resistance)
        for point in points:
            screen = self._to_screen(point.gamma, center, radius)
            painter.drawEllipse(screen, 1.8, 1.8)

    def _draw_measured(self, painter: QPainter, center: QPointF, radius: float) -> None:
        if not self._measured:
            return
        points = _decimated(self._measured, _DRAW_LIMIT)
        if len(points) >= 2:
            painter.setPen(
                QPen(
                    self._colors.reactance,
                    1.4,
                    Qt.PenStyle.DashLine,
                )
            )
            painter.drawPolyline(
                QPolygonF([self._to_screen(point.gamma, center, radius) for point in points])
            )
        painter.setPen(QPen(self._colors.reactance, 1.0))
        painter.setBrush(self._colors.reactance)
        for point in points:
            screen = self._to_screen(point.gamma, center, radius)
            painter.drawEllipse(screen, 2.0, 2.0)

    def _draw_target(self, painter: QPainter, center: QPointF, radius: float) -> None:
        target = self._to_screen(complex(0.0, 0.0), center, radius)
        painter.setPen(QPen(self._colors.feed, 1.2))
        painter.drawLine(
            QPointF(target.x() - 5.0, target.y()),
            QPointF(target.x() + 5.0, target.y()),
        )
        painter.drawLine(
            QPointF(target.x(), target.y() - 5.0),
            QPointF(target.x(), target.y() + 5.0),
        )
        painter.setFont(scaled_font(7))
        painter.setPen(self._colors.secondary_text)
        painter.drawText(
            QRectF(target.x() + 7.0, target.y() - 14.0, 60.0, 12.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self._translator.t("smith.target"),
        )

    def _draw_selected(self, painter: QPainter, center: QPointF, radius: float) -> None:
        point = self._selected_point()
        if point is None:
            return
        screen = self._to_screen(point.gamma, center, radius)
        painter.setPen(QPen(self._colors.pattern, 2.0))
        painter.setBrush(self._colors.background)
        painter.drawEllipse(screen, 5.0, 5.0)
        painter.setBrush(self._colors.pattern)
        painter.drawEllipse(screen, 2.4, 2.4)

    def _draw_hover(self, painter: QPainter, center: QPointF, radius: float) -> None:
        if self._hover is None:
            return
        measured, index = self._hover
        points = self._measured if measured else self._simulated
        if not 0 <= index < len(points):
            return
        point = points[index]
        screen = self._to_screen(point.gamma, center, radius)
        painter.setPen(QPen(self._colors.text, 1.0, Qt.PenStyle.DotLine))
        painter.setBrush(self._colors.text)
        painter.drawEllipse(screen, 2.5, 2.5)
        text = self._hover_text(point)
        metrics = painter.fontMetrics()
        width = max(metrics.horizontalAdvance(line) for line in text.splitlines()) + 12.0
        height = metrics.height() * len(text.splitlines()) + 8.0
        left = screen.x() + 10.0
        top = screen.y() - height - 8.0
        if left + width > self.width() - 8.0:
            left = screen.x() - width - 10.0
        if top < 8.0:
            top = screen.y() + 10.0
        box = QRectF(left, top, width, height)
        painter.setPen(QPen(self._colors.grid, 1.0))
        painter.setBrush(self._colors.background)
        painter.drawRect(box)
        painter.setPen(self._colors.text)
        painter.setFont(scaled_font(8))
        painter.drawText(
            box.adjusted(5.0, 3.0, -5.0, -3.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            text,
        )

    def _draw_legend(self, painter: QPainter, rect: QRectF, plot_rect: QRectF) -> None:
        painter.setFont(scaled_font(8))
        x = rect.left() + 14.0
        y = rect.top() + 34.0
        painter.setPen(QPen(self._colors.resistance, 2.0))
        painter.drawLine(QPointF(x, y), QPointF(x + 18.0, y))
        painter.setPen(self._colors.secondary_text)
        painter.drawText(
            QRectF(x + 24.0, y - 8.0, 130.0, 16.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self._translator.t("smith.legend_simulated"),
        )
        if self._measured:
            y += 15.0
            painter.setPen(QPen(self._colors.reactance, 1.4, Qt.PenStyle.DashLine))
            painter.drawLine(QPointF(x, y), QPointF(x + 18.0, y))
            painter.setPen(self._colors.secondary_text)
            painter.drawText(
                QRectF(x + 24.0, y - 8.0, 130.0, 16.0),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                self._translator.t("smith.legend_measured"),
            )
        summary = self._translator.t(
            "smith.summary",
            z0=f"{self._reference_impedance_ohm:g}",
            count=len(self._simulated),
            plane=self._plane_label,
        )
        painter.setPen(self._colors.secondary_text)
        painter.drawText(
            QRectF(
                plot_rect.left(),
                rect.bottom() - 22.0,
                rect.width() - 28.0,
                16.0,
            ),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            summary,
        )
        if self._measured_note:
            painter.drawText(
                QRectF(
                    plot_rect.left(),
                    rect.bottom() - 38.0,
                    rect.width() - 28.0,
                    16.0,
                ),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                self._measured_note,
            )

    def _plot_rect(self) -> QRectF:
        rect = QRectF(self.rect())
        top = 52.0
        bottom = 54.0
        available = max(min(rect.width() - 24.0, rect.height() - top - bottom), 0.0)
        left = (rect.width() - available) / 2.0
        return QRectF(left, top, available, available)

    @staticmethod
    def _radius(rect: QRectF) -> float:
        return max(min(rect.width(), rect.height()) / 2.0 - 8.0, 0.0)

    @staticmethod
    def _to_screen(gamma: complex, center: QPointF, radius: float) -> QPointF:
        return QPointF(
            center.x() + gamma.real * radius,
            center.y() - gamma.imag * radius,
        )

    def _selected_point(self) -> SmithPoint | None:
        if not self._simulated:
            return None
        selected = self._selected_frequency_hz
        if selected is None:
            return self._simulated[0]
        return min(
            self._simulated,
            key=lambda point: abs(point.frequency_hz - selected),
        )

    def _nearest(self, gamma: complex, rect: QRectF) -> tuple[bool, int] | None:
        radius = self._radius(rect)
        center = rect.center()
        target = self._to_screen(gamma, center, radius)
        best: tuple[bool, int] | None = None
        best_distance = _HOVER_RADIUS_PX
        for measured, points in ((False, self._simulated), (True, self._measured)):
            for index, point in enumerate(points):
                screen = self._to_screen(point.gamma, center, radius)
                distance = math.hypot(screen.x() - target.x(), screen.y() - target.y())
                if distance <= best_distance:
                    best_distance = distance
                    best = (measured, index)
        return best

    def _hover_text(self, point: SmithPoint) -> str:
        return "\n".join(
            (
                f"{point.frequency_hz / 1e6:.6f} MHz",
                f"R {point.impedance_ohm.real:.3f} Ω",
                f"X {point.impedance_ohm.imag:+.3f} Ω",
                f"|Γ| {point.gamma_magnitude:.3f}",
                f"SWR {point.swr:.3f}" if math.isfinite(point.swr) else "SWR ∞",
            )
        )


def _decimated(points: Sequence[SmithPoint], limit: int) -> tuple[SmithPoint, ...]:
    if len(points) <= limit or limit <= 0:
        return tuple(points)
    if limit == 1:
        return (points[len(points) // 2],)
    indices = sorted({round(index * (len(points) - 1) / (limit - 1)) for index in range(limit)})
    return tuple(points[index] for index in indices)
