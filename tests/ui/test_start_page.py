# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Start-page examples, reference library, and recent-project privacy."""

from __future__ import annotations

from pathlib import Path

from pytestqt.qtbot import QtBot

from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.recent_projects import RecentProject
from antennadesk.ui.widgets.start_page import StartPage


def test_recent_list_shows_file_names_and_emits_open_and_remove(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    page = StartPage(Translator(Language.ENGLISH))
    qtbot.addWidget(page)
    existing = tmp_path / "private" / "dipole.antennadesk"
    existing.parent.mkdir()
    existing.write_text("{}", encoding="utf-8")
    missing = tmp_path / "other" / "missing.antennadesk"
    page.set_recent_projects(
        (
            RecentProject(existing, "Dipole", "2026-11-19T12:00:00+00:00"),
            RecentProject(missing, "Missing", "2026-11-18T12:00:00+00:00"),
        )
    )

    texts = [page._recent_list.item(index).text() for index in range(page._recent_list.count())]
    assert texts == ["dipole.antennadesk", "missing.antennadesk (missing)"]
    assert all(str(tmp_path) not in text for text in texts)

    page._recent_list.setCurrentRow(0)
    with qtbot.waitSignal(page.recent_requested) as opened:
        page._recent_list.itemActivated.emit(page._recent_list.item(0))
    assert opened.args == [str(existing)]

    with qtbot.waitSignal(page.recent_remove_requested) as removed:
        page._remove_recent_button.click()
    assert removed.args == [str(existing)]


def test_example_menu_and_reference_button_emit_requests(qtbot: QtBot) -> None:
    page = StartPage(Translator(Language.ENGLISH))
    qtbot.addWidget(page)

    assert page._example_button.text() == "Open example"
    with qtbot.waitSignal(page.example_requested) as example:
        page._example_actions["yagi"].trigger()
    assert example.args == ["yagi"]

    with qtbot.waitSignal(page.reference_requested):
        page._reference_button.click()


def test_start_page_retranslates_dynamic_entries(qtbot: QtBot, tmp_path: Path) -> None:
    translator = Translator(Language.ENGLISH)
    page = StartPage(translator)
    qtbot.addWidget(page)
    missing = tmp_path / "missing.antennadesk"
    page.set_recent_projects((RecentProject(missing, "Missing", ""),))

    translator.set_language(Language.SPANISH)
    page.retranslate()

    assert "faltante" in page._recent_list.item(0).text()
    assert page._example_button.text() == "Abrir ejemplo"
    assert page._reference_button.text() == "Biblioteca de diseños de referencia"
