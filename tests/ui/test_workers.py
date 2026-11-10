# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Direct tests for the thin Qt worker adapters."""

from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType
from uuid import uuid4

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.workers import (
    band_analysis_worker,
    element_optimization_worker,
    endfed_convergence_worker,
    family_optimization_worker,
    open_project_worker,
    optimization_worker,
    save_project_worker,
    simulation_worker,
    synthesis_worker,
)

SENTINEL = object()


def _fake_use_case(
    *,
    result: object = SENTINEL,
    error: Exception | None = None,
) -> type:
    class FakeUseCase:
        def __init__(self, solver: object) -> None:
            self.solver = solver

        def execute(self, command: object) -> object:
            del command
            if error is not None:
                raise error
            return result

    return FakeUseCase


@dataclass(frozen=True, slots=True)
class WorkerCase:
    module: ModuleType
    worker_type: type
    use_case_name: str
    args: tuple[object, ...]


WORKER_CASES = (
    WorkerCase(
        simulation_worker,
        simulation_worker.SimulationWorker,
        "RunSimulation",
        (object(), object(), object(), object()),
    ),
    WorkerCase(
        band_analysis_worker,
        band_analysis_worker.BandAnalysisWorker,
        "AnalyzeBands",
        (object(), uuid4(), object(), (object(),), object()),
    ),
    WorkerCase(
        family_optimization_worker,
        family_optimization_worker.FamilyOptimizationWorker,
        "OptimizeAntenna",
        (object(), object()),
    ),
    WorkerCase(
        element_optimization_worker,
        element_optimization_worker.ElementOptimizationWorker,
        "OptimizeElements",
        (object(), object()),
    ),
    WorkerCase(
        optimization_worker,
        optimization_worker.OptimizationWorker,
        "OptimizeAntennaDimension",
        (object(), object()),
    ),
    WorkerCase(
        synthesis_worker,
        synthesis_worker.SynthesisWorker,
        "SynthesizeAntenna",
        (object(), object()),
    ),
)


@pytest.mark.parametrize("case", WORKER_CASES, ids=lambda case: case.worker_type.__name__)
def test_worker_emits_finished(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    case: WorkerCase,
) -> None:
    del qtbot
    monkeypatch.setattr(case.module, case.use_case_name, _fake_use_case(result=SENTINEL))
    worker = case.worker_type(*case.args)
    finished: list[object] = []
    failed: list[str] = []
    worker.finished.connect(finished.append)
    worker.failed.connect(failed.append)

    worker.run()

    assert finished == [SENTINEL]
    assert failed == []


@pytest.mark.parametrize("case", WORKER_CASES, ids=lambda case: case.worker_type.__name__)
def test_worker_emits_failure(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    case: WorkerCase,
) -> None:
    del qtbot
    monkeypatch.setattr(
        case.module,
        case.use_case_name,
        _fake_use_case(error=RuntimeError("boom")),
    )
    worker = case.worker_type(*case.args)
    finished: list[object] = []
    failed: list[str] = []
    worker.finished.connect(finished.append)
    worker.failed.connect(failed.append)

    worker.run()

    assert finished == []
    assert failed == ["boom"]


