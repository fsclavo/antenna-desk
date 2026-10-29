# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Palette-aware colors for diagrams and plots."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True, slots=True)
class ThemeColors:
    background: QColor
    plot_background: QColor
    text: QColor
    secondary_text: QColor
    axis: QColor
    grid: QColor
    light_line: QColor
    dimension: QColor
    wire: QColor
    feed: QColor
    ground: QColor
    resistance: QColor
    reactance: QColor
    swr: QColor
    pattern: QColor
    series_a: QColor
    series_b: QColor


LIGHT = ThemeColors(
    background=QColor("#ffffff"),
    plot_background=QColor("#ffffff"),
    text=QColor("#222222"),
    secondary_text=QColor("#666666"),
    axis=QColor("#333333"),
    grid=QColor("#b8b8b8"),
    light_line=QColor("#b8b8b8"),
    dimension=QColor("#555555"),
    wire=QColor("#1f5fa8"),
    feed=QColor("#c0392b"),
    ground=QColor("#777777"),
    resistance=QColor("#1f5fa8"),
    reactance=QColor("#d07b1f"),
    swr=QColor("#2e8b57"),
    pattern=QColor("#7b4ea3"),
    series_a=QColor("#1f5fa8"),
    series_b=QColor("#d07b1f"),
)

DARK = ThemeColors(
    background=QColor("#1e1e1e"),
    plot_background=QColor("#1e1e1e"),
    text=QColor("#e6e6e6"),
    secondary_text=QColor("#b8b8b8"),
    axis=QColor("#c8c8c8"),
    grid=QColor("#555555"),
    light_line=QColor("#666666"),
    dimension=QColor("#d0d0d0"),
    wire=QColor("#5aa9ff"),
    feed=QColor("#ff6b5a"),
    ground=QColor("#a0a0a0"),
    resistance=QColor("#5aa9ff"),
    reactance=QColor("#ffb454"),
    swr=QColor("#5fd38d"),
    pattern=QColor("#c49bff"),
    series_a=QColor("#5aa9ff"),
    series_b=QColor("#ffb454"),
)


def is_dark_palette(palette: QPalette | None = None) -> bool:
    active = palette if palette is not None else QApplication.palette()
    return active.color(QPalette.ColorRole.Window).lightness() < 128


def theme_colors(palette: QPalette | None = None) -> ThemeColors:
    return DARK if is_dark_palette(palette) else LIGHT
