# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run a simulation once per selected amateur band."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from uuid import UUID

from ...domain.antennas.antenna import AntennaModel
from ...domain.common.ids import new_id
from ...domain.common.time import utc_now
from ...domain.common.validation import Diagnostic, Severity
from ...domain.simulation.band_result import BandAnalysisResult, BandResult
from ...domain.simulation.bands import AmateurBand
from ...domain.simulation.result import SimulationResult, SimulationStatus
from ...domain.simulation.solver import SolverMetadata
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

BandProgressCallback = Callable[[int, int, AmateurBand], None]


@dataclass(frozen=True, slots=True)
class BandSimulationRequest:
    """One band and the simulation spec that covers it."""

    band: AmateurBand
    spec: SimulationSpec

    def __post_init__(self) -> None:
        if not self.band.name.strip():
            raise ValueError("band name must not be empty")


@dataclass(frozen=True, slots=True)
class AnalyzeBandsCommand:
    design_id: UUID
    model: AntennaModel
    requests: tuple[BandSimulationRequest, ...]
    cancel_token: CancelToken | None = None
    progress_callback: BandProgressCallback | None = None
    parallel_workers: int = 1

    def __post_init__(self) -> None:
        if not self.requests:
            raise ValueError("a band analysis requires at least one band")
        if not 1 <= self.parallel_workers <= 8:
            raise ValueError("parallel_workers must be between 1 and 8")


@dataclass(frozen=True, slots=True)
class AnalyzeBands:
    """Run the existing single-band solver for each requested band.

    When ``parallel_workers`` is greater than one, independent bands run in
    bounded batches. Results and progress remain in request order, and
    cancellation is propagated to every in-flight solver process.
    """

    solver: AntennaSolver

    def execute(self, command: AnalyzeBandsCommand) -> BandAnalysisResult:
        if command.parallel_workers == 1:
            return self._execute_sequential(command)
        return self._execute_parallel(command)

    def _execute_sequential(self, command: AnalyzeBandsCommand) -> BandAnalysisResult:
        results: list[BandResult] = []
        total = len(command.requests)
        for index, request in enumerate(command.requests, start=1):
            if self._is_cancelled(command):
                results.append(
                    BandResult(
                        band=request.band,
                        result=self._cancelled_result(request.spec),
                    )
                )
                break
            result = self._run_request(command, request)
            results.append(BandResult(band=request.band, result=result))
            self._report_progress(command, index, total, request.band)
            if result.status is SimulationStatus.CANCELLED or self._is_cancelled(command):
                break

        return self._analysis(command, results)

    def _execute_parallel(self, command: AnalyzeBandsCommand) -> BandAnalysisResult:
        results: list[BandResult] = []
        total = len(command.requests)
        worker_count = command.parallel_workers
        executor = ThreadPoolExecutor(max_workers=worker_count)
        try:
            start = 0
            while start < total:
                if self._is_cancelled(command):
                    request = command.requests[start]
                    results.append(
                        BandResult(
                            band=request.band,
                            result=self._cancelled_result(request.spec),
                        )
                    )
                    break
                chunk = command.requests[start : start + worker_count]
                futures = [
                    executor.submit(self._run_request, command, request) for request in chunk
                ]
                chunk_results = [future.result() for future in futures]
                stop = False
                for offset, (request, result) in enumerate(
                    zip(chunk, chunk_results, strict=True),
                    start=start + 1,
                ):
                    results.append(BandResult(band=request.band, result=result))
                    self._report_progress(command, offset, total, request.band)
                    if result.status is SimulationStatus.CANCELLED or self._is_cancelled(command):
                        stop = True
                if stop:
                    break
                start += len(chunk)
        finally:
            executor.shutdown(wait=True, cancel_futures=True)

        return self._analysis(command, results)

    def _run_request(
        self,
        command: AnalyzeBandsCommand,
        request: BandSimulationRequest,
    ) -> SimulationResult:
        try:
            return RunSimulation(self.solver).execute(
                RunSimulationCommand(
                    model=command.model,
                    spec=request.spec,
                    cancel_token=command.cancel_token,
                )
            )
        except Exception as exc:
            return self._error_result(request.spec, str(exc))

    @staticmethod
    def _is_cancelled(command: AnalyzeBandsCommand) -> bool:
        return command.cancel_token is not None and command.cancel_token.is_cancelled()

    @staticmethod
    def _report_progress(
        command: AnalyzeBandsCommand,
        index: int,
        total: int,
        band: AmateurBand,
    ) -> None:
        if command.progress_callback is not None:
            command.progress_callback(index, total, band)

    @staticmethod
    def _analysis(
        command: AnalyzeBandsCommand,
        results: list[BandResult],
    ) -> BandAnalysisResult:
        return BandAnalysisResult(
            design_id=command.design_id,
            batch_id=new_id(),
            created_at=utc_now(),
            bands=tuple(results),
        )

    def _solver_metadata(self) -> SolverMetadata:
        try:
            return self.solver.version()
        except Exception:
            return SolverMetadata(name="unknown", version="unknown")

    def _error_result(self, spec: SimulationSpec, message: str) -> SimulationResult:
        return SimulationResult(
            status=SimulationStatus.ERROR,
            spec=spec,
            model_fingerprint="",
            solver=self._solver_metadata(),
            frequencies=(),
            diagnostics=(
                Diagnostic(
                    code="band.error",
                    severity=Severity.ERROR,
                    message=message,
                    field="bands",
                ),
            ),
        )

    def _cancelled_result(self, spec: SimulationSpec) -> SimulationResult:
        return SimulationResult(
            status=SimulationStatus.CANCELLED,
            spec=spec,
            model_fingerprint="",
            solver=self._solver_metadata(),
            frequencies=(),
            diagnostics=(
                Diagnostic(
                    code="band.cancelled",
                    severity=Severity.INFO,
                    message="band analysis cancelled before this band ran",
                    field="bands",
                ),
            ),
        )
