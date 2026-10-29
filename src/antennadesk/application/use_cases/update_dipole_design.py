# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Replace a dipole design's parameters without mutating previous snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ...domain.antennas.dipole import DipoleParameters
from ...domain.common.time import utc_now
from ...domain.projects.project import Project


@dataclass(frozen=True, slots=True)
class UpdateDipoleDesignCommand:
    project: Project
    design_id: UUID
    parameters: DipoleParameters
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UpdateDipoleDesign:
    def execute(self, command: UpdateDipoleDesignCommand) -> Project:
        design = command.project.design_by_id(command.design_id)
        updated_design = design.with_parameters(command.parameters)
        timestamp = command.updated_at if command.updated_at is not None else utc_now()
        return command.project.with_design(updated_design, updated_at=timestamp)
