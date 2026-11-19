# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Recent-project list stored in QSettings, without a project schema change."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QSettings

RECENT_PROJECTS_KEY = "recent/projects"
MAX_RECENT_PROJECTS = 10


@dataclass(frozen=True, slots=True)
class RecentProject:
    path: Path
    name: str
    opened_at: str

    @property
    def display_name(self) -> str:
        """Return only the file name, never the full private path."""

        return self.path.name or self.name


class RecentProjectsStore(Protocol):
    def load(self) -> tuple[RecentProject, ...]: ...

    def add(
        self,
        path: Path,
        name: str,
        *,
        opened_at: str | None = None,
    ) -> None: ...

    def remove(self, path: Path) -> None: ...


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _absolute(path: Path) -> Path:
    return Path(path).expanduser().resolve()


def _serialize(entries: tuple[RecentProject, ...]) -> str:
    return json.dumps(
        [
            {
                "path": str(entry.path),
                "name": entry.name,
                "opened_at": entry.opened_at,
            }
            for entry in entries
        ],
        ensure_ascii=True,
        separators=(",", ":"),
    )


def _parse(raw: object) -> tuple[RecentProject, ...]:
    if not isinstance(raw, str) or not raw.strip():
        return ()
    try:
        values = json.loads(raw)
    except (TypeError, ValueError):
        return ()
    if not isinstance(values, list):
        return ()
    entries: list[RecentProject] = []
    for value in values:
        if not isinstance(value, dict):
            continue
        raw_path = value.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            continue
        path = Path(raw_path)
        name = value.get("name")
        opened_at = value.get("opened_at")
        entries.append(
            RecentProject(
                path=path,
                name=name if isinstance(name, str) and name.strip() else path.name,
                opened_at=opened_at if isinstance(opened_at, str) else "",
            )
        )
    return tuple(entries[:MAX_RECENT_PROJECTS])


class QSettingsRecentProjectsStore:
    """Persist the recent list per user in the platform-native settings."""

    def __init__(self, settings: QSettings | None = None) -> None:
        self._settings = settings if settings is not None else QSettings()

    def load(self) -> tuple[RecentProject, ...]:
        return _parse(self._settings.value(RECENT_PROJECTS_KEY, ""))

    def add(
        self,
        path: Path,
        name: str,
        *,
        opened_at: str | None = None,
    ) -> None:
        target = _absolute(path)
        entry = RecentProject(
            path=target,
            name=name.strip() or target.name,
            opened_at=opened_at or _timestamp(),
        )
        entries = (entry, *(item for item in self.load() if item.path != target))
        self._write(entries[:MAX_RECENT_PROJECTS])

    def remove(self, path: Path) -> None:
        target = _absolute(path)
        self._write(tuple(item for item in self.load() if item.path != target))

    def _write(self, entries: tuple[RecentProject, ...]) -> None:
        self._settings.setValue(RECENT_PROJECTS_KEY, _serialize(entries))
        self._settings.sync()


class InMemoryRecentProjectsStore:
    """Recent-project store used by tests and windows without persistence."""

    def __init__(self, entries: tuple[RecentProject, ...] = ()) -> None:
        self._entries = entries

    def load(self) -> tuple[RecentProject, ...]:
        return self._entries

    def add(
        self,
        path: Path,
        name: str,
        *,
        opened_at: str | None = None,
    ) -> None:
        target = _absolute(path)
        entry = RecentProject(
            path=target,
            name=name.strip() or target.name,
            opened_at=opened_at or _timestamp(),
        )
        self._entries = (
            entry,
            *(item for item in self._entries if item.path != target),
        )[:MAX_RECENT_PROJECTS]

    def remove(self, path: Path) -> None:
        target = _absolute(path)
        self._entries = tuple(item for item in self._entries if item.path != target)
