# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import threading
from dataclasses import replace
from uuid import uuid4

import pytest

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.application.use_cases.analyze_bands import (
    AnalyzeBands,
    AnalyzeBandsCommand,
    BandSimulationRequest,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.simulation.bands import amateur_band_by_id
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class FakeBandSolver:
    def __init__(self, *, fail_hz: float | None = None) -> None:
        self.fail_hz = fail_hz
        self.specs: list[SimulationSpec] = []

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="fake", version="1")

    def validate(self, model: object, spec: SimulationSpec) -> tuple:
        return ()

    def run(self, model: object, spec: SimulationSpec, **kwargs: object) -> SimulationResult:
        self.specs.append(spec)
        if self.fail_hz is not None and abs(spec.frequency_plan.start_hz - self.fail_hz) < 1.0:
            raise RuntimeError("solver failed")
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=spec.frequency_plan.start_hz,
                    feed_tag=1,
                    feed_segment=1,
                    impedance_ohm=complex(50.0, 0.0),
                    swr=1.5,
                    input_power_w=1.0,
                ),
            ),
        )


def _model():
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna()


def _request(band_id: str) -> BandSimulationRequest:
    band = amateur_band_by_id(band_id)
    assert band is not None
    return BandSimulationRequest(
        band=band,
        spec=SimulationSpec(frequency_plan=FrequencyPlan.sweep(band.start_hz, band.stop_hz, 5)),
    )


class BarrierBandSolver(FakeBandSolver):
    """Require two solver calls to overlap before returning."""

    def __init__(self, parties: int = 2) -> None:
        super().__init__()
        self._barrier = threading.Barrier(parties, timeout=5)

    def run(self, model: object, spec: SimulationSpec, **kwargs: object) -> SimulationResult:
        self._barrier.wait()
        return super().run(model, spec, **kwargs)


class CancellingBandSolver(FakeBandSolver):
    """Cancel the analysis after one completed band."""

    def __init__(self, token: EventCancelToken, cancel_hz: float) -> None:
        super().__init__()
        self._token = token
        self._cancel_hz = cancel_hz

    def run(self, model: object, spec: SimulationSpec, **kwargs: object) -> SimulationResult:
        result = super().run(model, spec, **kwargs)
        if abs(spec.frequency_plan.start_hz - self._cancel_hz) < 1.0:
            self._token.cancel()
        return result


class CancelledResultBandSolver(FakeBandSolver):
    """Return a cancelled result for one band."""

    def __init__(self, cancel_hz: float) -> None:
        super().__init__()
        self._cancel_hz = cancel_hz

    def run(self, model: object, spec: SimulationSpec, **kwargs: object) -> SimulationResult:
        if abs(spec.frequency_plan.start_hz - self._cancel_hz) < 1.0:
            return SimulationResult(
                status=SimulationStatus.CANCELLED,
                spec=spec,
                model_fingerprint="a" * 64,
                solver=self.version(),
                frequencies=(),
            )
        return super().run(model, spec, **kwargs)


def test_analyze_bands_runs_one_result_per_band() -> None:
    solver = FakeBandSolver()
    progress: list[tuple[int, int, str]] = []

    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"), _request("20m")),
            progress_callback=lambda index, total, band: progress.append((index, total, band.name)),
        )
    )

    assert len(analysis.bands) == 2
    assert analysis.status is SimulationStatus.COMPLETED
    assert [band.band.name for band in analysis.bands] == ["40m", "20m"]
    assert progress == [(1, 2, "40m"), (2, 2, "20m")]
    assert len(solver.specs) == 2


def test_analyze_bands_keeps_completed_bands_after_an_error() -> None:
    solver = FakeBandSolver(fail_hz=14_000_000.0)
    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"), _request("20m"), _request("10m")),
        )
    )

    assert analysis.status is SimulationStatus.PARTIAL
    assert analysis.bands[0].result.status is SimulationStatus.COMPLETED
    assert analysis.bands[1].result.status is SimulationStatus.ERROR
    assert analysis.bands[2].result.status is SimulationStatus.COMPLETED
    assert analysis.bands[1].result.diagnostics[0].code == "band.error"


def test_analyze_bands_stops_after_cancellation() -> None:
    token = EventCancelToken()
    token.cancel()
    solver = FakeBandSolver()

    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"), _request("20m")),
            cancel_token=token,
        )
    )

    assert analysis.status is SimulationStatus.CANCELLED
    assert len(analysis.bands) == 1
    assert analysis.bands[0].result.status is SimulationStatus.CANCELLED
    assert solver.specs == []


def test_analyze_bands_parallel_matches_sequential_results_and_progress() -> None:
    requests = (_request("40m"), _request("20m"), _request("10m"))

    sequential_progress: list[tuple[int, int, str]] = []
    sequential = AnalyzeBands(FakeBandSolver()).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=requests,
            progress_callback=lambda index, total, band: sequential_progress.append(
                (index, total, band.name)
            ),
        )
    )

    parallel_progress: list[tuple[int, int, str]] = []
    parallel = AnalyzeBands(FakeBandSolver()).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=requests,
            parallel_workers=3,
            progress_callback=lambda index, total, band: parallel_progress.append(
                (index, total, band.name)
            ),
        )
    )

    assert [(band.band.name, band.result.status) for band in parallel.bands] == [
        (band.band.name, band.result.status) for band in sequential.bands
    ]
    assert parallel.status is SimulationStatus.COMPLETED
    assert (
        parallel_progress
        == sequential_progress
        == [
            (1, 3, "40m"),
            (2, 3, "20m"),
            (3, 3, "10m"),
        ]
    )


