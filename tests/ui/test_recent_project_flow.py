# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Recent-project flow and one-click examples in the main window."""

from __future__ import annotations

from pathlib import Path

import pytest
from main_window_support import FakeSolver
from PySide6.QtWidgets import QInputDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.project import Project
from antennadesk.persistence.container import ProjectContainerRepository
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.preferences import InMemoryPreferencesStore
from antennadesk.ui.recent_projects import (
    InMemoryRecentProjectsStore,
    RecentProject,
)
from antennadesk.ui.units import UnitSystem


def _save_project(project: Project, path: Path) -> None:
    ProjectContainerRepository().save(project, path)


def test_open_project_records_and_removes_a_missing_recent(
    window: MainWindow,
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    path = tmp_path / "recent.antennadesk"
    _save_project(window._project, path)
    errors: list[str] = []
    monkeypatch.setattr(window, "_show_error", errors.append)

    window.open_recent_project(str(path))

    entries = window._recent_projects.load()
    assert [entry.path for entry in entries] == [path.resolve()]
    assert window._start_page._recent_list.item(0).text() == "recent.antennadesk"

    path.unlink()
    window.open_recent_project(str(path))

    assert window._recent_projects.load() == ()
    assert errors
    assert "file not found" in errors[0]
    assert window._start_page._recent_list.count() == 0


def test_save_project_records_the_file_as_recent(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from PySide6.QtWidgets import QFileDialog

    path = tmp_path / "saved.antennadesk"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(path), ""),
    )

    assert window.save_project_as() is True

    entries = window._recent_projects.load()
    assert [entry.path for entry in entries] == [path.resolve()]
    assert window._start_page._recent_list.item(0).text() == "saved.antennadesk"
    window._dirty = False


def test_remove_recent_project_updates_the_start_page(window: MainWindow, tmp_path: Path) -> None:
    path = tmp_path / "remove-me.antennadesk"
    window._recent_projects.add(path, "Remove me")
    window._refresh_start_page_recents()
    assert window._start_page._recent_list.count() == 1

    window.remove_recent_project(str(path))

    assert window._recent_projects.load() == ()
    assert window._start_page._recent_list.count() == 0


def test_open_example_creates_a_normal_project_without_a_name_prompt(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        QInputDialog,
        "getText",
        lambda *args, **kwargs: pytest.fail("example must not prompt for a name"),
    )
    window._dirty = False

    window.open_example("yagi")

    assert window._project is not None
    assert window._project.designs[0].antenna_type == "yagi"
    assert window._project.designs[0].name == "Initial"
    assert window._current_path is None
    assert window._dirty is True
    window._dirty = False


def test_restore_last_project_opens_the_newest_recent(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "restore.antennadesk"
    _save_project(sample_project, path)
    recent = InMemoryRecentProjectsStore(
        (RecentProject(path.resolve(), sample_project.name, "2026-11-19T12:00:00+00:00"),)
    )
    window = MainWindow(
        ProjectContainerRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preferences=InMemoryPreferencesStore(),
        recent_projects=recent,
    )
    qtbot.addWidget(window)

    window._restore_last_project()

    assert window._project is not None
    assert window._project.name == sample_project.name
    assert window._current_path == path.resolve()
    window._dirty = False
    window.close()
