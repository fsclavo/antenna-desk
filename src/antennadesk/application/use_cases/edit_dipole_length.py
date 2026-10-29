# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Edit the length of a dipole without mutating previous project snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ...domain.antennas.dipole import DipoleParameters
from ...domain.common.time import utc_now
from ...domain.projects.project import Project


@dataclass(frozen=True, slots=True)
class EditDipoleLengthCommand:
    project: Project
    design_id: UUID
    total_length_m: float
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class EditDipoleLength:
    """Return a new project with one dipole length changed."""

    def execute(self, command: EditDipoleLengthCommand) -> Project:
        design = command.project.design_by_id(command.design_id)
        if not isinstance(design.parameters, DipoleParameters):
            raise ValueError("length editing is only available for wire dipoles")
        parameters = design.parameters.with_length(command.total_length_m)
        updated_design = design.with_parameters(parameters)
        timestamp = command.updated_at if command.updated_at is not None else utc_now()
        return command.project.with_design(updated_design, updated_at=timestamp)
