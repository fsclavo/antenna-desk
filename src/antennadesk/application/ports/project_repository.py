# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project repository port."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ...domain.projects.project import Project
from ..project_payload import PreparedProject
from ..project_session import ProjectSession


class ProjectRepository(Protocol):
    """Persistence boundary for native project files."""

    def save(self, project: Project, path: Path) -> None:
        """Write *project* to *path*, replacing any existing file atomically."""

    def open_session(self, path: Path) -> ProjectSession:
        """Open *path* with lazy simulation runs."""

    def open_design_only(self, path: Path) -> Project:
        """Open *path* without its simulation runs, for recovery."""

    def prepare_payload(self, project: Project) -> PreparedProject:
        """Serialize and size-check *project* for a later atomic write.

        The returned payload may use a bounded temporary spool instead of
        holding the whole container in memory. Raises
        ``ProjectPayloadTooLargeError`` when the payload exceeds a storage or
        reopen limit.
        """

    def prepare_session_payload(
        self,
        session: ProjectSession,
        project: Project,
        *,
        retained_only: bool = False,
    ) -> PreparedProject:
        """Prepare a save that streams unloaded runs from the session source."""

    def write_payload(self, path: Path, payload: PreparedProject) -> None:
        """Write a prepared payload atomically."""

    def load(self, path: Path) -> Project:
        """Read and validate a project from *path*."""

    def serialized_size(self, project: Project) -> int:
        """Return the approximate native-file size in bytes."""
