# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run a simulation once per selected amateur band."""

from __future__ import annotations

from collections.abc import Callable
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

    def __post_init__(self) -> None:
        if not self.requests:
            raise ValueError("a band analysis requires at least one band")


@dataclass(frozen=True, slots=True)
class AnalyzeBands:
    """Run the existing single-band solver for each requested band."""

    solver: AntennaSolver

    def execute(self, command: AnalyzeBandsCommand) -> BandAnalysisResult:
        results: list[BandResult] = []
        total = len(command.requests)
        for index, request in enumerate(command.requests, start=1):
            if command.cancel_token is not None and command.cancel_token.is_cancelled():
                results.append(
                    BandResult(
                        band=request.band,
                        result=self._cancelled_result(request.spec),
                    )
                )
                break
            try:
                result = RunSimulation(self.solver).execute(
                    RunSimulationCommand(
                        model=command.model,
                        spec=request.spec,
                        cancel_token=command.cancel_token,
                    )
                )
            except Exception as exc:
                result = self._error_result(request.spec, str(exc))
            results.append(BandResult(band=request.band, result=result))
            if command.progress_callback is not None:
                command.progress_callback(index, total, request.band)
            if result.status is SimulationStatus.CANCELLED or (
                command.cancel_token is not None and command.cancel_token.is_cancelled()
            ):
                break

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
