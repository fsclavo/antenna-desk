# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Estimate simulation storage and choose the finest pattern that fits."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

BASE_PROJECT_BYTES = 50_000
BYTES_PER_FAR_FIELD_POINT = 430
BYTES_PER_CURRENT_SAMPLE = 360
BYTES_PER_FREQUENCY = 20
DEFAULT_MAX_PROJECT_BYTES = 9_500_000


@dataclass(frozen=True, slots=True)
class PatternBudget:
    """The chosen far-field sampling and its estimated project size."""

    pattern_step_deg: float | None
    estimated_project_bytes: int
    far_field_points_per_frequency: int
    requested_step_deg: float | None
    far_field_enabled: bool
    reduced: bool


def estimate_project_bytes(
    *,
    frequency_count: int,
    far_field_points_per_frequency: int,
    segment_count: int,
) -> int:
    """Estimate the persisted project JSON size for one simulation run.

    The estimate is calibrated against the G5RV preset and deliberately
    conservative. It includes the raw NEC output plus the normalized
    far-field/current records that are persisted in the project.
    """

    if frequency_count < 1:
        raise ValueError("frequency_count must be at least 1")
    if far_field_points_per_frequency < 0:
        raise ValueError("far_field_points_per_frequency must not be negative")
    if segment_count < 0:
        raise ValueError("segment_count must not be negative")
    per_frequency = (
        far_field_points_per_frequency * BYTES_PER_FAR_FIELD_POINT
        + segment_count * BYTES_PER_CURRENT_SAMPLE
        + BYTES_PER_FREQUENCY
    )
    return BASE_PROJECT_BYTES + frequency_count * per_frequency


def choose_pattern_step(
    *,
    frequency_count: int,
    segment_count: int,
    candidate_steps: Sequence[float],
    counts_for_step: Callable[[float], tuple[int, int]],
    requested_step_deg: float | None = None,
    max_project_bytes: int = DEFAULT_MAX_PROJECT_BYTES,
) -> PatternBudget:
    """Choose the finest pattern step that fits the project budget.

    ``candidate_steps`` may be in any order; the function sorts them from finest
    to coarsest. A requested step is treated as a maximum resolution: the
    function may coarsen it, but never choose a finer step than requested.
    """

    if not candidate_steps:
        raise ValueError("candidate_steps must not be empty")
    steps = sorted({float(step) for step in candidate_steps})
    if requested_step_deg is None:
        candidates = steps
    else:
        candidates = [step for step in steps if step >= requested_step_deg]
        if not candidates:
            candidates = [max(steps)]

    for step in candidates:
        theta_count, phi_count = counts_for_step(step)
        points = theta_count * phi_count
        estimated = estimate_project_bytes(
            frequency_count=frequency_count,
            far_field_points_per_frequency=points,
            segment_count=segment_count,
        )
        if estimated <= max_project_bytes:
            return PatternBudget(
                pattern_step_deg=step,
                estimated_project_bytes=estimated,
                far_field_points_per_frequency=points,
                requested_step_deg=requested_step_deg,
                far_field_enabled=True,
                reduced=requested_step_deg is not None and step != requested_step_deg,
            )

    estimated_without = estimate_project_bytes(
        frequency_count=frequency_count,
        far_field_points_per_frequency=0,
        segment_count=segment_count,
    )
    return PatternBudget(
        pattern_step_deg=None,
        estimated_project_bytes=estimated_without,
        far_field_points_per_frequency=0,
        requested_step_deg=requested_step_deg,
        far_field_enabled=False,
        reduced=True,
    )
