# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UI preferences: font-size presets, language, units, and persistence."""

from __future__ import annotations

from pathlib import Path

import pytest
from main_window_support import FakeSolver
from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QDialog
from pytestqt.qtbot import QtBot

from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.dialogs.preferences_dialog import PreferencesDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.preferences import (
    FONT_SIZE_KEY,
    LANGUAGE_KEY,
    UNIT_SYSTEM_KEY,
    FontSize,
    FontSizeController,
    InMemoryPreferencesStore,
    QSettingsPreferencesStore,
    UiPreferences,
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


def test_qsettings_store_round_trips_all_preferences(tmp_path: Path) -> None:
    path = tmp_path / "preferences.ini"
    store = QSettingsPreferencesStore(QSettings(str(path), QSettings.Format.IniFormat))
    preferences = UiPreferences(
        font_size=FontSize.LARGE,
        language=Language.SPANISH,
        unit_system=UnitSystem.IMPERIAL,
    )

    store.save(preferences)

    reopened = QSettingsPreferencesStore(QSettings(str(path), QSettings.Format.IniFormat))
    assert reopened.load() == preferences


def test_missing_preferences_use_the_startup_defaults(tmp_path: Path) -> None:
    store = QSettingsPreferencesStore(
        QSettings(
            str(tmp_path / "preferences.ini"),
            QSettings.Format.IniFormat,
        )
    )

    preferences = store.load(
        default_language=Language.SPANISH,
        default_unit_system=UnitSystem.IMPERIAL,
    )

    assert preferences.font_size is FontSize.MEDIUM
    assert preferences.language is Language.SPANISH
    assert preferences.unit_system is UnitSystem.IMPERIAL


def test_invalid_stored_preferences_fall_back_to_defaults(tmp_path: Path) -> None:
    settings = QSettings(
        str(tmp_path / "preferences.ini"),
        QSettings.Format.IniFormat,
    )
    settings.setValue(FONT_SIZE_KEY, "huge")
    settings.setValue(LANGUAGE_KEY, "fr")
    settings.setValue(UNIT_SYSTEM_KEY, "cubits")
    store = QSettingsPreferencesStore(settings)

    preferences = store.load(
        default_language=Language.SPANISH,
        default_unit_system=UnitSystem.IMPERIAL,
    )

    assert preferences.font_size is FontSize.MEDIUM
    assert preferences.language is Language.SPANISH
    assert preferences.unit_system is UnitSystem.IMPERIAL


def test_in_memory_store_round_trips_preferences() -> None:
    store = InMemoryPreferencesStore()
    defaults = store.load(
        default_language=Language.SPANISH,
        default_unit_system=UnitSystem.IMPERIAL,
    )
    assert defaults.language is Language.SPANISH
    assert defaults.unit_system is UnitSystem.IMPERIAL

    preferences = UiPreferences(
        font_size=FontSize.SMALL,
        language=Language.ENGLISH,
        unit_system=UnitSystem.METRIC,
    )
    store.save(preferences)

    assert store.load() == preferences


def test_main_window_font_size_applies_and_persists(qtbot: QtBot) -> None:
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

    assert window._font_size_controller.size is FontSize.MEDIUM

    window._set_font_size(FontSize.LARGE)

    assert app.font().pointSizeF() == pytest.approx(12.0)
    assert preferences.load().font_size is FontSize.LARGE
    assert window._font_size_controller.size is FontSize.LARGE
    assert window._dirty is False

    window._set_font_size(FontSize.MEDIUM)

    assert app.font().pointSizeF() == pytest.approx(10.0)
    assert preferences.load().font_size is FontSize.MEDIUM
    assert window._font_size_controller.size is FontSize.MEDIUM


def test_main_window_starts_with_the_saved_font_size(qtbot: QtBot) -> None:
    app = _application()
    base = QFont("Sans Serif", 10)
    app.setFont(base)
    preferences = InMemoryPreferencesStore(UiPreferences(font_size=FontSize.LARGE))
    controller = FontSizeController(base)
    controller.apply(preferences.load().font_size)
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
    assert window._font_size_controller.size is FontSize.LARGE


def test_language_and_units_are_persisted(window: MainWindow) -> None:
    window._set_language(Language.SPANISH)
    window._set_unit_system(UnitSystem.IMPERIAL)

    saved = window._preferences.load()

    assert saved.language is Language.SPANISH
    assert saved.unit_system is UnitSystem.IMPERIAL


def test_preferences_action_applies_accepted_values(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    accepted = UiPreferences(
        font_size=FontSize.LARGE,
        language=Language.SPANISH,
        unit_system=UnitSystem.IMPERIAL,
    )
    monkeypatch.setattr(
        PreferencesDialog,
        "exec",
        lambda self: QDialog.DialogCode.Accepted,
    )
    monkeypatch.setattr(PreferencesDialog, "preferences", lambda self: accepted)

    window.show_preferences()

    assert window._translator.language is Language.SPANISH
    assert window._font_size_controller.size is FontSize.LARGE
    assert window._unit_system is UnitSystem.IMPERIAL
    assert window._ocfd_form._length.suffix().strip() == "ft"
    assert window._simulate_action.text() == "Simular"
    assert window._current_preferences() == accepted
    assert window._preferences.load() == accepted
    assert window._dirty is False


def test_preferences_dialog_returns_selected_values(qtbot: QtBot) -> None:
    dialog = PreferencesDialog(
        Translator(Language.ENGLISH),
        UiPreferences(
            font_size=FontSize.SMALL,
            language=Language.SPANISH,
            unit_system=UnitSystem.IMPERIAL,
        ),
    )
    qtbot.addWidget(dialog)

    assert dialog._language.currentData() == Language.SPANISH.value
    assert dialog._units.currentData() == UnitSystem.IMPERIAL.value
    assert dialog._font_size.currentData() == FontSize.SMALL.value

    dialog._language.setCurrentIndex(dialog._language.findData(Language.ENGLISH.value))
    dialog._units.setCurrentIndex(dialog._units.findData(UnitSystem.METRIC.value))
    dialog._font_size.setCurrentIndex(dialog._font_size.findData(FontSize.LARGE.value))

    assert dialog.preferences() == UiPreferences(
        font_size=FontSize.LARGE,
        language=Language.ENGLISH,
        unit_system=UnitSystem.METRIC,
    )


def test_preferences_action_retranslates_and_replaces_quick_menus(
    window: MainWindow,
) -> None:
    assert window._preferences_action in window._edit_menu.actions()
    assert window._preferences_action not in window._tools_menu.actions()
    assert not hasattr(window, "_language_menu")
    assert not hasattr(window, "_units_menu")
    assert not hasattr(window, "_font_size_menu")

    window._set_language(Language.SPANISH)

    assert window._preferences_action.text() == "Preferencias..."

    window._set_language(Language.ENGLISH)

    assert window._preferences_action.text() == "Preferences..."

    edit_titles = [action.text() for action in window._edit_menu.actions()]
    tools_titles = [action.text() for action in window._tools_menu.actions()]
    assert "Preferences..." in edit_titles
    assert "Preferences..." not in tools_titles
    assert "Language" not in tools_titles
    assert "Units" not in tools_titles
    assert "Font Size" not in tools_titles


def test_preferences_keys_exist_in_both_languages() -> None:
    keys = (
        "preferences.font_size",
        "preferences.language",
        "preferences.units",
        "font_size.small",
        "font_size.medium",
        "font_size.large",
        "preferences.title",
        "preferences.hint",
        "action.preferences",
    )
    for key in keys:
        assert Translator(Language.ENGLISH).t(key) != key
        assert Translator(Language.SPANISH).t(key) != key
