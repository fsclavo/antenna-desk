# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import time
from collections.abc import Callable
from datetime import UTC, datetime

from PySide6.QtCore import QCoreApplication

from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


def wait_for_condition(predicate: Callable[[], bool], *, timeout_ms: int = 5_000) -> None:
    """Process Qt events without relying on a nested QEventLoop.

    ``qtbot.waitUntil`` uses a nested event loop. After many MainWindow tests
    on the offscreen platform, that loop can stop delivering queued worker
    signals even though the worker thread has already finished. Processing
    posted events directly keeps worker-based UI tests deterministic.
    """

    deadline = time.monotonic() + timeout_ms / 1000.0
    while not predicate():
        if time.monotonic() >= deadline:
            raise TimeoutError(f"condition not met in {timeout_ms} ms")
        QCoreApplication.processEvents()
        time.sleep(0.01)


def make_completed_result() -> SimulationResult:
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        far_field=FarFieldRequest(enabled=True),
    )
    far_field = (
        FarFieldPoint(
            0.0,
            0.0,
            2.14,
            None,
            2.14,
            0.0,
            0.0,
            "LINEAR",
            None,
            None,
            None,
            None,
        ),
        FarFieldPoint(
            90.0,
            0.0,
            None,
            None,
            None,
            0.0,
            0.0,
            None,
            None,
            None,
            None,
            None,
        ),
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=(
            FrequencyResult(
                frequency_hz=7_100_000.0,
                feed_tag=1,
                feed_segment=11,
                impedance_ohm=complex(50.0, 0.0),
                swr=1.0,
                input_power_w=0.001,
                far_field=far_field,
            ),
        ),
        duration_s=0.1,
        started_at=datetime(2026, 10, 29, tzinfo=UTC),
        finished_at=datetime(2026, 10, 29, tzinfo=UTC),
    )
