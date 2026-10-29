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

    def execute(self, project: Project, path: Path) -> None:
        raise_if_errors(project.validate())
        self.repository.save(project, path)
