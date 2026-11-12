# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run the same comparison basis across several designs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from ...domain.antennas.antenna import AntennaModel
from ...domain.simulation.result import SimulationResult
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

ComparisonProgress = Callable[[int, int, str], None]


@dataclass(frozen=True, slots=True)
class ComparisonRun:
    """One design/model/spec tuple in the comparison batch."""

    design_id: UUID
    name: str
    model: AntennaModel
    spec: SimulationSpec


@dataclass(frozen=True, slots=True)
class ComparisonDesignResult:
    """The outcome for one comparison run."""

    design_id: UUID
    result: SimulationResult | None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class CompareDesignsCommand:
    runs: tuple[ComparisonRun, ...]
    cancel_token: CancelToken | None = None
    progress_callback: ComparisonProgress | None = None


@dataclass(frozen=True, slots=True)
class ComparisonOutcome:
    results: tuple[ComparisonDesignResult, ...]
    cancelled: bool = False


@dataclass(frozen=True, slots=True)
class CompareDesigns:
    solver: AntennaSolver

    def execute(self, command: CompareDesignsCommand) -> ComparisonOutcome:
        total = len(command.runs)
        results: list[ComparisonDesignResult] = []
        cancelled = False
        run_simulation = RunSimulation(self.solver)
        for index, run in enumerate(command.runs, start=1):
            if command.cancel_token is not None and command.cancel_token.is_cancelled():
                cancelled = True
                break
            try:
                result = run_simulation.execute(
                    RunSimulationCommand(
                        model=run.model,
                        spec=run.spec,
                        cancel_token=command.cancel_token,
                    )
                )
            except Exception as exc:
                results.append(
                    ComparisonDesignResult(
                        design_id=run.design_id,
                        result=None,
                        error=str(exc),
                    )
                )
            else:
                results.append(
                    ComparisonDesignResult(
                        design_id=run.design_id,
                        result=result,
                    )
                )
            if command.progress_callback is not None:
                command.progress_callback(index, total, run.name)
            if command.cancel_token is not None and command.cancel_token.is_cancelled():
                cancelled = True
                break
        return ComparisonOutcome(results=tuple(results), cancelled=cancelled)
