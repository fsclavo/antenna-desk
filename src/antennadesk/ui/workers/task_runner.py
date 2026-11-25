# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""One lifecycle owner for Qt worker threads.

The UI used to copy the same ``QThread``/``moveToThread``/``deleteLater``
sequence into every dialog. This module centralizes that lifecycle:

- at most one active task per runner;
- every worker signal is queued to the GUI thread;
- a generation check makes a late result from an abandoned task harmless;
- the terminal signals are emitted after the thread's `finished` signal and a
  bounded join, so a handler may start the next task;
- close waits are bounded and a stuck task is detached instead of blocking or
  destroying a running thread.

See ``docs/ADR/0053-qt-worker-task-lifecycle.md``.
"""

from __future__ import annotations

import weakref
from dataclasses import dataclass
from typing import Any, Protocol, cast

from PySide6.QtCore import QEventLoop, QObject, Qt, QThread, Signal, Slot


class CancelHandle(Protocol):
    """Anything that can request cooperative cancellation."""

    def cancel(self) -> None:
        """Request cancellation."""


class TaskRunner(QObject):
    """Run one worker in a ``QThread`` and own its complete lifecycle."""

    started = Signal()
    succeeded = Signal(object)
    failed = Signal(object)
    cancelled = Signal()
    rejected = Signal(str)
    finished = Signal()

    def __init__(
        self,
        parent: QObject | None = None,
        *,
        close_timeout_ms: int = 2_000,
    ) -> None:
        super().__init__(parent)
        if close_timeout_ms < 0:
            raise ValueError("close_timeout_ms must not be negative")
        self._close_timeout_ms = close_timeout_ms
        self._generation = 0
        self._state: _TaskState | None = None

    @property
    def is_running(self) -> bool:
        """Whether a task is owned by this runner."""

        return self._state is not None

    @property
    def generation(self) -> int:
        """Identifier of the most recent task, incremented by ``start``."""

        return self._generation

    def start(
        self,
        worker: QObject,
        *,
        success_signal: str = "finished",
        cancel: CancelHandle | None = None,
    ) -> bool:
        """Start ``worker`` unless another task is active.

        The caller connects its own progress signals before calling ``start``.
        The worker must expose ``success_signal(object)`` and ``failed(object)``.
        """

        if self._state is not None:
            self.rejected.emit("A task is already running.")
            return False
        success = getattr(worker, success_signal, None)
        failure = getattr(worker, "failed", None)
        run = getattr(worker, "run", None)
        if success is None or failure is None or run is None:
            raise TypeError("worker must expose run, finished/… and failed")
        if worker.parent() is not None:
            raise TypeError("worker must not have a parent before moveToThread")

        self._generation += 1
        generation = self._generation
        thread = QThread(self)
        bridge = _TaskBridge(self, generation)
        worker.moveToThread(thread)
        thread.started.connect(cast(Any, worker).run)
        success.connect(bridge.relay_succeeded, Qt.ConnectionType.QueuedConnection)
        failure.connect(bridge.relay_failed, Qt.ConnectionType.QueuedConnection)
        # QThread::quit is thread-safe; a direct call stops the event loop even
        # while close() is waiting on the GUI thread.
        success.connect(thread.quit, Qt.ConnectionType.DirectConnection)
        failure.connect(thread.quit, Qt.ConnectionType.DirectConnection)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(bridge.relay_thread_finished, Qt.ConnectionType.QueuedConnection)
        thread.finished.connect(bridge.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._state = _TaskState(
            generation=generation,
            thread=thread,
            worker=worker,
            bridge=bridge,
            cancel=cancel,
        )
        thread.start()
        self.started.emit()
        return True

    def cancel(self) -> bool:
        """Ask the active worker to cancel.

        Returns ``False`` when no task is active. The worker still decides how
        to finish; a partial result is delivered normally.
        """

        state = self._state
        if state is None:
            return False
        if state.cancel is not None:
            state.cancel.cancel()
        return True

    def close(self, timeout_ms: int | None = None) -> bool:
        """Stop the active task, or detach it after a bounded wait.

        ``True`` means the thread stopped before the timeout. ``False`` means it
        was detached: it will finish and delete its worker and itself, but the
        controller will not report a result for it.
        """

        state = self._state
        if state is None:
            return True
        timeout = self._close_timeout_ms if timeout_ms is None else max(0, timeout_ms)
        if state.cancel is not None:
            state.cancel.cancel()
        state.thread.quit()
        if state.thread.wait(timeout):
            self._state = None
            self.cancelled.emit()
            self.finished.emit()
            return True
        self._state = None
        self._detach(state)
        self.cancelled.emit()
        self.finished.emit()
        return False

    def _detach(self, state: _TaskState) -> None:
        """Let a running thread finish without the controller or its parents."""

        thread = state.thread
        guard = _DetachedGuard(thread, state.worker)
        _DETACHED_TASKS.add(guard)
        thread.finished.connect(guard.release, Qt.ConnectionType.QueuedConnection)
        thread.setParent(None)

    def _worker_succeeded(self, generation: int, result: object) -> None:
        state = self._state
        if state is None or state.generation != generation or state.outcome is not None:
            return
        state.outcome = _Outcome("succeeded", result)
        state.thread.quit()

    def _worker_failed(self, generation: int, error: object) -> None:
        state = self._state
        if state is None or state.generation != generation or state.outcome is not None:
            return
        state.outcome = _Outcome("failed", error)
        state.thread.quit()

    def _thread_finished(self, generation: int) -> None:
        state = self._state
        if state is None or state.generation != generation:
            return
        # QThread::finished is emitted just before the thread exits. Join it
        # before handing the result to the GUI, so a handler may destroy the
        # runner and its child thread without racing the thread exit.
        if not state.thread.wait(1_000):
            self._state = None
            self._detach(state)
            self.cancelled.emit()
            self.finished.emit()
            return
        self._state = None
        outcome = state.outcome
        if outcome is None:
            self.cancelled.emit()
        elif outcome.kind == "succeeded":
            self.succeeded.emit(outcome.value)
        else:
            self.failed.emit(outcome.value)
        self.finished.emit()


@dataclass(slots=True)
class _Outcome:
    kind: str
    value: object


@dataclass(slots=True)
class _TaskState:
    generation: int
    thread: QThread
    worker: QObject
    bridge: _TaskBridge
    cancel: CancelHandle | None
    outcome: _Outcome | None = None


class _TaskBridge(QObject):
    """GUI-thread receiver that carries the task generation."""

    def __init__(self, runner: TaskRunner, generation: int) -> None:
        super().__init__(runner)
        self._runner = weakref.ref(runner)
        self._generation = generation

    @Slot(object)
    def relay_succeeded(self, result: object) -> None:
        runner = self._runner()
        if runner is not None:
            runner._worker_succeeded(self._generation, result)

    @Slot(object)
    def relay_failed(self, error: object) -> None:
        runner = self._runner()
        if runner is not None:
            runner._worker_failed(self._generation, error)

    @Slot()
    def relay_thread_finished(self) -> None:
        runner = self._runner()
        if runner is not None:
            runner._thread_finished(self._generation)


class _DetachedGuard(QObject):
    """Keep a detached thread and its worker alive until the thread stops."""

    def __init__(self, thread: QThread, worker: QObject) -> None:
        super().__init__()
        self._thread = thread
        self._worker = worker

    @Slot()
    def release(self) -> None:
        _DETACHED_TASKS.discard(self)
        self.deleteLater()


_DETACHED_TASKS: set[_DetachedGuard] = set()


def run_worker_blocking(
    parent: QObject | None,
    worker: QObject,
    *,
    success_signal: str = "finished",
    cancel: CancelHandle | None = None,
) -> object:
    """Run one worker through ``TaskRunner`` while a nested event loop waits.

    This is the shared adapter for the modal project-I/O and end-fed paths. It
    preserves their previous behavior: the caller blocks until the worker
    finishes, and exceptions sent through ``failed`` are re-raised.
    """

    runner = TaskRunner(parent)
    loop = QEventLoop()
    outcome: dict[str, object] = {}

    def succeeded(value: object) -> None:
        outcome["value"] = value

    def failed(error: object) -> None:
        outcome["error"] = error

    runner.succeeded.connect(succeeded)
    runner.failed.connect(failed)
    runner.finished.connect(loop.quit)
    try:
        if not runner.start(worker, success_signal=success_signal, cancel=cancel):
            raise RuntimeError("worker task was rejected")
        loop.exec()
    finally:
        runner.close(5_000)
        runner.deleteLater()
    error = outcome.get("error")
    if isinstance(error, BaseException):
        raise error
    if error is not None:
        raise ValueError(str(error))
    if "value" not in outcome:
        raise RuntimeError("worker produced no result")
    return outcome["value"]
