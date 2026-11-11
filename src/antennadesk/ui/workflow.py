# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Progressive workflow mode and state-derived next-step guidance.

The workflow layer is deliberately Qt-free. It turns the current project and
result state into one deterministic next action, so the UI can stay a thin
renderer and the guidance can be unit-tested without a display.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..domain.simulation.result import SimulationStatus

HIGH_SWR = 2.0
"""SWR at the design frequency above which the coach suggests reviewing the match."""


class WorkflowMode(StrEnum):
    """How much of the interface is visible by default."""

    GUIDED = "guided"
    STANDARD = "standard"
    ADVANCED = "advanced"


class NextStepKind(StrEnum):
    """The single action the coach recommends next."""

    CREATE_PROJECT = "create_project"
    CONFIGURE_SOLVER = "configure_solver"
    SIMULATE = "simulate"
    REVIEW_DIAGNOSTICS = "review_diagnostics"
    REVIEW_SWR = "review_swr"
    BUILD_SHEET = "build_sheet"
    MEASURE = "measure"
    COMPARE_MEASUREMENT = "compare_measurement"
    COMPLETE = "complete"


@dataclass(frozen=True, slots=True)
class WorkflowContext:
    """The project and session facts used to choose the next step.

    The context is intentionally small. It does not contain widgets, result
    objects, or translated strings; the caller derives those from the current
    project and simulation result.
    """

    has_project: bool
    has_solver: bool
    has_result: bool
    result_status: SimulationStatus | None = None
    design_swr: float | None = None
    reviewed_swr: bool = False
    construction_viewed: bool = False
    has_measurement: bool = False
    measurement_compared: bool = False


@dataclass(frozen=True, slots=True)
class NextStep:
    """A translatable next-step recommendation."""

    kind: NextStepKind
    title_key: str
    body_key: str
    action_key: str | None

    @classmethod
    def for_kind(cls, kind: NextStepKind, *, action: bool = True) -> NextStep:
        """Build the conventional translation keys for ``kind``."""

        base = f"workflow.next.{kind.value}"
        return cls(
            kind=kind,
            title_key=f"{base}.title",
            body_key=f"{base}.body",
            action_key=f"{base}.action" if action else None,
        )


def next_step(context: WorkflowContext) -> NextStep:
    """Return the highest-value next action for ``context``.

    The order is intentional: a missing project or solver blocks everything;
    a missing result comes before interpretation; diagnostics come before a
    high-SWR review because a partial or failed run is not a trustworthy match;
    construction and measurement follow only after the design is simulated.
    """

    if not context.has_project:
        return NextStep.for_kind(NextStepKind.CREATE_PROJECT)
    if not context.has_solver:
        return NextStep.for_kind(NextStepKind.CONFIGURE_SOLVER)
    if not context.has_result:
        return NextStep.for_kind(NextStepKind.SIMULATE)
    if context.result_status in {
        SimulationStatus.ERROR,
        SimulationStatus.PARTIAL,
    }:
        return NextStep.for_kind(NextStepKind.REVIEW_DIAGNOSTICS)
    if context.result_status is SimulationStatus.CANCELLED:
        return NextStep.for_kind(NextStepKind.SIMULATE)
    if (
        context.design_swr is not None
        and context.design_swr > HIGH_SWR
        and not context.reviewed_swr
    ):
        return NextStep.for_kind(NextStepKind.REVIEW_SWR)
    if not context.construction_viewed:
        return NextStep.for_kind(NextStepKind.BUILD_SHEET)
    if not context.has_measurement:
        return NextStep.for_kind(NextStepKind.MEASURE)
    if not context.measurement_compared:
        return NextStep.for_kind(NextStepKind.COMPARE_MEASUREMENT)
    return NextStep.for_kind(NextStepKind.COMPLETE)
