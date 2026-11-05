# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistent UI preferences and application font sizing."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from .fonts import set_current_font_scale

FONT_SIZE_KEY = "ui/font_size"
_MIN_POINT_SIZE = 6.0
_MIN_PIXEL_SIZE = 8


class FontSize(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


_FONT_SCALE: dict[FontSize, float] = {
    FontSize.SMALL: 0.9,
    FontSize.MEDIUM: 1.0,
    FontSize.LARGE: 1.2,
}


class PreferencesStore(Protocol):
    """Minimal persistence port for UI preferences."""

    def load_font_size(self) -> FontSize: ...

    def save_font_size(self, size: FontSize) -> None: ...


class QSettingsPreferencesStore:
    """Store UI preferences with the platform-native QSettings backend."""

    def __init__(self, settings: QSettings | None = None) -> None:
        self._settings = settings if settings is not None else QSettings()

    def load_font_size(self) -> FontSize:
        raw = self._settings.value(FONT_SIZE_KEY, FontSize.MEDIUM.value)
        if isinstance(raw, str):
            try:
                return FontSize(raw)
            except ValueError:
                pass
        return FontSize.MEDIUM

    def save_font_size(self, size: FontSize) -> None:
        self._settings.setValue(FONT_SIZE_KEY, size.value)
        self._settings.sync()


class InMemoryPreferencesStore:
    """In-memory store used by tests and by windows without persistence."""

    def __init__(self, font_size: FontSize = FontSize.MEDIUM) -> None:
        self._font_size = font_size

    def load_font_size(self) -> FontSize:
        return self._font_size

    def save_font_size(self, size: FontSize) -> None:
        self._font_size = size


class FontSizeController:
    """Apply S/M/L font sizes relative to the application's original font."""

    def __init__(self, base_font: QFont) -> None:
        self._base_font = QFont(base_font)
        self._size = FontSize.MEDIUM

    @property
    def size(self) -> FontSize:
        return self._size

    def font_for(self, size: FontSize) -> QFont:
        if size is FontSize.MEDIUM:
            return QFont(self._base_font)

        font = QFont(self._base_font)
        factor = _FONT_SCALE[size]
        if font.pointSizeF() > 0:
            font.setPointSizeF(max(_MIN_POINT_SIZE, font.pointSizeF() * factor))
        elif font.pixelSize() > 0:
            font.setPixelSize(max(_MIN_PIXEL_SIZE, round(font.pixelSize() * factor)))
        return font

    def apply(self, size: FontSize) -> None:
        set_current_font_scale(_FONT_SCALE[size])
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setFont(self.font_for(size))
        self._size = size
