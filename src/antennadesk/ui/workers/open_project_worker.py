# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Open and validate a project without blocking the Qt event loop."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from ...application.use_cases.open_project import OpenProject
from ...domain.projects.project import Project


class OpenProjectWorker(QObject):
    """Read, migrate, and validate a project in a worker thread."""

    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        open_project: OpenProject,
        path: Path,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._open_project = open_project
        self._path = path

    @Slot()
    def run(self) -> None:
        try:
            project: Project = self._open_project.execute(self._path)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(project)
