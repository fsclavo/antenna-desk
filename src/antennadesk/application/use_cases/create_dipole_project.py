"""Create a project containing a horizontal half-wave dipole."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ...domain.antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from ...domain.common.ids import new_id
from ...domain.common.time import utc_now
from ...domain.projects.project import DesignVariant, Project


@dataclass(frozen=True, slots=True)
class CreateDipoleProjectCommand:
    project_name: str
    variant_name: str
    parameters: DipoleParameters
    description: str = ""


@dataclass(frozen=True, slots=True)
class CreateDipoleProject:
    """Build a new project from user-facing dipole parameters."""

    def execute(
        self,
        command: CreateDipoleProjectCommand,
        *,
        project_id: UUID | None = None,
        design_id: UUID | None = None,
        now: datetime | None = None,
    ) -> Project:
        project_name = command.project_name.strip()
        variant_name = command.variant_name.strip()
        if not project_name:
            raise ValueError("project name must not be empty")
        if not variant_name:
            raise ValueError("variant name must not be empty")

        timestamp = now if now is not None else utc_now()
        antenna = command.parameters.to_antenna(name=variant_name)
        design = DesignVariant(
            id=design_id if design_id is not None else new_id(),
            name=variant_name,
            antenna_type=ANTENNA_TYPE_WIRE_DIPOLE,
            parameters=command.parameters,
            antenna=antenna,
        )

        return Project(
            id=project_id if project_id is not None else new_id(),
            name=project_name,
            description=command.description,
            created_at=timestamp,
            updated_at=timestamp,
            designs=(design,),
        )
