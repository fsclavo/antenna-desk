# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Basic 2D geometry view for a single-wire antenna."""

from __future__ import annotations

import math

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ...domain.antennas.antenna import AntennaModel
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_unit_key


class GeometryView(QWidget):
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

        self._plot = pg.PlotWidget(self)
        self._plot.setBackground("w")
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.setAspectLocked(True)
        for axis in ("left", "bottom"):
            self._plot.getAxis(axis).setPen("#333333")
            self._plot.getAxis(axis).setTextPen("#333333")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot)

        self._redraw()

    def set_model(self, model: AntennaModel | None) -> None:
        self._model = model
        self._redraw()

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        self._unit_system = unit_system
        self._redraw()

    def retranslate(self) -> None:
        self._redraw()

    def _redraw(self) -> None:
        self._plot.clear()
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._plot.setLabel(
            "bottom",
            self._translator.t("geometry.distance", unit=unit),
            color="#333333",
        )
        self._plot.setLabel(
            "left",
            self._translator.t("geometry.height", unit=unit),
            color="#333333",
        )

        if self._model is None:
            self._plot.setTitle(self._translator.t("geometry.none"), color="#333333")
            return

        self._plot.setTitle(self._translator.t("panel.geometry"), color="#333333")
        x_values: list[float] = []
        z_values: list[float] = [0.0]
        span = 1.0

        for index, wire in enumerate(self._model.wires):
            dx = wire.end.x_m - wire.start.x_m
            dy = wire.end.y_m - wire.start.y_m
            horizontal = math.hypot(dx, dy)
            span = max(span, horizontal)
            if horizontal > 1e-12:
                x_start = -horizontal / 2.0
                x_end = horizontal / 2.0
            else:
                x_start = 0.0
                x_end = 0.0

            x_display = [
                length_from_m(x_start, self._unit_system),
                length_from_m(x_end, self._unit_system),
            ]
            z_display = [
                length_from_m(wire.start.z_m, self._unit_system),
                length_from_m(wire.end.z_m, self._unit_system),
            ]
            color = "#1f5fa8" if index == 0 else "#4a8f4a"
            self._plot.plot(
                x_display,
                z_display,
                pen=pg.mkPen(color, width=3),
            )
            x_values.extend([x_display[0], x_display[1]])
            z_values.extend(z_display)
            if horizontal <= 1e-12:
                x_values.append(0.0)

        ground_x = [
            length_from_m(-span * 0.6, self._unit_system),
            length_from_m(span * 0.6, self._unit_system),
        ]
        self._plot.plot(
            ground_x,
            [0.0, 0.0],
            pen=pg.mkPen("#777777", width=1, style=Qt.PenStyle.DashLine),
        )
        x_values.extend(ground_x)

        feed_wire = self._model.feed_wire
        feed_length = feed_wire.length_m
        ratio = (
            min(max(self._model.feed.offset_m / feed_length, 0.0), 1.0) if feed_length > 0 else 0.0
        )
        dx = feed_wire.end.x_m - feed_wire.start.x_m
        dy = feed_wire.end.y_m - feed_wire.start.y_m
        horizontal = math.hypot(dx, dy)
        feed_x = -horizontal / 2.0 + horizontal * ratio
        feed_z = feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * ratio
        feed_x_display = length_from_m(feed_x, self._unit_system)
        feed_z_display = length_from_m(feed_z, self._unit_system)
        self._plot.addItem(
            pg.ScatterPlotItem(
                [feed_x_display],
                [feed_z_display],
                symbol="o",
                size=10,
                brush=pg.mkBrush("#c0392b"),
                pen=pg.mkPen("#c0392b"),
            )
        )
        feed_label = pg.TextItem(
            self._translator.t("geometry.feed"),
            color="#c0392b",
            anchor=(0.0, 1.2),
        )
        feed_label.setPos(feed_x_display, feed_z_display)
        self._plot.addItem(feed_label)
        x_values.append(feed_x_display)
        z_values.append(feed_z_display)

        x_min = min(x_values)
        x_max = max(x_values)
        z_min = min(z_values)
        z_max = max(z_values)
        x_margin = max((x_max - x_min) * 0.15, 0.5)
        z_margin = max((z_max - z_min) * 0.15, 0.5)
        self._plot.setXRange(x_min - x_margin, x_max + x_margin, padding=0.0)
        self._plot.setYRange(
            min(0.0, z_min - z_margin),
            z_max + z_margin,
            padding=0.0,
        )
