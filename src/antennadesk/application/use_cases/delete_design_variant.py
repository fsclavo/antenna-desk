# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Delete a design variant, keeping at least one."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from ...domain.common.time import utc_now
from ...domain.projects.project import Project


@dataclass(frozen=True, slots=True)
class DeleteDesignVariantCommand:
    project: Project
    design_id: UUID
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class DeleteDesignVariant:
    def execute(self, command: DeleteDesignVariantCommand) -> Project:
        command.project.design_by_id(command.design_id)
        remaining = tuple(
            design for design in command.project.designs if design.id != command.design_id
        )
        if not remaining:
            raise ValueError("cannot delete the last design variant")
        timestamp = command.updated_at if command.updated_at is not None else utc_now()
        return replace(
            command.project,
            designs=remaining,
            updated_at=timestamp,
        )
