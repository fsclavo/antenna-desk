# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run the solver off the GUI thread."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from ...application.ports.antenna_solver import AntennaSolver
from ...application.ports.cancellation import CancelToken
from ...application.use_cases.run_simulation import RunSimulation, RunSimulationCommand
from ...domain.antennas.antenna import AntennaModel
from ...domain.simulation.result import SimulationResult
from ...domain.simulation.spec import SimulationSpec


class SimulationWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        solver: AntennaSolver,
        model: AntennaModel,
        spec: SimulationSpec,
        cancel_token: CancelToken,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._solver = solver
        self._model = model
        self._spec = spec
        self._cancel_token = cancel_token

    @Slot()
    def run(self) -> None:
        try:
            result: SimulationResult = RunSimulation(self._solver).execute(
                RunSimulationCommand(
                    model=self._model,
                    spec=self._spec,
                    cancel_token=self._cancel_token,
                )
            )
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)
