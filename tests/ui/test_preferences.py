# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UI preferences: font-size presets, language, units, and persistence."""

from __future__ import annotations

from pathlib import Path

import pytest
from main_window_support import FakeSolver
from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import QApplication, QDialog, QStyleFactory
from pytestqt.qtbot import QtBot

from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.dialogs.preferences_dialog import PreferencesDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.preferences import (
    FONT_SIZE_KEY,
    LANGUAGE_KEY,
    THEME_KEY,
    UNIT_SYSTEM_KEY,
    WORKFLOW_MODE_KEY,
    FontSize,
    FontSizeController,
    InMemoryPreferencesStore,
    LanguagePreference,
    QSettingsPreferencesStore,
    UiPreferences,
    resolve_language,
)
from antennadesk.ui.theme import (
    ThemeController,
    ThemePreference,
    is_dark_palette,
)
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.workflow import WorkflowMode


def _application() -> QApplication:
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    return app


def test_system_language_resolves_to_a_supported_language() -> None:
    assert resolve_language(LanguagePreference.ENGLISH) is Language.ENGLISH
    assert resolve_language(LanguagePreference.SPANISH) is Language.SPANISH
    assert resolve_language(LanguagePreference.SYSTEM) in (
        Language.ENGLISH,
        Language.SPANISH,
    )


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
        language=LanguagePreference.SPANISH,
        unit_system=UnitSystem.IMPERIAL,
        workflow_mode=WorkflowMode.GUIDED,
        theme=ThemePreference.DARK,
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
        default_language=LanguagePreference.SPANISH,
        default_unit_system=UnitSystem.IMPERIAL,
    )

    assert preferences.font_size is FontSize.MEDIUM
    assert preferences.language is LanguagePreference.SPANISH
    assert preferences.unit_system is UnitSystem.IMPERIAL
    assert preferences.workflow_mode is WorkflowMode.STANDARD
    assert preferences.theme is ThemePreference.SYSTEM


def test_invalid_stored_preferences_fall_back_to_defaults(tmp_path: Path) -> None:
    settings = QSettings(
        str(tmp_path / "preferences.ini"),
        QSettings.Format.IniFormat,
    )
    settings.setValue(FONT_SIZE_KEY, "huge")
    settings.setValue(LANGUAGE_KEY, "fr")
    settings.setValue(UNIT_SYSTEM_KEY, "cubits")
    settings.setValue(WORKFLOW_MODE_KEY, "expert")
    settings.setValue(THEME_KEY, "sepia")
    store = QSettingsPreferencesStore(settings)

    preferences = store.load(
        default_language=LanguagePreference.SPANISH,
        default_unit_system=UnitSystem.IMPERIAL,
    )

    assert preferences.font_size is FontSize.MEDIUM
    assert preferences.language is LanguagePreference.SPANISH
    assert preferences.unit_system is UnitSystem.IMPERIAL
    assert preferences.workflow_mode is WorkflowMode.STANDARD
    assert preferences.theme is ThemePreference.SYSTEM


def test_in_memory_store_round_trips_preferences() -> None:
    store = InMemoryPreferencesStore()
    defaults = store.load(
        default_language=LanguagePreference.SPANISH,
        default_unit_system=UnitSystem.IMPERIAL,
    )
    assert defaults.language is LanguagePreference.SPANISH
    assert defaults.unit_system is UnitSystem.IMPERIAL
    assert defaults.workflow_mode is WorkflowMode.STANDARD
    assert defaults.theme is ThemePreference.SYSTEM

    preferences = UiPreferences(
        font_size=FontSize.SMALL,
        language=LanguagePreference.ENGLISH,
        unit_system=UnitSystem.METRIC,
        workflow_mode=WorkflowMode.GUIDED,
        theme=ThemePreference.LIGHT,
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


def test_theme_controller_switches_between_system_light_and_dark(qtbot: QtBot) -> None:
    app = _application()
    controller = ThemeController()
    system_window = controller.system_palette.color(QPalette.ColorRole.Window)

    controller.apply(ThemePreference.DARK)

    assert controller.preference is ThemePreference.DARK
    assert is_dark_palette(app.palette())

    controller.apply(ThemePreference.LIGHT)

    assert controller.preference is ThemePreference.LIGHT
    assert not is_dark_palette(app.palette())

    controller.apply(ThemePreference.SYSTEM)

    assert controller.preference is ThemePreference.SYSTEM
    assert app.palette().color(QPalette.ColorRole.Window) == system_window


def test_theme_controller_does_not_change_the_application_style(qtbot: QtBot) -> None:
    app = _application()
    available_styles = QStyleFactory.keys()
    alternative = next(
        (name for name in available_styles if name.lower() != "fusion"),
        None,
    )
    if alternative is not None:
        app.setStyle(alternative)
    style = app.style().name()
    controller = ThemeController()

    for preference in (
        ThemePreference.LIGHT,
        ThemePreference.DARK,
        ThemePreference.SYSTEM,
    ):
        controller.apply(preference)
        assert app.style().name() == style


def test_main_window_starts_with_the_saved_theme(qtbot: QtBot) -> None:
    app = _application()
    preferences = InMemoryPreferencesStore(UiPreferences(theme=ThemePreference.DARK))
    window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preferences=preferences,
    )
    qtbot.addWidget(window)

    assert window._theme_controller.preference is ThemePreference.DARK
    assert window._current_preferences().theme is ThemePreference.DARK
    assert is_dark_palette(app.palette())


