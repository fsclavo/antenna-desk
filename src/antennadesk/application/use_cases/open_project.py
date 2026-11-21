# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Open and validate a project through the repository port."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...domain.common.validation import raise_if_errors
from ...domain.projects.project import Project
from ..ports.project_repository import ProjectRepository
from ..project_session import ProjectSession


@dataclass(frozen=True, slots=True)
class OpenProject:
    repository: ProjectRepository

    def execute(self, path: Path) -> Project:
        project = self.repository.load(path)
        raise_if_errors(project.validate())
        return project


@dataclass(frozen=True, slots=True)
class OpenProjectSession:
    """Open project metadata and designs while keeping runs lazy."""

    repository: ProjectRepository

    def execute(self, path: Path) -> ProjectSession:
        session = self.repository.open_session(path)
        raise_if_errors(session.project.validate())
        return session
