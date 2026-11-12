# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Comparison batch use case."""

from __future__ import annotations

from uuid import uuid4

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.application.use_cases.compare_designs import (
    CompareDesigns,
    CompareDesignsCommand,
    ComparisonRun,
)
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.spec import SimulationSpec


class _FakeSolver:
    def __init__(self, *, fail_on: int | None = None) -> None:
        self.calls = 0
        self.fail_on = fail_on

    def validate(self, model: object, spec: object) -> tuple[object, ...]:
        return ()

    def run(self, model: object, spec: object, **_kwargs: object) -> object:
        self.calls += 1
        if self.fail_on == self.calls:
            raise RuntimeError("solver failed")
        return object()


def _runs(count: int = 2) -> tuple[ComparisonRun, ...]:
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))
    return tuple(
        ComparisonRun(
            design_id=uuid4(),
            name=f"Design {index + 1}",
            model=object(),  # type: ignore[arg-type]
            spec=spec,
        )
        for index in range(count)
    )


def test_compare_designs_runs_every_design_and_reports_progress() -> None:
    runs = _runs()
    progress: list[tuple[int, int, str]] = []

    outcome = CompareDesigns(_FakeSolver()).execute(  # type: ignore[arg-type]
        CompareDesignsCommand(
            runs=runs,
            progress_callback=lambda index, total, name: progress.append((index, total, name)),
        )
    )

    assert len(outcome.results) == 2
    assert all(result.result is not None for result in outcome.results)
    assert outcome.cancelled is False
    assert progress == [(1, 2, "Design 1"), (2, 2, "Design 2")]


def test_compare_designs_keeps_partial_results_when_one_run_fails() -> None:
    outcome = CompareDesigns(_FakeSolver(fail_on=2)).execute(  # type: ignore[arg-type]
        CompareDesignsCommand(runs=_runs())
    )

    assert outcome.results[0].result is not None
    assert outcome.results[1].result is None
    assert outcome.results[1].error == "solver failed"


def test_compare_designs_stops_when_the_token_is_cancelled() -> None:
    token = EventCancelToken()
    token.cancel()

    outcome = CompareDesigns(_FakeSolver()).execute(  # type: ignore[arg-type]
        CompareDesignsCommand(runs=_runs(), cancel_token=token)
    )

    assert outcome.results == ()
    assert outcome.cancelled is True