def test_analyze_bands_parallel_keeps_partial_results_after_an_error() -> None:
    solver = FakeBandSolver(fail_hz=14_000_000.0)
    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"), _request("20m"), _request("10m")),
            parallel_workers=2,
        )
    )

    assert analysis.status is SimulationStatus.PARTIAL
    assert [band.band.name for band in analysis.bands] == ["40m", "20m", "10m"]
    assert analysis.bands[0].result.status is SimulationStatus.COMPLETED
    assert analysis.bands[1].result.status is SimulationStatus.ERROR
    assert analysis.bands[2].result.status is SimulationStatus.COMPLETED
    assert analysis.bands[1].result.diagnostics[0].code == "band.error"


def test_analyze_bands_parallel_stops_before_running_after_cancellation() -> None:
    token = EventCancelToken()
    token.cancel()
    solver = FakeBandSolver()

    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"), _request("20m")),
            cancel_token=token,
            parallel_workers=2,
        )
    )

    assert analysis.status is SimulationStatus.CANCELLED
    assert len(analysis.bands) == 1
    assert analysis.bands[0].result.status is SimulationStatus.CANCELLED
    assert solver.specs == []


def test_analyze_bands_parallel_runs_independent_bands_concurrently() -> None:
    solver = BarrierBandSolver(parties=2)
    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"), _request("20m")),
            parallel_workers=2,
        )
    )

    assert analysis.status is SimulationStatus.COMPLETED
    assert [band.band.name for band in analysis.bands] == ["40m", "20m"]
    assert len(solver.specs) == 2


def test_analyze_bands_sequential_marks_the_next_band_cancelled() -> None:
    token = EventCancelToken()
    solver = CancellingBandSolver(token, cancel_hz=14_000_000.0)
    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"), _request("20m"), _request("10m")),
            cancel_token=token,
        )
    )

    assert [band.band.name for band in analysis.bands] == ["40m", "20m", "10m"]
    assert [band.result.status for band in analysis.bands] == [
        SimulationStatus.COMPLETED,
        SimulationStatus.COMPLETED,
        SimulationStatus.CANCELLED,
    ]
    assert analysis.status is SimulationStatus.PARTIAL
    assert len(solver.specs) == 2


def test_analyze_bands_sequential_stops_on_a_cancelled_result() -> None:
    solver = CancelledResultBandSolver(cancel_hz=14_000_000.0)
    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"), _request("20m"), _request("10m")),
        )
    )

    assert [band.band.name for band in analysis.bands] == ["40m", "20m"]
    assert [band.result.status for band in analysis.bands] == [
        SimulationStatus.COMPLETED,
        SimulationStatus.CANCELLED,
    ]
    assert analysis.status is SimulationStatus.PARTIAL


def test_analyze_bands_parallel_marks_the_next_band_cancelled() -> None:
    token = EventCancelToken()
    solver = CancellingBandSolver(token, cancel_hz=14_000_000.0)
    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"), _request("20m"), _request("10m")),
            cancel_token=token,
            parallel_workers=2,
        )
    )

    assert [band.band.name for band in analysis.bands] == ["40m", "20m", "10m"]
    assert [band.result.status for band in analysis.bands] == [
        SimulationStatus.COMPLETED,
        SimulationStatus.COMPLETED,
        SimulationStatus.CANCELLED,
    ]
    assert analysis.status is SimulationStatus.PARTIAL
    assert len(solver.specs) == 2


def test_analyze_bands_parallel_keeps_a_cancelled_solver_result() -> None:
    solver = CancelledResultBandSolver(cancel_hz=14_000_000.0)
    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"), _request("20m"), _request("10m")),
            parallel_workers=2,
        )
    )

    assert [band.band.name for band in analysis.bands] == ["40m", "20m"]
    assert [band.result.status for band in analysis.bands] == [
        SimulationStatus.COMPLETED,
        SimulationStatus.CANCELLED,
    ]
    assert analysis.status is SimulationStatus.PARTIAL
    assert len(solver.specs) == 1


@pytest.mark.parametrize("workers", [0, 9])
def test_analyze_bands_rejects_invalid_worker_counts(workers: int) -> None:
    with pytest.raises(ValueError, match="parallel_workers"):
        AnalyzeBandsCommand(
            design_id=uuid4(),
            model=_model(),
            requests=(_request("40m"),),
            parallel_workers=workers,
        )


def test_analyze_bands_rejects_an_empty_band_name() -> None:
    request = _request("40m")

    with pytest.raises(ValueError, match="band name"):
        BandSimulationRequest(band=replace(request.band, name=""), spec=request.spec)


def test_analyze_bands_requires_a_band() -> None:
    with pytest.raises(ValueError, match="at least one band"):
        AnalyzeBandsCommand(design_id=uuid4(), model=_model(), requests=())
