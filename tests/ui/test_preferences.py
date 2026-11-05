# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UI font-size presets and preference persistence."""

from __future__ import annotations

from pathlib import Path

import pytest
from main_window_support import FakeSolver
from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.preferences import (
    FONT_SIZE_KEY,
    FontSize,
    FontSizeController,
    InMemoryPreferencesStore,
    QSettingsPreferencesStore,
)
from antennadesk.ui.units import UnitSystem


def _application() -> QApplication:
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    return app


def test_font_sizes_are_relative_to_the_base_font() -> None:
    controller = FontSizeController(QFont("Sans Serif", 10))

    assert controller.size is FontSize.MEDIUM
    assert controller.font_for(FontSize.SMALL).pointSizeF() == pytest.approx(9.0)
    assert controller.font_for(FontSize.MEDIUM).pointSizeF() == pytest.approx(10.0)
    assert controller.font_for(FontSize.LARGE).pointSizeF() == pytest.approx(12.0)


def test_applying_font_sizes_restores_the_base_font(qtbot: QtBot) -> None:
    app = _application()
    base = QFont("Sans Serif", 10)
    app.setFont(base)
    controller = FontSizeController(base)

    controller.apply(FontSize.LARGE)
    assert app.font().pointSizeF() == pytest.approx(12.0)

    controller.apply(FontSize.SMALL)
    assert app.font().pointSizeF() == pytest.approx(9.0)

    controller.apply(FontSize.MEDIUM)
    assert app.font().pointSizeF() == pytest.approx(10.0)
    assert app.font().family() == base.family()
    assert controller.size is FontSize.MEDIUM


def test_pixel_sized_fonts_keep_using_pixels() -> None:
    base = QFont("Sans Serif")
    base.setPixelSize(16)
    controller = FontSizeController(base)

    assert controller.font_for(FontSize.SMALL).pixelSize() == 14
    assert controller.font_for(FontSize.MEDIUM).pixelSize() == 16
    assert controller.font_for(FontSize.LARGE).pixelSize() == 19


def test_small_font_has_a_legibility_floor() -> None:
    controller = FontSizeController(QFont("Sans Serif", 6))

    assert controller.font_for(FontSize.SMALL).pointSizeF() == pytest.approx(6.0)


def test_qsettings_store_round_trips_the_font_size(tmp_path: Path) -> None:
    path = tmp_path / "preferences.ini"
    store = QSettingsPreferencesStore(QSettings(str(path), QSettings.Format.IniFormat))

    assert store.load_font_size() is FontSize.MEDIUM
    store.save_font_size(FontSize.LARGE)

    reopened = QSettingsPreferencesStore(QSettings(str(path), QSettings.Format.IniFormat))
    assert reopened.load_font_size() is FontSize.LARGE


def test_invalid_stored_font_size_falls_back_to_normal(tmp_path: Path) -> None:
    settings = QSettings(
        str(tmp_path / "preferences.ini"),
        QSettings.Format.IniFormat,
    )
    settings.setValue(FONT_SIZE_KEY, "huge")
    store = QSettingsPreferencesStore(settings)

    assert store.load_font_size() is FontSize.MEDIUM


def test_in_memory_store_round_trips_the_font_size() -> None:
    store = InMemoryPreferencesStore()

    assert store.load_font_size() is FontSize.MEDIUM
    store.save_font_size(FontSize.SMALL)
    assert store.load_font_size() is FontSize.SMALL


def test_main_window_font_actions_apply_and_persist(
    qtbot: QtBot,
) -> None:
    app = _application()
    base = QFont("Sans Serif", 10)
    app.setFont(base)
    preferences = InMemoryPreferencesStore()
    controller = FontSizeController(base)
    window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preferences=preferences,
        font_size_controller=controller,
    )
    qtbot.addWidget(window)

    assert window._font_medium_action.isChecked() is True
    assert window._font_small_action.isChecked() is False
    assert window._font_large_action.isChecked() is False

    window._font_large_action.trigger()

    assert app.font().pointSizeF() == pytest.approx(12.0)
    assert preferences.load_font_size() is FontSize.LARGE
    assert window._font_large_action.isChecked() is True
    assert window._font_medium_action.isChecked() is False
    assert window._dirty is False

    window._font_medium_action.trigger()

    assert app.font().pointSizeF() == pytest.approx(10.0)
    assert preferences.load_font_size() is FontSize.MEDIUM
    assert window._font_medium_action.isChecked() is True


def test_main_window_starts_with_the_saved_font_size(qtbot: QtBot) -> None:
    app = _application()
    base = QFont("Sans Serif", 10)
    app.setFont(base)
    preferences = InMemoryPreferencesStore(FontSize.LARGE)
    controller = FontSizeController(base)
    controller.apply(preferences.load_font_size())
    window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preferences=preferences,
        font_size_controller=controller,
    )
    qtbot.addWidget(window)

    assert app.font().pointSizeF() == pytest.approx(12.0)
    assert window._font_large_action.isChecked() is True
    assert window._font_medium_action.isChecked() is False


def test_font_size_menu_retranslates(window: MainWindow) -> None:
    assert window._font_size_menu.menuAction() in window._tools_menu.actions()

    window._set_language(Language.SPANISH)

    assert window._font_size_menu.title() == "Tamaño de fuente"
    assert window._font_small_action.text() == "Pequeño"
    assert window._font_medium_action.text() == "Normal"
    assert window._font_large_action.text() == "Grande"

    window._set_language(Language.ENGLISH)

    assert window._font_size_menu.title() == "Font Size"
    assert window._font_small_action.text() == "Small"
    assert window._font_medium_action.text() == "Normal"
    assert window._font_large_action.text() == "Large"


def test_font_size_keys_exist_in_both_languages() -> None:
    keys = (
        "menu.font_size",
        "font_size.small",
        "font_size.medium",
        "font_size.large",
    )
    for key in keys:
        assert Translator(Language.ENGLISH).t(key) != key
        assert Translator(Language.SPANISH).t(key) != key
