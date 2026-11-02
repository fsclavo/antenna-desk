# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QIcon
from pytestqt.qtbot import QtBot


def test_application_icon_is_a_loadable_resource(qtbot: QtBot) -> None:
    icon_path = Path("src/antennadesk/ui/resources/antennadesk.svg")
    assert icon_path.is_file()
    assert not QIcon(str(icon_path)).isNull()


def test_desktop_entry_points_to_the_gui_script() -> None:
    desktop = Path("packaging/antennadesk.desktop")
    assert desktop.is_file()
    text = desktop.read_text(encoding="utf-8")
    assert "Exec=antennadesk" in text
    assert "Icon=antennadesk" in text
