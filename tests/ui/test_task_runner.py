# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Lifecycle tests for the shared Qt task runner."""

from __future__ import annotations

import threading

import pytest
from PySide6.QtCore import QObject, QThread, Signal, Slot
from pytestqt.qtbot import QtBot

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.ui.workers.task_runner import TaskRunner, run_worker_blocking


class _Worker(QObject):
    finished = Signal(object)
    failed = Signal(object)

    def __init__(
        self,
        *,
        result: object = None,
        error: object | None = None,
        delay_ms: int = 0,
        token: EventCancelToken | None = None,
        wait_for_token: bool = False,
    ) -> None:
        super().__init__()
        self._result = result
        self._error = error
        self._delay_ms = delay_ms
        self._token = token
        self._wait_for_token = wait_for_token
        self.runs = 0
        self.done = threading.Event()

    @Slot()
    def run(self) -> None:
        self.runs += 1
        try:
            if self._wait_for_token and self._token is not None:
                while not self._token.is_cancelled():
                    QThread.msleep(5)
            if self._delay_ms:
                QThread.msleep(self._delay_ms)
            if self._error is not None:
                self.failed.emit(self._error)
            else:
                self.finished.emit(self._result)
        finally:
            self.done.set()


def test_success_is_reported_after_the_thread_stops(qtbot: QtBot) -> None:
    runner = TaskRunner()
    worker = _Worker(result=42)
    results: list[object] = []
    states: list[bool] = []

    def succeeded(value: object) -> None:
        results.append(value)
        states.append(runner.is_running)

    runner.succeeded.connect(succeeded)
    with qtbot.waitSignal(runner.finished, timeout=5_000):
        assert runner.start(worker) is True
        assert runner.is_running is True

    assert results == [42]
    assert states == [False]
    assert runner.is_running is False
    qtbot.waitUntil(worker.done.is_set, timeout=5_000)
    runner.deleteLater()


def test_failure_is_reported_without_losing_the_payload(qtbot: QtBot) -> None:
    runner = TaskRunner()
    worker = _Worker(error=ValueError("boom"))
    failures: list[object] = []
    runner.failed.connect(failures.append)

    with qtbot.waitSignal(runner.finished, timeout=5_000):
        assert runner.start(worker) is True

    assert len(failures) == 1
    assert isinstance(failures[0], ValueError)
    assert str(failures[0]) == "boom"
    runner.deleteLater()


def test_cancel_keeps_the_partial_result(qtbot: QtBot) -> None:
    token = EventCancelToken()
    runner = TaskRunner()
    worker = _Worker(result="partial", token=token, wait_for_token=True)
    results: list[object] = []
    runner.succeeded.connect(results.append)

    with qtbot.waitSignal(runner.finished, timeout=5_000):
        assert runner.start(worker, cancel=token) is True
        assert runner.cancel() is True

    assert results == ["partial"]
    assert token.is_cancelled() is True
    runner.deleteLater()


def test_double_start_is_rejected_without_overlap(qtbot: QtBot) -> None:
    token = EventCancelToken()
    runner = TaskRunner()
    first = _Worker(token=token, wait_for_token=True)
    second = _Worker(result="second")
    reasons: list[str] = []
    results: list[object] = []
    runner.rejected.connect(reasons.append)
    runner.succeeded.connect(results.append)

    assert runner.start(first, cancel=token) is True
    assert runner.start(second) is False
    assert reasons
    assert "already running" in reasons[0]
    assert second.runs == 0

    with qtbot.waitSignal(runner.finished, timeout=5_000):
        runner.cancel()

    assert results == [None]
    assert second.runs == 0
    runner.deleteLater()


def test_close_stops_a_cooperative_worker_within_the_timeout(qtbot: QtBot) -> None:
    token = EventCancelToken()
    runner = TaskRunner()
    worker = _Worker(token=token, wait_for_token=True)
    signals: list[str] = []
    runner.succeeded.connect(lambda _value: signals.append("succeeded"))
    runner.cancelled.connect(lambda: signals.append("cancelled"))
    runner.finished.connect(lambda: signals.append("finished"))

    assert runner.start(worker, cancel=token) is True
    assert runner.close(2_000) is True
    assert runner.is_running is False
    assert signals == ["cancelled", "finished"]
    qtbot.waitUntil(worker.done.is_set, timeout=5_000)
    runner.deleteLater()


def test_close_detaches_a_stuck_worker_and_ignores_its_late_result(qtbot: QtBot) -> None:
    runner = TaskRunner()
    stuck = _Worker(result="late", delay_ms=150)
    late_results: list[object] = []
    runner.succeeded.connect(late_results.append)

    assert runner.start(stuck) is True
    qtbot.waitUntil(lambda: stuck.runs == 1, timeout=5_000)
    assert runner.close(0) is False
    assert runner.is_running is False

    # A new task can start while the detached one is still finishing.
    fresh = _Worker(result="fresh")
    results: list[object] = []
    runner.succeeded.connect(results.append)
    with qtbot.waitSignal(runner.finished, timeout=5_000):
        assert runner.start(fresh) is True

    qtbot.waitUntil(stuck.done.is_set, timeout=5_000)
    qtbot.wait(50)
    assert results == ["fresh"]
    assert late_results == ["fresh"]
    runner.deleteLater()


def test_blocking_adapter_returns_the_result(qtbot: QtBot) -> None:
    del qtbot
    value = run_worker_blocking(None, _Worker(result="value"))
    assert value == "value"


def test_blocking_adapter_reraises_exceptions(qtbot: QtBot) -> None:
    del qtbot
    with pytest.raises(ValueError, match="boom"):
        run_worker_blocking(None, _Worker(error=ValueError("boom")))


def test_blocking_adapter_reports_string_failures(qtbot: QtBot) -> None:
    del qtbot
    with pytest.raises(ValueError, match="broken"):
        run_worker_blocking(None, _Worker(error="broken"))


def test_close_immediately_after_start_still_stops_the_thread(qtbot: QtBot) -> None:
    runner = TaskRunner()
    worker = _Worker(result="value", delay_ms=20)

    assert runner.start(worker) is True
    assert runner.close(2_000) is True

    qtbot.waitUntil(worker.done.is_set, timeout=5_000)
    runner.deleteLater()


def test_detached_task_survives_runner_deletion(qtbot: QtBot) -> None:
    runner = TaskRunner()
    worker = _Worker(result="late", delay_ms=150)

    assert runner.start(worker) is True
    qtbot.waitUntil(lambda: worker.runs == 1, timeout=5_000)
    assert runner.close(0) is False

    runner.deleteLater()
    qtbot.wait(20)
    qtbot.waitUntil(worker.done.is_set, timeout=5_000)
    qtbot.wait(50)


def test_start_rejects_a_worker_with_a_parent(qtbot: QtBot) -> None:
    del qtbot
    runner = TaskRunner()
    parent = QObject()
    worker = _Worker()
    worker.setParent(parent)

    with pytest.raises(TypeError, match="parent"):
        runner.start(worker)


def test_results_are_delivered_on_the_runner_thread(qtbot: QtBot) -> None:
    runner = TaskRunner()
    threads: list[QThread] = []
    runner.succeeded.connect(lambda _value: threads.append(QThread.currentThread()))

    with qtbot.waitSignal(runner.finished, timeout=5_000):
        assert runner.start(_Worker(result="value")) is True

    assert threads == [runner.thread()]
