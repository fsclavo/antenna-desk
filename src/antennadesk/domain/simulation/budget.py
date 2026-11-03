# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Estimate simulation storage and choose the finest pattern that fits."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

BASE_PROJECT_BYTES = 50_000
BYTES_PER_FAR_FIELD_POINT = 430
BYTES_PER_CURRENT_SAMPLE = 360
BYTES_PER_FREQUENCY = 20
DEFAULT_MAX_PROJECT_BYTES = 24 * 1024 * 1024
ESTIMATED_COMPRESSION_RATIO = 6.0


@dataclass(frozen=True, slots=True)
class PatternBudget:
    """The chosen far-field sampling and its estimated project size."""

    pattern_step_deg: float | None
    estimated_project_bytes: int
    estimated_json_bytes: int
    far_field_points_per_frequency: int
    pattern_frequency_count: int
    requested_step_deg: float | None
    far_field_enabled: bool
    reduced: bool


def estimate_project_bytes(
    *,
    frequency_count: int,
    far_field_points_per_frequency: int,
    segment_count: int,
    pattern_frequency_count: int | None = None,
) -> int:
    """Estimate the persisted project JSON size for one simulation run.

    The estimate is calibrated against the G5RV preset and deliberately
    conservative. It includes the raw NEC output plus the normalized
    far-field/current records that are persisted in the project.

    ``frequency_count`` is the impedance/current sweep. ``pattern_frequency_count``
    is the number of far-field snapshots; when omitted, every sweep frequency is
    assumed to carry a pattern.
    """

    if frequency_count < 1:
        raise ValueError("frequency_count must be at least 1")
    if far_field_points_per_frequency < 0:
        raise ValueError("far_field_points_per_frequency must not be negative")
    if segment_count < 0:
        raise ValueError("segment_count must not be negative")
    snapshots = frequency_count if pattern_frequency_count is None else pattern_frequency_count
    if snapshots < 0:
        raise ValueError("pattern_frequency_count must not be negative")
    sweep_bytes = frequency_count * (segment_count * BYTES_PER_CURRENT_SAMPLE + BYTES_PER_FREQUENCY)
    pattern_bytes = snapshots * (
        far_field_points_per_frequency * BYTES_PER_FAR_FIELD_POINT
        + segment_count * BYTES_PER_CURRENT_SAMPLE
        + BYTES_PER_FREQUENCY
    )
    return BASE_PROJECT_BYTES + sweep_bytes + pattern_bytes


def estimate_compressed_project_bytes(
    *,
    frequency_count: int,
    far_field_points_per_frequency: int,
    segment_count: int,
    pattern_frequency_count: int | None = None,
) -> int:
    """Estimate the compressed on-disk project size.

    New project files are gzip-compressed. The ratio is deliberately
    conservative and calibrated against real G5RV runs.
    """

    raw = estimate_project_bytes(
        frequency_count=frequency_count,
        far_field_points_per_frequency=far_field_points_per_frequency,
        segment_count=segment_count,
        pattern_frequency_count=pattern_frequency_count,
    )
    return max(1, math.ceil(raw / ESTIMATED_COMPRESSION_RATIO))


