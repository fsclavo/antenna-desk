# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Duplicate a design variant with a new name and identity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ...domain.common.ids import new_id
from ...domain.common.time import utc_now
from ...domain.projects.project import DesignVariant, Project


@dataclass(frozen=True, slots=True)
class AddDesignVariantCommand:
    project: Project
    source_design_id: UUID
    name: str
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class AddDesignVariant:
    def execute(self, command: AddDesignVariantCommand) -> Project:
        name = command.name.strip()
        if not name:
            raise ValueError("variant name must not be empty")
        source = command.project.design_by_id(command.source_design_id)
        variant = DesignVariant(
            id=new_id(),
            name=name,
            antenna_type=source.antenna_type,
            parameters=source.parameters,
            antenna=source.antenna,
        )
        timestamp = command.updated_at if command.updated_at is not None else utc_now()
        return command.project.with_design(variant, updated_at=timestamp)
