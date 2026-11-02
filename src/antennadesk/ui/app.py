# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""QApplication entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QLocale
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .. import __version__
from ..persistence.json_repository import JsonProjectRepository
from ..simulation.nec2.solver import Nec2cSolver
from .i18n import Language, Translator
from .main_window import MainWindow
from .solver_locator import find_nec2c


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

    language = (
        Language.SPANISH
        if QLocale.system().language() == QLocale.Language.Spanish
        else Language.ENGLISH
    )
    translator = Translator(language)
    executable = find_nec2c()
    solver = Nec2cSolver(executable) if executable is not None else None
    window = MainWindow(JsonProjectRepository(), solver, translator)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