def choose_batch_pattern_step(
    *,
    frequency_counts: Sequence[int],
    segment_counts: Sequence[int],
    candidate_steps: Sequence[float],
    counts_for_step: Callable[[float], tuple[int, int]],
    requested_step_deg: float | None = None,
    pattern_frequency_count: int = 1,
    max_project_bytes: int = DEFAULT_MAX_PROJECT_BYTES,
) -> PatternBudget:
    """Choose one pattern step that fits a whole per-band batch.

    Each band keeps its own sweep and segmentation, but the angular step is
    shared. The estimate is the sum of the per-band project estimates.
    """

    if not frequency_counts or len(frequency_counts) != len(segment_counts):
        raise ValueError("frequency_counts and segment_counts must be non-empty and aligned")
    if pattern_frequency_count < 1:
        raise ValueError("pattern_frequency_count must be at least 1")
    if not candidate_steps:
        raise ValueError("candidate_steps must not be empty")

    steps = sorted({float(step) for step in candidate_steps})
    if requested_step_deg is None:
        candidates = steps
    else:
        candidates = [step for step in steps if step >= requested_step_deg]
        if not candidates:
            candidates = [max(steps)]

    total_patterns = len(frequency_counts) * pattern_frequency_count
    for step in candidates:
        theta_count, phi_count = counts_for_step(step)
        points = theta_count * phi_count
        estimated_json = sum(
            estimate_project_bytes(
                frequency_count=frequency_count,
                far_field_points_per_frequency=points,
                segment_count=segment_count,
                pattern_frequency_count=pattern_frequency_count,
            )
            for frequency_count, segment_count in zip(frequency_counts, segment_counts, strict=True)
        )
        estimated = max(1, math.ceil(estimated_json / ESTIMATED_COMPRESSION_RATIO))
        if estimated <= max_project_bytes:
            return PatternBudget(
                pattern_step_deg=step,
                estimated_project_bytes=estimated,
                estimated_json_bytes=estimated_json,
                far_field_points_per_frequency=points,
                pattern_frequency_count=total_patterns,
                requested_step_deg=requested_step_deg,
                far_field_enabled=True,
                reduced=requested_step_deg is not None and step != requested_step_deg,
            )

    estimated_json_without = sum(
        estimate_project_bytes(
            frequency_count=frequency_count,
            far_field_points_per_frequency=0,
            segment_count=segment_count,
            pattern_frequency_count=0,
        )
        for frequency_count, segment_count in zip(frequency_counts, segment_counts, strict=True)
    )
    estimated_without = max(
        1,
        math.ceil(estimated_json_without / ESTIMATED_COMPRESSION_RATIO),
    )
    return PatternBudget(
        pattern_step_deg=None,
        estimated_project_bytes=estimated_without,
        estimated_json_bytes=estimated_json_without,
        far_field_points_per_frequency=0,
        pattern_frequency_count=0,
        requested_step_deg=requested_step_deg,
        far_field_enabled=False,
        reduced=True,
    )


def choose_pattern_step(
    *,
    frequency_count: int,
    segment_count: int,
    candidate_steps: Sequence[float],
    counts_for_step: Callable[[float], tuple[int, int]],
    requested_step_deg: float | None = None,
    pattern_frequency_count: int | None = None,
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
        estimated_json = estimate_project_bytes(
            frequency_count=frequency_count,
            far_field_points_per_frequency=points,
            segment_count=segment_count,
            pattern_frequency_count=pattern_frequency_count,
        )
        estimated = max(
            1,
            math.ceil(estimated_json / ESTIMATED_COMPRESSION_RATIO),
        )
        if estimated <= max_project_bytes:
            return PatternBudget(
                pattern_step_deg=step,
                estimated_project_bytes=estimated,
                estimated_json_bytes=estimated_json,
                far_field_points_per_frequency=points,
                pattern_frequency_count=(
                    frequency_count if pattern_frequency_count is None else pattern_frequency_count
                ),
                requested_step_deg=requested_step_deg,
                far_field_enabled=True,
                reduced=requested_step_deg is not None and step != requested_step_deg,
            )

    estimated_json_without = estimate_project_bytes(
        frequency_count=frequency_count,
        far_field_points_per_frequency=0,
        segment_count=segment_count,
        pattern_frequency_count=0,
    )
    estimated_without = max(
        1,
        math.ceil(estimated_json_without / ESTIMATED_COMPRESSION_RATIO),
    )
    return PatternBudget(
        pattern_step_deg=None,
        estimated_project_bytes=estimated_without,
        estimated_json_bytes=estimated_json_without,
        far_field_points_per_frequency=0,
        pattern_frequency_count=0,
        requested_step_deg=requested_step_deg,
        far_field_enabled=False,
        reduced=True,
    )
