"""Run a simulation through the solver port."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.antennas.antenna import AntennaModel
from ...domain.common.validation import raise_if_errors
from ...domain.simulation.result import SimulationResult
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken


@dataclass(frozen=True, slots=True)
class RunSimulationCommand:
    model: AntennaModel
    spec: SimulationSpec
    cancel_token: CancelToken | None = None


@dataclass(frozen=True, slots=True)
class RunSimulation:
    solver: AntennaSolver

    def execute(self, command: RunSimulationCommand) -> SimulationResult:
        diagnostics = self.solver.validate(command.model, command.spec)
        raise_if_errors(diagnostics)
        return self.solver.run(
            command.model,
            command.spec,
            cancel_token=command.cancel_token,
        )
