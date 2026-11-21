# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prepare a project payload without blocking the Qt event loop."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from ...application.project_session import ProjectSession
from ...application.use_cases.save_project import SaveProject
from ...domain.projects.project import Project


class SaveProjectWorker(QObject):
    """Serialize and compress a project in a worker thread."""

    prepared = Signal(object)
    failed = Signal(object)

    def __init__(
        self,
        save_project: SaveProject,
        project: Project,
        session: ProjectSession | None = None,
        *,
        retained_only: bool = False,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._save_project = save_project
        self._project = project
        self._session = session
        self._retained_only = retained_only

    @Slot()
    def run(self) -> None:
        try:
            if self._session is None:
                payload = self._save_project.prepare(self._project)
            else:
                payload = self._save_project.prepare_session(
                    self._project,
                    self._session,
                    retained_only=self._retained_only,
                )
        except Exception as exc:
            # Keep the exception instance so callers can react to structured
            # failures such as a project that would exceed the reopen limit.
            self.failed.emit(exc)
            return
        self.prepared.emit(payload)
