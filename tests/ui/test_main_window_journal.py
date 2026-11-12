# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project journal integration in the main window."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from main_window_support import FakeSolver
from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.journal import JournalEntry, JournalEntryKind
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem

NOW = datetime(2026, 11, 12, 21, 0, tzinfo=UTC)


def _entry(project: Project) -> JournalEntry:
    design = project.designs[0]
    return JournalEntry(
        id=uuid4(),
        created_at=NOW,
        title="First field check",
        kind=JournalEntryKind.MEASUREMENT,
        body="SWR 1.4 at 7.100 MHz.",
        design_id=design.id,
    )


def test_journal_action_is_available_and_retranslates(window: MainWindow) -> None:
    assert window._journal_action in window._tools_menu.actions()
    assert window._journal_action.isEnabled()
    assert window._journal_action.text() == "Project Journal..."
    assert "snapshots" in window._journal_action.toolTip()

    window._set_language(Language.SPANISH)

    assert window._journal_action.text() == "Bitácora del proyecto..."
    assert "instantáneas" in window._journal_action.toolTip()
    window._set_language(Language.ENGLISH)


def test_journal_action_cancels_without_changing_the_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    before = window._project

    class FakeJournalDialog:
        opened = False

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> int:
            type(self).opened = True
            return 0

        def result_project(self) -> Project:
            raise AssertionError("a cancelled dialog must not be queried")

    monkeypatch.setattr(main_window_module, "JournalDialog", FakeJournalDialog)

    window.edit_project_journal()

    assert FakeJournalDialog.opened is True
    assert window._project == before
    assert window._dirty is False
    assert window._undo_stack.canUndo() is False


def test_journal_entry_change_is_dirty_and_undoable(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    before = window._project
    entry = _entry(before)
    updated = before.with_journal_entry(entry, updated_at=NOW)

    class FakeJournalDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> int:
            return 1

        def result_project(self) -> Project:
            return updated

    monkeypatch.setattr(main_window_module, "JournalDialog", FakeJournalDialog)

    window.edit_project_journal()

    assert window._project == updated
    assert window._project.journal_entries == (entry,)
    assert window._dirty is True
    assert window._undo_stack.canUndo() is True

    window._undo_stack.undo()
    assert window._project.journal_entries == ()
    restored = window._project
    assert replace(restored, updated_at=before.updated_at) == before

    window._undo_stack.redo()
    replayed = window._project
    assert replayed.journal_entries == (entry,)
    assert replace(replayed, updated_at=updated.updated_at) == updated
    window._dirty = False


def test_journal_action_requires_a_project(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(window)
    errors: list[str] = []
    monkeypatch.setattr(window, "_show_error", errors.append)

    assert window._journal_action.isEnabled() is False
    window.edit_project_journal()

    assert errors == [window._translator.t("error.no_project")]
    window.close()
