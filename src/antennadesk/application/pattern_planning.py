# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Choose far-field sampling that fits the project storage budget.

The planner is Qt-free. It returns the adjusted specification, the selected
budget, and an optional diagnostic; the caller decides how to present them.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ..domain.antennas.antenna import AntennaModel
from ..domain.common.validation import Diagnostic, Severity
from ..domain.simulation.bands import band_snapshot_frequencies
from ..domain.simulation.budget import (
    PatternBudget,
    choose_batch_pattern_step,
    choose_pattern_step,
)
from ..domain.simulation.far_field import FarFieldRequest
from ..domain.simulation.frequency import FrequencyPlan
from ..domain.simulation.spec import SimulationSpec
from .pattern_resolution import PATTERN_STEPS_DEG, far_field_request, pattern_counts

CANDIDATE_PATTERN_STEPS_DEG = tuple(reversed(PATTERN_STEPS_DEG))


@dataclass(frozen=True, slots=True)
class PatternPlan:
    """The fitted specification and the observations behind the choice."""

    spec: SimulationSpec
    budget: PatternBudget | None = None
    diagnostic: Diagnostic | None = None


def snapshot_frequencies(
    frequency_plan: FrequencyPlan,
    *,
    preferred_frequency_hz: float,
    count: int | None,
) -> tuple[float, ...]:
    """Return automatic band snapshots or an explicit snapshot count."""

    if count is None:
        return band_snapshot_frequencies(
            frequency_plan,
            preferred_frequency_hz=preferred_frequency_hz,
        )
    return frequency_plan.snapshot_frequencies(
        count,
        preferred_frequency_hz=preferred_frequency_hz,
    )


def _segment_count(model: AntennaModel, spec: SimulationSpec) -> int:
    return sum(
        spec.segmentation.segments_for(wire, spec.frequency_plan.stop_hz) for wire in model.wires
    )


def fit_spec_to_budget(
    model: AntennaModel,
    spec: SimulationSpec,
    *,
    requested_step_deg: float | None,
    pattern_frequency_count: int | None,
) -> PatternPlan:
    """Choose pattern snapshots and the finest pattern step that fits."""

    if not spec.far_field.enabled:
        return PatternPlan(spec=replace(spec, pattern_frequencies_hz=()))

    ground = model.environment.ground
    pattern_frequencies = spec.pattern_frequencies_hz
    if not pattern_frequencies:
        pattern_frequencies = snapshot_frequencies(
            spec.frequency_plan,
            preferred_frequency_hz=model.design_frequency_hz,
            count=pattern_frequency_count,
        )
    pattern_count = len(pattern_frequencies) if pattern_frequencies else spec.frequency_plan.count
    budget = choose_pattern_step(
        frequency_count=spec.frequency_plan.count,
        pattern_frequency_count=pattern_count,
        segment_count=_segment_count(model, spec),
        candidate_steps=CANDIDATE_PATTERN_STEPS_DEG,
        counts_for_step=lambda step: pattern_counts(step, ground),
        requested_step_deg=requested_step_deg,
    )
    if budget.far_field_enabled:
        if requested_step_deg is None or budget.pattern_step_deg == requested_step_deg:
            diagnostic = None
        else:
            diagnostic = Diagnostic(
                code="solver.pattern_resolution_reduced",
                severity=Severity.INFO,
                message=(
                    "far-field pattern resolution reduced from "
                    f"{requested_step_deg:g}° to {budget.pattern_step_deg:g}° "
                    "to fit the project storage limit"
                ),
                field="far_field",
            )
        pattern_step_deg = budget.pattern_step_deg
        if pattern_step_deg is None:
            raise ValueError("far-field pattern step is missing")
        return PatternPlan(
            spec=replace(
                spec,
                far_field=far_field_request(pattern_step_deg, ground),
                pattern_frequencies_hz=pattern_frequencies,
            ),
            budget=budget,
            diagnostic=diagnostic,
        )
    return PatternPlan(
        spec=replace(
            spec,
            far_field=FarFieldRequest(enabled=False),
            pattern_frequencies_hz=(),
        ),
        budget=budget,
        diagnostic=Diagnostic(
            code="solver.pattern_disabled",
            severity=Severity.WARNING,
            message=(
                "far-field pattern disabled: the sweep is too large for the project storage limit"
            ),
            field="far_field",
        ),
    )


def fit_band_specs_to_budget(
    model: AntennaModel,
    specs: tuple[SimulationSpec, ...],
    *,
    requested_step_deg: float | None,
) -> tuple[tuple[SimulationSpec, ...], PatternBudget | None]:
    """Choose one shared pattern step for a per-band batch."""

    if not specs:
        return specs, None
    ground = model.environment.ground
    budget = choose_batch_pattern_step(
        frequency_counts=tuple(spec.frequency_plan.count for spec in specs),
        segment_counts=tuple(_segment_count(model, spec) for spec in specs),
        candidate_steps=CANDIDATE_PATTERN_STEPS_DEG,
        counts_for_step=lambda step: pattern_counts(step, ground),
        requested_step_deg=requested_step_deg,
        pattern_frequency_counts=tuple(max(1, len(spec.pattern_frequencies_hz)) for spec in specs),
    )
    if not budget.far_field_enabled:
        return (
            tuple(
                replace(
                    spec,
                    far_field=FarFieldRequest(enabled=False),
                    pattern_frequencies_hz=(),
                )
                for spec in specs
            ),
            budget,
        )
    if budget.pattern_step_deg is None:
        return specs, budget
    request = far_field_request(budget.pattern_step_deg, ground)
    return tuple(replace(spec, far_field=request) for spec in specs), budget
