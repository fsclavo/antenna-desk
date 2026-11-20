# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Application ports for solver-backed export and pre-flight."""

from __future__ import annotations

from typing import Protocol

from ...domain.design.preflight import PreflightReport
from ...domain.projects.project import DesignVariant, Project
from ...domain.simulation.result import SimulationResult
from ...domain.simulation.solver import SolverMetadata
from ...domain.simulation.spec import SimulationSpec


class PreflightRunner(Protocol):
    def __call__(
        self,
        project: Project,
        design: DesignVariant,
        spec: SimulationSpec,
        *,
        result: SimulationResult | None = None,
    ) -> PreflightReport: ...


class NecDeckExporter(Protocol):
    def __call__(
        self,
        project: Project,
        design: DesignVariant,
        spec: SimulationSpec,
        solver: SolverMetadata | None,
    ) -> str: ...
