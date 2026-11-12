# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""QApplication entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .. import __version__
from ..persistence.json_repository import JsonProjectRepository
from ..simulation.nec2.solver import Nec2cSolver
from .i18n import Translator
from .main_window import MainWindow
from .preferences import (
    FontSizeController,
    QSettingsPreferencesStore,
    resolve_language,
)
from .solver_locator import find_nec2c
from .theme import ThemeController


def main() -> int:
    if any(argument in {"--version", "-V"} for argument in sys.argv[1:]):
        print(__version__)
        return 0

    if "--check-solver" in sys.argv[1:]:
        executable = find_nec2c()
        if executable is None:
            print("nec2c not found", file=sys.stderr)
            return 1
        print(executable)
        return 0

    app = QApplication(sys.argv)
    app.setApplicationName("AntennaDesk")
    app.setApplicationDisplayName("AntennaDesk")
    app.setOrganizationName("AntennaDesk")
    icon_path = Path(__file__).with_name("resources") / "antennadesk.svg"
    if icon_path.is_file():
        app.setWindowIcon(QIcon(str(icon_path)))

    preferences_store = QSettingsPreferencesStore()
    preferences = preferences_store.load()
    font_size_controller = FontSizeController(app.font())
    font_size_controller.apply(preferences.font_size)
    theme_controller = ThemeController()
    # Use one widget style for every theme. Changing QApplication.style() at
    # runtime leaves cached popup metrics from the previous style behind, which
    # can make a QComboBox show scroll arrows with only part of its items.
    if app.style().name().lower() != "fusion":
        app.setStyle("Fusion")
    theme_controller.apply(preferences.theme)

    translator = Translator(resolve_language(preferences.language))
    executable = find_nec2c()
    solver = Nec2cSolver(executable) if executable is not None else None
    window = MainWindow(
        JsonProjectRepository(),
        solver,
        translator,
        preferences.unit_system,
        preferences=preferences_store,
        font_size_controller=font_size_controller,
        language_preference=preferences.language,
        theme_controller=theme_controller,
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
