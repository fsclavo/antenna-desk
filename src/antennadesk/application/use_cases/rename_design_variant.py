# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Rename a design variant without changing its geometry."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from ...domain.common.time import utc_now
from ...domain.projects.project import Project


@dataclass(frozen=True, slots=True)
class RenameDesignVariantCommand:
    project: Project
    design_id: UUID
    name: str
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class RenameDesignVariant:
    def execute(self, command: RenameDesignVariantCommand) -> Project:
        name = command.name.strip()
        if not name:
            raise ValueError("variant name must not be empty")
        design = command.project.design_by_id(command.design_id)
        renamed = replace(design, name=name)
        timestamp = command.updated_at if command.updated_at is not None else utc_now()
        return command.project.with_design(renamed, updated_at=timestamp)
