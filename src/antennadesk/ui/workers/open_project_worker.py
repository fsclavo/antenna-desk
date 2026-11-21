# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Open and validate a project without blocking the Qt event loop."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from ...application.project_session import ProjectSession
from ...application.use_cases.open_project import OpenProject, OpenProjectSession
from ...domain.projects.project import Project


class OpenProjectWorker(QObject):
    """Read and validate a project container in a worker thread."""

    finished = Signal(object)
    failed = Signal(object)

    def __init__(
        self,
        open_project: OpenProject | OpenProjectSession,
        path: Path,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._open_project = open_project
        self._path = path

    @Slot()
    def run(self) -> None:
        try:
            project: Project | ProjectSession = self._open_project.execute(self._path)
        except Exception as exc:
            self.failed.emit(exc)
            return
        self.finished.emit(project)
