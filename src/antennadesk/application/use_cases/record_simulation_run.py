# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Record an immutable simulation run in a project."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ...domain.common.ids import new_id
from ...domain.common.time import utc_now
from ...domain.projects.project import Project
from ...domain.simulation.result import SimulationResult
from ...domain.simulation.run import SimulationRun


@dataclass(frozen=True, slots=True)
class RecordSimulationRunCommand:
    project: Project
    design_id: UUID
    result: SimulationResult
    run_id: UUID | None = None
    created_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class RecordSimulationRun:
    def execute(self, command: RecordSimulationRunCommand) -> Project:
        command.project.design_by_id(command.design_id)
        timestamp = command.created_at if command.created_at is not None else utc_now()
        run = SimulationRun(
            id=command.run_id if command.run_id is not None else new_id(),
            design_id=command.design_id,
            created_at=timestamp,
            result=command.result,
        )
        return command.project.with_simulation_run(run, updated_at=timestamp)
