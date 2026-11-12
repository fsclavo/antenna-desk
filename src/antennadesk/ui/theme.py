# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Application palettes and palette-aware colors for diagrams and plots."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


class ThemePreference(StrEnum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


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


def _build_palette(
    *,
    window: str,
    window_text: str,
    base: str,
    alternate_base: str,
    tooltip_base: str,
    tooltip_text: str,
    text: str,
    button: str,
    button_text: str,
    bright_text: str,
    link: str,
    highlight: str,
    highlighted_text: str,
    placeholder_text: str,
    light: str,
    midlight: str,
    dark: str,
    mid: str,
    shadow: str,
    disabled_text: str,
) -> QPalette:
    palette = QPalette()
    roles = {
        QPalette.ColorRole.Window: window,
        QPalette.ColorRole.WindowText: window_text,
        QPalette.ColorRole.Base: base,
        QPalette.ColorRole.AlternateBase: alternate_base,
        QPalette.ColorRole.ToolTipBase: tooltip_base,
        QPalette.ColorRole.ToolTipText: tooltip_text,
        QPalette.ColorRole.Text: text,
        QPalette.ColorRole.Button: button,
        QPalette.ColorRole.ButtonText: button_text,
        QPalette.ColorRole.BrightText: bright_text,
        QPalette.ColorRole.Link: link,
        QPalette.ColorRole.LinkVisited: link,
        QPalette.ColorRole.Highlight: highlight,
        QPalette.ColorRole.HighlightedText: highlighted_text,
        QPalette.ColorRole.PlaceholderText: placeholder_text,
        QPalette.ColorRole.Light: light,
        QPalette.ColorRole.Midlight: midlight,
        QPalette.ColorRole.Dark: dark,
        QPalette.ColorRole.Mid: mid,
        QPalette.ColorRole.Shadow: shadow,
    }
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
        for role, value in roles.items():
            palette.setColor(group, role, QColor(value))
    for role, value in roles.items():
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(value))
    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.ToolTipText,
        QPalette.ColorRole.PlaceholderText,
    ):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(disabled_text))
    return palette


LIGHT_PALETTE = _build_palette(
    window="#f3f3f3",
    window_text="#1a1a1a",
    base="#ffffff",
    alternate_base="#f0f0f0",
    tooltip_base="#ffffdc",
    tooltip_text="#1a1a1a",
    text="#1a1a1a",
    button="#f3f3f3",
    button_text="#1a1a1a",
    bright_text="#c0392b",
    link="#1f5fa8",
    highlight="#2f6fbf",
    highlighted_text="#ffffff",
    placeholder_text="#6b6b6b",
    light="#ffffff",
    midlight="#e3e3e3",
    dark="#b0b0b0",
    mid="#c8c8c8",
    shadow="#808080",
    disabled_text="#8a8a8a",
)

DARK_PALETTE = _build_palette(
    window="#1e1e1e",
    window_text="#e6e6e6",
    base="#252525",
    alternate_base="#2d2d2d",
    tooltip_base="#2d2d2d",
    tooltip_text="#e6e6e6",
    text="#e6e6e6",
    button="#2d2d2d",
    button_text="#e6e6e6",
    bright_text="#ff6b5a",
    link="#5aa9ff",
    highlight="#2f6fbf",
    highlighted_text="#ffffff",
    placeholder_text="#a0a0a0",
    light="#3a3a3a",
    midlight="#333333",
    dark="#151515",
    mid="#202020",
    shadow="#0a0a0a",
    disabled_text="#707070",
)


class ThemeController:
    """Apply the system, light, or dark palette to the whole application.

    The application uses Fusion as its single widget style. Themes only swap
    palettes, so changing them at runtime does not invalidate widget geometry or
    popup metrics computed by the style.
    """

    _system_palette: QPalette | None = None

    def __init__(self) -> None:
        if ThemeController._system_palette is None:
            app = QApplication.instance()
            if isinstance(app, QApplication):
                ThemeController._system_palette = QPalette(app.palette())
            else:
                ThemeController._system_palette = QPalette()
        self._preference = ThemePreference.SYSTEM

    @property
    def preference(self) -> ThemePreference:
        return self._preference

    @property
    def system_palette(self) -> QPalette:
        palette = ThemeController._system_palette
        return QPalette(palette) if palette is not None else QPalette()

    def apply(self, preference: ThemePreference) -> None:
        self._preference = ThemePreference(preference)
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return

        if self._preference is ThemePreference.SYSTEM:
            app.setPalette(self.system_palette)
            return

        palette = DARK_PALETTE if self._preference is ThemePreference.DARK else LIGHT_PALETTE
        app.setPalette(palette)


def is_dark_palette(palette: QPalette | None = None) -> bool:
    active = palette if palette is not None else QApplication.palette()
    return active.color(QPalette.ColorRole.Window).lightness() < 128


def theme_colors(palette: QPalette | None = None) -> ThemeColors:
    return DARK if is_dark_palette(palette) else LIGHT
