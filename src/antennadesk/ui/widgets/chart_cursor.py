# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reusable hover cursor for pyqtgraph result charts."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import pyqtgraph as pg
from PySide6.QtCore import QEvent, QObject, QPointF, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel


@dataclass(frozen=True, slots=True)
class CursorSeries:
    """One plotted series that can be inspected by the cursor."""

    label: str
    x_values: tuple[float, ...]
    y_values: tuple[float, ...]
    color: QColor
    unit: str = ""
    show_marker: bool = True


ReadoutBuilder = Callable[[float, tuple[tuple[str, float], ...]], str]


def nearest_index(
    x_values: Sequence[float],
    x: float,
    *,
    wrap_period: float | None = None,
) -> int | None:
    """Return the index of the x value closest to ``x``.

    ``wrap_period`` handles cyclic axes such as azimuth angles.
    """

    if not x_values:
        return None
    best_index = 0
    best_distance = math.inf
    for index, value in enumerate(x_values):
        distance = abs(value - x)
        if wrap_period is not None and wrap_period > 0.0:
            distance = min(distance, abs(distance - wrap_period), abs(distance + wrap_period))
        if distance < best_distance:
            best_distance = distance
            best_index = index
    return best_index


class ChartCursor(QObject):
    """Vertical cursor with nearest-point markers and a floating readout."""

    def __init__(
        self,
        plot: pg.PlotWidget,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent or plot)
        self._plot = plot
        self._series: tuple[CursorSeries, ...] = ()
        self._readout_builder: ReadoutBuilder | None = None
        self._wrap_period: float | None = None
        self._text_color = QColor("#222222")
        self._background = QColor("#ffffff")
        self._line_color = QColor("#666666")
        self._label = QLabel(plot)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._label.setVisible(False)
        self._label.setMargin(4)
        self._line = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen=pg.mkPen(self._line_color, width=1, style=Qt.PenStyle.DashLine),
            label=None,
        )
        self._line.setVisible(False)
        self._line.setZValue(100)
        self._dots: list[pg.ScatterPlotItem] = []
        self._proxy = pg.SignalProxy(
            self._plot.scene().sigMouseMoved,
            rateLimit=30,
            slot=self._mouse_moved,
        )
        self._plot.viewport().installEventFilter(self)
        self._apply_label_style()

    def set_colors(
        self,
        *,
        text: QColor,
        background: QColor,
        line: QColor,
    ) -> None:
        self._text_color = QColor(text)
        self._background = QColor(background)
        self._line_color = QColor(line)
        self._line.setPen(pg.mkPen(self._line_color, width=1, style=Qt.PenStyle.DashLine))
        self._apply_label_style()

    def _apply_label_style(self) -> None:
        self._label.setStyleSheet(
            "QLabel {"
            f"color: {self._text_color.name()};"
            f"background-color: {self._background.name()};"
            "border: 1px solid #808080;"
            "border-radius: 3px;"
            "padding: 2px 5px;"
            "}"
        )

    def set_series(
        self,
        series: Sequence[CursorSeries],
        *,
        readout_builder: ReadoutBuilder | None = None,
        wrap_period: float | None = None,
    ) -> None:
        self.clear_markers()
        self._series = tuple(
            CursorSeries(
                label=item.label,
                x_values=tuple(item.x_values),
                y_values=tuple(item.y_values),
                color=QColor(item.color),
                unit=item.unit,
                show_marker=item.show_marker,
            )
            for item in series
            if item.x_values and item.y_values
        )
        self._readout_builder = readout_builder
        self._wrap_period = wrap_period
        if not self._series:
            return
        self._attach_items()

    def _attach_items(self) -> None:
        plot_item = self._plot.getPlotItem()
        if self._line.scene() is None:
            plot_item.addItem(self._line, ignoreBounds=True)
        for item in self._series:
            if not item.show_marker:
                continue
            dot = pg.ScatterPlotItem(
                size=7,
                pen=pg.mkPen(item.color, width=1),
                brush=pg.mkBrush(item.color),
            )
            dot.setZValue(101)
            plot_item.addItem(dot, ignoreBounds=True)
            self._dots.append(dot)

    def clear_markers(self) -> None:
        for dot in self._dots:
            scene = dot.scene()
            if scene is not None:
                scene.removeItem(dot)
        self._dots.clear()
        self._line.setVisible(False)
        self._label.setVisible(False)

    def clear(self) -> None:
        self._series = ()
        self._readout_builder = None
        self.clear_markers()

    def hide_cursor(self) -> None:
        self._line.setVisible(False)
        for dot in self._dots:
            dot.setVisible(False)
        self._label.setVisible(False)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        try:
            if watched is self._plot.viewport() and event.type() == QEvent.Type.Leave:
                self.hide_cursor()
        except RuntimeError:
            return False
        return super().eventFilter(watched, event)

    def _mouse_moved(self, event: object) -> None:
        if not self._series:
            return
        position = event[0] if isinstance(event, tuple) else event
        if not isinstance(position, QPointF):
            return
        plot_item = self._plot.getPlotItem()
        if not plot_item.vb.sceneBoundingRect().contains(position):
            self.hide_cursor()
            return
        view_position = plot_item.vb.mapSceneToView(position)
        self.show_at_x(view_position.x(), mouse_position=position)

    def show_at_x(
        self,
        x: float,
        *,
        mouse_position: QPointF | None = None,
    ) -> None:
        if not self._series:
            return
        primary = self._series[0]
        primary_index = nearest_index(
            primary.x_values,
            x,
            wrap_period=self._wrap_period,
        )
        if primary_index is None:
            self.hide_cursor()
            return
        cursor_x = primary.x_values[primary_index]
        values: list[tuple[str, float]] = []
        self._line.setPos(cursor_x)
        self._line.setVisible(True)

        marker_index = 0
        for series in self._series:
            index = nearest_index(
                series.x_values,
                cursor_x,
                wrap_period=self._wrap_period,
            )
            if index is None:
                continue
            values.append((series.label, series.y_values[index]))
            if series.show_marker and marker_index < len(self._dots):
                self._dots[marker_index].setData(
                    [series.x_values[index]],
                    [series.y_values[index]],
                )
                self._dots[marker_index].setVisible(True)
                marker_index += 1

        if self._readout_builder is not None:
            text = self._readout_builder(cursor_x, tuple(values))
        else:
            text = f"{cursor_x:g}"
            if values:
                text += " · " + " · ".join(f"{label}: {value:.4g}" for label, value in values)
        self._label.setText(text)
        self._label.adjustSize()
        self._position_label(mouse_position)
        self._label.setVisible(True)

    def _position_label(self, mouse_position: QPointF | None) -> None:
        if mouse_position is None:
            anchor = self._plot.rect().center()
        else:
            anchor = self._plot.mapFromScene(mouse_position)
        x = anchor.x() + 16
        y = anchor.y() + 16
        width = self._label.width()
        height = self._label.height()
        rect = self._plot.rect()
        if x + width > rect.right() - 6:
            x = anchor.x() - width - 16
        if y + height > rect.bottom() - 6:
            y = anchor.y() - height - 16
        x = max(rect.left() + 6, x)
        y = max(rect.top() + 6, y)
        self._label.move(x, y)