def test_language_and_units_are_persisted(window: MainWindow) -> None:
    window._set_language(Language.SPANISH)
    window._set_unit_system(UnitSystem.IMPERIAL)

    saved = window._preferences.load()

    assert saved.language is LanguagePreference.SPANISH
    assert saved.unit_system is UnitSystem.IMPERIAL


def test_preferences_action_applies_accepted_values(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    accepted = UiPreferences(
        font_size=FontSize.LARGE,
        language=LanguagePreference.SPANISH,
        unit_system=UnitSystem.IMPERIAL,
        workflow_mode=WorkflowMode.GUIDED,
        theme=ThemePreference.DARK,
    )
    monkeypatch.setattr(
        PreferencesDialog,
        "exec",
        lambda self: QDialog.DialogCode.Accepted,
    )
    monkeypatch.setattr(PreferencesDialog, "preferences", lambda self: accepted)

    window.show_preferences()

    assert window._translator.language is Language.SPANISH
    assert window._language_preference is LanguagePreference.SPANISH
    assert window._font_size_controller.size is FontSize.LARGE
    assert window._unit_system is UnitSystem.IMPERIAL
    assert window._workflow_mode is WorkflowMode.GUIDED
    assert window._theme_controller.preference is ThemePreference.DARK
    assert is_dark_palette(_application().palette())
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
            language=LanguagePreference.SPANISH,
            unit_system=UnitSystem.IMPERIAL,
            workflow_mode=WorkflowMode.GUIDED,
            theme=ThemePreference.LIGHT,
        ),
    )
    qtbot.addWidget(dialog)

    assert dialog._language.currentData() == LanguagePreference.SPANISH.value
    assert dialog._units.currentData() == UnitSystem.IMPERIAL.value
    assert dialog._font_size.currentData() == FontSize.SMALL.value
    assert dialog._theme.currentData() == ThemePreference.LIGHT.value
    assert dialog._workflow_mode.currentData() == WorkflowMode.GUIDED.value
    assert "palette" in dialog._theme.toolTip().lower()

    dialog._language.setCurrentIndex(dialog._language.findData(LanguagePreference.ENGLISH.value))
    dialog._units.setCurrentIndex(dialog._units.findData(UnitSystem.METRIC.value))
    dialog._font_size.setCurrentIndex(dialog._font_size.findData(FontSize.LARGE.value))
    dialog._theme.setCurrentIndex(dialog._theme.findData(ThemePreference.DARK.value))
    dialog._workflow_mode.setCurrentIndex(
        dialog._workflow_mode.findData(WorkflowMode.ADVANCED.value)
    )

    assert dialog.preferences() == UiPreferences(
        font_size=FontSize.LARGE,
        language=LanguagePreference.ENGLISH,
        unit_system=UnitSystem.METRIC,
        workflow_mode=WorkflowMode.ADVANCED,
        theme=ThemePreference.DARK,
    )


def test_preferences_dialog_restores_defaults(qtbot: QtBot) -> None:
    dialog = PreferencesDialog(
        Translator(Language.ENGLISH),
        UiPreferences(
            font_size=FontSize.LARGE,
            language=LanguagePreference.SPANISH,
            unit_system=UnitSystem.IMPERIAL,
            theme=ThemePreference.DARK,
        ),
    )
    qtbot.addWidget(dialog)

    dialog._restore_defaults()

    assert dialog.preferences() == UiPreferences()
    assert dialog.preferences().workflow_mode is WorkflowMode.STANDARD
    assert dialog.preferences().theme is ThemePreference.SYSTEM


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
        "preferences.language_system",
        "preferences.theme",
        "preferences.units",
        "preferences.workflow_mode",
        "preferences.restore_defaults",
        "font_size.small",
        "font_size.medium",
        "font_size.large",
        "theme.system",
        "theme.light",
        "theme.dark",
        "workflow.mode.guided",
        "workflow.mode.standard",
        "workflow.mode.advanced",
        "preferences.title",
        "preferences.hint",
        "help.preferences.theme",
        "help.preferences.workflow_mode",
        "action.preferences",
        "action.ok",
        "action.cancel",
    )
    for key in keys:
        assert Translator(Language.ENGLISH).t(key) != key
        assert Translator(Language.SPANISH).t(key) != key
