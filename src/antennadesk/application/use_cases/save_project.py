# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Save a project through the repository port."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...domain.common.validation import raise_if_errors
from ...domain.projects.project import Project
from ..ports.project_repository import ProjectRepository
from ..project_payload import PreparedProject
from ..project_session import ProjectSession


@dataclass(frozen=True, slots=True)
class SaveProject:
    repository: ProjectRepository

    def prepare(self, project: Project) -> PreparedProject:
        """Validate and prepare a project for a later atomic write."""

        raise_if_errors(project.validate())
        return self.repository.prepare_payload(project)

    def prepare_session(
        self,
        project: Project,
        session: ProjectSession,
        *,
        retained_only: bool = False,
    ) -> PreparedProject:
        """Prepare a save that reuses unloaded run entries from the session."""

        raise_if_errors(project.validate())
        return self.repository.prepare_session_payload(
            session,
            project,
            retained_only=retained_only,
        )

    def write(self, path: Path, payload: PreparedProject) -> None:
        """Write an already prepared payload atomically."""

        self.repository.write_payload(path, payload)

    def execute(self, project: Project, path: Path) -> None:
        prepared = self.prepare(project)
        try:
            self.write(path, prepared)
        finally:
            prepared.close()
