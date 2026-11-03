# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Replace a design's parameters without mutating previous snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ...domain.antennas.design import AntennaDesignParameters
from ...domain.antennas.load import LumpedLoad
from ...domain.antennas.transmission_line import TransmissionLine
from ...domain.common.time import utc_now
from ...domain.projects.project import Project


@dataclass(frozen=True, slots=True)
class UpdateDipoleDesignCommand:
    project: Project
    design_id: UUID
    parameters: AntennaDesignParameters
    loads: tuple[LumpedLoad, ...] | None = None
    transmission_lines: tuple[TransmissionLine, ...] | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UpdateDipoleDesign:
    def execute(self, command: UpdateDipoleDesignCommand) -> Project:
        design = command.project.design_by_id(command.design_id)
        updated_design = design.with_parameters(command.parameters)
        if command.loads is not None:
            updated_design = updated_design.with_loads(command.loads)
        if command.transmission_lines is not None:
            updated_design = updated_design.with_transmission_lines(command.transmission_lines)
        timestamp = command.updated_at if command.updated_at is not None else utc_now()
        return command.project.with_design(updated_design, updated_at=timestamp)


UpdateDesignVariantCommand = UpdateDipoleDesignCommand
UpdateDesignVariant = UpdateDipoleDesign
