# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prepare a project payload without blocking the Qt event loop."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from ...application.use_cases.save_project import SaveProject
from ...domain.projects.project import Project


class SaveProjectWorker(QObject):
    """Serialize and compress a project in a worker thread."""

    prepared = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        save_project: SaveProject,
        project: Project,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._save_project = save_project
        self._project = project

    @Slot()
    def run(self) -> None:
        try:
            payload = self._save_project.prepare(self._project)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.prepared.emit(payload)
