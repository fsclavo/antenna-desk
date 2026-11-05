# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistent UI preferences and application font sizing."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, TypeVar

from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from .fonts import set_current_font_scale
from .i18n import Language
from .units import UnitSystem

FONT_SIZE_KEY = "ui/font_size"
LANGUAGE_KEY = "ui/language"
UNIT_SYSTEM_KEY = "ui/units"
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
_PreferenceEnum = TypeVar("_PreferenceEnum", FontSize, Language, UnitSystem)


@dataclass(frozen=True, slots=True)
class UiPreferences:
    font_size: FontSize = FontSize.MEDIUM
    language: Language = Language.ENGLISH
    unit_system: UnitSystem = UnitSystem.METRIC


class PreferencesStore(Protocol):
    """Minimal persistence port for UI preferences."""

    def load(
        self,
        *,
        default_language: Language = Language.ENGLISH,
        default_unit_system: UnitSystem = UnitSystem.METRIC,
    ) -> UiPreferences: ...

    def save(self, preferences: UiPreferences) -> None: ...


class QSettingsPreferencesStore:
    """Store UI preferences with the platform-native QSettings backend."""

    def __init__(self, settings: QSettings | None = None) -> None:
        self._settings = settings if settings is not None else QSettings()

    def load(
        self,
        *,
        default_language: Language = Language.ENGLISH,
        default_unit_system: UnitSystem = UnitSystem.METRIC,
    ) -> UiPreferences:
        return UiPreferences(
            font_size=self._load_enum(FONT_SIZE_KEY, FontSize, FontSize.MEDIUM),
            language=self._load_enum(LANGUAGE_KEY, Language, default_language),
            unit_system=self._load_enum(
                UNIT_SYSTEM_KEY,
                UnitSystem,
                default_unit_system,
            ),
        )

    def save(self, preferences: UiPreferences) -> None:
        self._settings.setValue(FONT_SIZE_KEY, preferences.font_size.value)
        self._settings.setValue(LANGUAGE_KEY, preferences.language.value)
        self._settings.setValue(UNIT_SYSTEM_KEY, preferences.unit_system.value)
        self._settings.sync()

    def _load_enum(
        self,
        key: str,
        enum_type: type[_PreferenceEnum],
        default: _PreferenceEnum,
    ) -> _PreferenceEnum:
        raw = self._settings.value(key, default.value)
        if isinstance(raw, str):
            try:
                return enum_type(raw)
            except ValueError:
                pass
        return default


class InMemoryPreferencesStore:
    """In-memory store used by tests and by windows without persistence."""

    def __init__(self, preferences: UiPreferences | None = None) -> None:
        self._preferences = preferences

    def load(
        self,
        *,
        default_language: Language = Language.ENGLISH,
        default_unit_system: UnitSystem = UnitSystem.METRIC,
    ) -> UiPreferences:
        if self._preferences is not None:
            return self._preferences
        return UiPreferences(
            language=default_language,
            unit_system=default_unit_system,
        )

    def save(self, preferences: UiPreferences) -> None:
        self._preferences = preferences


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
