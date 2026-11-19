# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Recent-project persistence and privacy."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings

from antennadesk.ui.recent_projects import (
    MAX_RECENT_PROJECTS,
    InMemoryRecentProjectsStore,
    QSettingsRecentProjectsStore,
    RecentProject,
)


def _store(path: Path) -> QSettingsRecentProjectsStore:
    return QSettingsRecentProjectsStore(QSettings(str(path), QSettings.Format.IniFormat))


def test_recent_projects_round_trip_and_show_only_the_file_name(tmp_path: Path) -> None:
    settings = tmp_path / "settings.ini"
    project = tmp_path / "secret-folder" / "dipole.antennadesk"
    project.parent.mkdir()

    store = _store(settings)
    store.add(project, "40 m dipole", opened_at="2026-11-19T12:00:00+00:00")

    entries = _store(settings).load()
    assert len(entries) == 1
    assert entries[0].name == "40 m dipole"
    assert entries[0].display_name == "dipole.antennadesk"
    assert str(project.parent) not in entries[0].display_name


def test_recent_projects_deduplicate_and_keep_the_newest_first(tmp_path: Path) -> None:
    settings = tmp_path / "settings.ini"
    first = tmp_path / "first.antennadesk"
    second = tmp_path / "second.antennadesk"
    store = _store(settings)

    store.add(first, "First", opened_at="2026-11-18T12:00:00+00:00")
    store.add(second, "Second", opened_at="2026-11-19T12:00:00+00:00")
    store.add(first, "First updated", opened_at="2026-11-20T12:00:00+00:00")

    entries = store.load()
    assert [entry.path for entry in entries] == [first.resolve(), second.resolve()]
    assert entries[0].name == "First updated"


def test_recent_projects_are_bounded_and_removable(tmp_path: Path) -> None:
    settings = tmp_path / "settings.ini"
    store = _store(settings)

    for index in range(MAX_RECENT_PROJECTS + 3):
        store.add(
            tmp_path / f"project-{index}.antennadesk",
            f"Project {index}",
            opened_at=f"2026-11-19T12:00:{index:02d}+00:00",
        )

    entries = store.load()
    assert len(entries) == MAX_RECENT_PROJECTS

    store.remove(entries[0].path)
    assert len(store.load()) == MAX_RECENT_PROJECTS - 1


def test_malformed_recent_settings_are_ignored(tmp_path: Path) -> None:
    settings = tmp_path / "settings.ini"
    qsettings = QSettings(str(settings), QSettings.Format.IniFormat)
    qsettings.setValue("recent/projects", "{not json")
    qsettings.sync()

    assert _store(settings).load() == ()


def test_in_memory_store_matches_the_qsettings_contract(tmp_path: Path) -> None:
    store = InMemoryRecentProjectsStore(
        (RecentProject(tmp_path / "old.antennadesk", "Old", "2026-11-18"),)
    )
    new = tmp_path / "new.antennadesk"

    store.add(new, "New", opened_at="2026-11-19T12:00:00+00:00")

    assert [entry.display_name for entry in store.load()] == [
        "new.antennadesk",
        "old.antennadesk",
    ]
    store.remove(new)
    assert [entry.display_name for entry in store.load()] == ["old.antennadesk"]
