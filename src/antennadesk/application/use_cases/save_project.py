# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Save a project through the repository port."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...domain.common.validation import raise_if_errors
from ...domain.projects.project import Project
from ..ports.project_repository import ProjectRepository


@dataclass(frozen=True, slots=True)
class SaveProject:
    repository: ProjectRepository

    def prepare(self, project: Project) -> bytes:
        """Validate and serialize a project without writing it to disk."""

        raise_if_errors(project.validate())
        return self.repository.prepare_payload(project)

    def write(self, path: Path, payload: bytes) -> None:
        """Write an already prepared payload atomically."""

        self.repository.write_payload(path, payload)

    def execute(self, project: Project, path: Path) -> None:
        self.write(path, self.prepare(project))