def test_simulation_worker_reports_phases(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del qtbot
    monkeypatch.setattr(simulation_worker, "RunSimulation", _fake_use_case(result=SENTINEL))
    worker = simulation_worker.SimulationWorker(
        object(),
        object(),
        object(),
        object(),
    )
    phases: list[str] = []
    worker.phase.connect(phases.append)

    worker.run()

    assert phases == ["running", "processing"]


@dataclass
class _FamilyProgressCommand:
    progress: object = None


@dataclass
class _LengthProgressCommand:
    progress: object = None


def test_family_optimization_worker_forwards_progress(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del qtbot

    class FakeUseCase:
        def __init__(self, solver: object) -> None:
            self.solver = solver

        def execute(self, command: object) -> object:
            command.progress(2, 1.25)  # type: ignore[attr-defined]
            return SENTINEL

    monkeypatch.setattr(family_optimization_worker, "OptimizeAntenna", FakeUseCase)
    external: list[tuple[int, object]] = []
    worker = family_optimization_worker.FamilyOptimizationWorker(
        object(),
        _FamilyProgressCommand(
            progress=lambda completed, score: external.append((completed, score))
        ),  # type: ignore[arg-type]
    )
    progress: list[tuple[int, object]] = []
    worker.progress.connect(lambda completed, score: progress.append((completed, score)))

    worker.run()

    assert external == [(2, 1.25)]
    assert progress == [(2, 1.25)]


def test_optimization_worker_forwards_progress(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del qtbot

    class FakeUseCase:
        def __init__(self, solver: object) -> None:
            self.solver = solver

        def execute(self, command: object) -> object:
            command.progress(3)  # type: ignore[attr-defined]
            return SENTINEL

    monkeypatch.setattr(optimization_worker, "OptimizeAntennaDimension", FakeUseCase)
    external: list[int] = []
    worker = optimization_worker.OptimizationWorker(
        object(),
        _LengthProgressCommand(progress=external.append),  # type: ignore[arg-type]
    )
    progress: list[int] = []
    worker.progress.connect(progress.append)

    worker.run()

    assert external == [3]
    assert progress == [3]


def test_band_analysis_worker_reports_progress(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del qtbot

    class FakeBand:
        name = "40m"

    class FakeUseCase:
        def __init__(self, solver: object) -> None:
            self.solver = solver

        def execute(self, command: object) -> object:
            command.progress_callback(1, 2, FakeBand())  # type: ignore[attr-defined]
            return SENTINEL

    monkeypatch.setattr(band_analysis_worker, "AnalyzeBands", FakeUseCase)
    worker = band_analysis_worker.BandAnalysisWorker(
        object(),
        uuid4(),
        object(),
        (object(),),
        object(),
        parallel_workers=2,
    )
    progress: list[tuple[int, int, str]] = []
    finished: list[object] = []
    worker.progress.connect(lambda index, total, band: progress.append((index, total, band)))
    worker.finished.connect(finished.append)

    worker.run()

    assert progress == [(1, 2, "40m")]
    assert finished == [SENTINEL]


def test_save_project_worker_emits_prepared(qtbot: QtBot) -> None:
    del qtbot

    class FakeSaveProject:
        def prepare(self, project: object) -> object:
            del project
            return SENTINEL

    worker = save_project_worker.SaveProjectWorker(FakeSaveProject(), object())
    prepared: list[object] = []
    failed: list[str] = []
    worker.prepared.connect(prepared.append)
    worker.failed.connect(failed.append)

    worker.run()

    assert prepared == [SENTINEL]
    assert failed == []


def test_save_project_worker_emits_failure(qtbot: QtBot) -> None:
    del qtbot

    class FailingSaveProject:
        def prepare(self, project: object) -> object:
            del project
            raise RuntimeError("boom")

    worker = save_project_worker.SaveProjectWorker(FailingSaveProject(), object())
    prepared: list[object] = []
    failed: list[str] = []
    worker.prepared.connect(prepared.append)
    worker.failed.connect(failed.append)

    worker.run()

    assert prepared == []
    assert failed == ["boom"]


def test_open_project_worker_emits_project(qtbot: QtBot) -> None:
    del qtbot

    class FakeOpenProject:
        def execute(self, path: object) -> object:
            del path
            return SENTINEL

    worker = open_project_worker.OpenProjectWorker(FakeOpenProject(), object())
    finished: list[object] = []
    failed: list[str] = []
    worker.finished.connect(finished.append)
    worker.failed.connect(failed.append)

    worker.run()

    assert finished == [SENTINEL]
    assert failed == []


def test_open_project_worker_emits_failure(qtbot: QtBot) -> None:
    del qtbot

    class FailingOpenProject:
        def execute(self, path: object) -> object:
            del path
            raise RuntimeError("boom")

    worker = open_project_worker.OpenProjectWorker(FailingOpenProject(), object())
    finished: list[object] = []
    failed: list[str] = []
    worker.finished.connect(finished.append)
    worker.failed.connect(failed.append)

    worker.run()

    assert finished == []
    assert failed == ["boom"]


def test_endfed_convergence_worker_emits_result(qtbot: QtBot) -> None:
    del qtbot

    class FakeCheck:
        def execute(self, command: object) -> object:
            del command
            return SENTINEL

    worker = endfed_convergence_worker.EndFedConvergenceWorker(FakeCheck(), object())
    finished: list[object] = []
    failed: list[str] = []
    worker.finished.connect(finished.append)
    worker.failed.connect(failed.append)

    worker.run()

    assert finished == [SENTINEL]
    assert failed == []


def test_endfed_convergence_worker_emits_failure(qtbot: QtBot) -> None:
    del qtbot

    class FailingCheck:
        def execute(self, command: object) -> object:
            del command
            raise RuntimeError("boom")

    worker = endfed_convergence_worker.EndFedConvergenceWorker(FailingCheck(), object())
    finished: list[object] = []
    failed: list[str] = []
    worker.finished.connect(finished.append)
    worker.failed.connect(failed.append)

    worker.run()

    assert finished == []
    assert failed == ["boom"]
