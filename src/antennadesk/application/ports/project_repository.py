# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project repository port."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ...domain.projects.project import Project


class ProjectRepository(Protocol):
    """Persistence boundary for native project files."""

    def save(self, project: Project, path: Path) -> None:
        """Write *project* to *path*, replacing any existing file atomically."""

    def load(self, path: Path) -> Project:
        """Read and validate a project from *path*."""
