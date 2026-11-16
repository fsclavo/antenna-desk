# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Font scaling helpers for custom-painted widgets and plots."""

from __future__ import annotations

from collections.abc import Iterable

import pyqtgraph as pg
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

FONT_SCALE_PROPERTY = "antennadesk_font_scale"
MIN_POINT_SIZE = 6.0
MIN_PIXEL_SIZE = 8


def current_font_scale() -> float:
    """Return the active UI font scale, or 1.0 outside the application."""

    app = QApplication.instance()
    if isinstance(app, QApplication):
        value = app.property(FONT_SCALE_PROPERTY)
        if isinstance(value, (int, float)):
            return float(value)
    return 1.0


def set_current_font_scale(scale: float) -> None:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        app.setProperty(FONT_SCALE_PROPERTY, scale)


def scaled_point_size(point_size: float) -> float:
    return max(MIN_POINT_SIZE, point_size * current_font_scale())


def scaled_font(
    point_size: float,
    weight: QFont.Weight = QFont.Weight.Normal,
    family: str | None = None,
) -> QFont:
    font = QFont(family) if family is not None else QFont("Sans Serif")
    font.setPointSizeF(scaled_point_size(point_size))
    font.setWeight(weight)
    return font


def scaled_pixel_font(
    pixel_size: int,
    weight: QFont.Weight = QFont.Weight.Normal,
    family: str | None = None,
) -> QFont:
    font = QFont(family) if family is not None else QFont("Sans Serif")
    font.setPixelSize(max(MIN_PIXEL_SIZE, round(pixel_size * current_font_scale())))
    font.setWeight(weight)
    return font


def scaled_font_copy(font: QFont) -> QFont:
    """Scale an existing font, preserving its family and style."""

    scaled = QFont(font)
    scale = current_font_scale()
    if scaled.pointSizeF() > 0:
        scaled.setPointSizeF(max(MIN_POINT_SIZE, scaled.pointSizeF() * scale))
    elif scaled.pixelSize() > 0:
        scaled.setPixelSize(max(MIN_PIXEL_SIZE, round(scaled.pixelSize() * scale)))
    return scaled


def scaled_dialog_size(width: int, height: int) -> tuple[int, int]:
    """Scale a dialog's preferred size and cap it to the available screen.

    A tall dialog at a large font scale can exceed the screen height even though
    its content is inside a scroll area. Capping the initial size keeps the
    title bar, buttons, and scroll area reachable; the user can still resize the
    dialog larger.
    """

    scale = current_font_scale()
    scaled_width = max(320, round(width * scale))
    scaled_height = max(240, round(height * scale))
    app = QApplication.instance()
    if isinstance(app, QApplication):
        screen = app.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            max_width = max(320, round(available.width() * 0.9))
            max_height = max(240, round(available.height() * 0.9))
            scaled_width = min(scaled_width, max_width)
            scaled_height = min(scaled_height, max_height)
    return scaled_width, scaled_height


def apply_plot_fonts(plots: Iterable[pg.PlotWidget]) -> None:
    """Apply the active font scale to pyqtgraph axes, titles, and legends."""

    app = QApplication.instance()
    family = app.font().family() if isinstance(app, QApplication) else None
    tick_font = scaled_font(9.0, family=family)
    title_size = f"{scaled_point_size(11.0):.1f}pt"
    legend_size = f"{scaled_point_size(9.0):.1f}pt"
    for plot in plots:
        for axis_name in ("left", "bottom"):
            axis = plot.getAxis(axis_name)
            axis.setTickFont(tick_font)
            if axis.label is not None:
                axis.label.setFont(tick_font)
        title = plot.plotItem.titleLabel
        title.setAttr("size", title_size)
        if title.text:
            title.setText(title.text)
        legend = plot.plotItem.legend
        if legend is not None:
            legend.setLabelTextSize(legend_size)
