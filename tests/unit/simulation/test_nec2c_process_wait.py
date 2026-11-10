# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Process-wait behavior of the nec2c adapter, without a real solver."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import antennadesk.simulation.nec2.solver as solver_module
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationStatus
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.solver import Nec2cSolver


class _ImmediateProcess:
    """A child that exits on the first wait and writes no output."""

    returncode: int | None = None

    def __init__(self) -> None:
        self.poll_calls = 0
        self.wait_calls = 0
        self.wait_timeout: float | None = None
        self.terminated = False
        self.killed = False

    def poll(self) -> int | None:
        self.poll_calls += 1
        # Force one wait() call; the old poll+sleep loop would sleep here.
        return None if self.poll_calls == 1 else self.returncode

    def wait(self, timeout: float | None = None) -> int:
        self.wait_calls += 1
        self.wait_timeout = timeout
        self.returncode = 0
        return 0

    def communicate(self, timeout: float | None = None) -> tuple[str, str]:
        del timeout
        return "", ""

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True


class _RunningProcess(_ImmediateProcess):
    """A child that never exits on its own."""

    def poll(self) -> int | None:
        self.poll_calls += 1
        return None

    def wait(self, timeout: float | None = None) -> int:
        self.wait_calls += 1
        self.wait_timeout = timeout
        if self.killed:
            self.returncode = -9
            return -9
        raise subprocess.TimeoutExpired(cmd="nec2c", timeout=timeout or 0.0)


class _CancelAfterFirstWait:
    """Cancel after the adapter has entered its wait loop."""

    def __init__(self) -> None:
        self.calls = 0

    def is_cancelled(self) -> bool:
        self.calls += 1
        return self.calls >= 3


def _solver() -> Nec2cSolver:
    solver = Nec2cSolver(Path("unused"))
    solver._metadata = SolverMetadata(name="nec2c", version="test")
    return solver


def _spec() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
        timeout_s=10.0,
    )


def _model() -> AntennaModel:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna(name="Dipole")


def test_solver_waits_for_the_child_without_sleeping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = _ImmediateProcess()
    sleeps: list[float] = []
    monkeypatch.setattr(solver_module.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(solver_module.time, "sleep", sleeps.append)

    _solver().run(_model(), _spec())

    assert process.wait_calls == 1
    assert process.wait_timeout is not None
    assert 0.0 < process.wait_timeout <= solver_module.PROCESS_POLL_INTERVAL_S
    assert sleeps == []
    assert process.terminated is False


def test_solver_can_cancel_while_waiting_for_the_child(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = _RunningProcess()
    sleeps: list[float] = []
    monkeypatch.setattr(solver_module.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(solver_module.time, "sleep", sleeps.append)

    result = _solver().run(
        _model(),
        _spec(),
        cancel_token=_CancelAfterFirstWait(),
    )

    assert process.wait_calls >= 1
    assert process.terminated is True
    assert process.killed is True
    assert sleeps == []
    assert result.status is SimulationStatus.CANCELLED
    assert any(diagnostic.code == "solver.cancelled" for diagnostic in result.diagnostics)
