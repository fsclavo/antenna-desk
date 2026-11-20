# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Recent-project list and start-page synchronization."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtWidgets import QWidget

from .i18n import Translator
from .recent_projects import RecentProjectsStore
from .widgets.start_page import StartPage


@dataclass(frozen=True, slots=True)
class RecentProjectActions:
    store: RecentProjectsStore
    start_page: StartPage
    parent: QWidget
    translator: Translator
    open_path: Callable[[Path, bool], bool]
    show_error: Callable[[str], None]

    def refresh(self) -> None:
        self.start_page.set_recent_projects(self.store.load())

    def open(self, path: Path) -> bool:
        if not path.is_file():
            self.show_error(
                self.translator.t(
                    "error.open",
                    message=self.translator.t("error.file_missing", name=path.name),
                )
            )
            self.store.remove(path)
            self.refresh()
            return False
        return self.open_path(path, True)

    def remove(self, path: Path) -> None:
        self.store.remove(path)
        self.refresh()

    def restore_last(self, *, has_project: bool) -> str | None:
        if has_project:
            return None
        entries = self.store.load()
        if not entries:
            return None
        path = entries[0].path
        if not path.is_file():
            self.store.remove(path)
            self.refresh()
            return "status.recent_missing"
        if not self.open_path(path, False):
            self.store.remove(path)
            self.refresh()
            return "status.recent_missing"
        return None
