# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Next-step guidance and workflow-mode invariants."""

from __future__ import annotations

from antennadesk.domain.simulation.result import SimulationStatus
from antennadesk.ui.workflow import (
    HIGH_SWR,
    NextStepKind,
    WorkflowContext,
    WorkflowMode,
    next_step,
)


def _context(**overrides: object) -> WorkflowContext:
    values: dict[str, object] = {
        "has_project": True,
        "has_solver": True,
        "has_result": True,
        "result_status": SimulationStatus.COMPLETED,
        "design_swr": 1.2,
    }
    values.update(overrides)
    return WorkflowContext(**values)  # type: ignore[arg-type]


def test_missing_project_and_solver_block_the_flow() -> None:
    assert next_step(WorkflowContext(False, True, False)).kind is NextStepKind.CREATE_PROJECT
    assert next_step(WorkflowContext(True, False, False)).kind is NextStepKind.CONFIGURE_SOLVER


def test_missing_result_asks_for_a_simulation() -> None:
    step = next_step(_context(has_result=False))

    assert step.kind is NextStepKind.SIMULATE
    assert step.title_key == "workflow.next.simulate.title"
    assert step.body_key == "workflow.next.simulate.body"
    assert step.action_key == "workflow.next.simulate.action"


def test_error_and_partial_results_send_the_user_to_diagnostics() -> None:
    for status in (SimulationStatus.ERROR, SimulationStatus.PARTIAL):
        assert next_step(_context(result_status=status)).kind is NextStepKind.REVIEW_DIAGNOSTICS


def test_cancelled_result_asks_for_another_run() -> None:
    step = next_step(_context(result_status=SimulationStatus.CANCELLED))

    assert step.kind is NextStepKind.SIMULATE


def test_high_swr_is_reviewed_before_construction() -> None:
    assert next_step(_context(design_swr=HIGH_SWR + 0.1)).kind is NextStepKind.REVIEW_SWR
    assert next_step(_context(design_swr=HIGH_SWR)).kind is NextStepKind.BUILD_SHEET
    assert (
        next_step(_context(design_swr=HIGH_SWR + 0.1, reviewed_swr=True)).kind
        is NextStepKind.BUILD_SHEET
    )


def test_construction_and_measurement_states_follow_the_design_loop() -> None:
    assert next_step(_context()).kind is NextStepKind.BUILD_SHEET
    assert next_step(_context(construction_viewed=True)).kind is NextStepKind.MEASURE
    assert (
        next_step(_context(construction_viewed=True, has_measurement=True)).kind
        is NextStepKind.COMPARE_MEASUREMENT
    )
    assert (
        next_step(
            _context(
                construction_viewed=True,
                has_measurement=True,
                measurement_compared=True,
            )
        ).kind
        is NextStepKind.COMPLETE
    )


def test_workflow_mode_values_are_stable() -> None:
    assert {mode.value for mode in WorkflowMode} == {
        "guided",
        "standard",
        "advanced",
    }
