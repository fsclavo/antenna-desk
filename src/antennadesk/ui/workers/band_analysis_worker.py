# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run a band analysis off the GUI thread."""

from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import QObject, Signal, Slot

from ...application.ports.antenna_solver import AntennaSolver
from ...application.ports.cancellation import CancelToken
from ...application.use_cases.analyze_bands import (
    AnalyzeBands,
    AnalyzeBandsCommand,
    BandSimulationRequest,
)
from ...domain.antennas.antenna import AntennaModel
from ...domain.simulation.band_result import BandAnalysisResult


class BandAnalysisWorker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        solver: AntennaSolver,
        design_id: UUID,
        model: AntennaModel,
        requests: tuple[BandSimulationRequest, ...],
        cancel_token: CancelToken,
        parallel_workers: int = 1,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._solver = solver
        self._design_id = design_id
        self._model = model
        self._requests = requests
        self._cancel_token = cancel_token
        self._parallel_workers = parallel_workers

    @Slot()
    def run(self) -> None:
        try:
            result: BandAnalysisResult = AnalyzeBands(self._solver).execute(
                AnalyzeBandsCommand(
                    design_id=self._design_id,
                    model=self._model,
                    requests=self._requests,
                    cancel_token=self._cancel_token,
                    parallel_workers=self._parallel_workers,
                    progress_callback=lambda index, total, band: self.progress.emit(
                        index, total, band.name
                    ),
                )
            )
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)
