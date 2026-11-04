# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.simulation.budget import (
    DEFAULT_MAX_PROJECT_BYTES,
    choose_pattern_step,
    estimate_compressed_project_bytes,
    estimate_project_bytes,
)


def _counts(step_deg: float) -> tuple[int, int]:
    return round(90.0 / step_deg) + 1, round(360.0 / step_deg) + 1


def test_project_size_estimate_rejects_the_failing_g5rv_default() -> None:
    estimate = estimate_project_bytes(
        frequency_count=301,
        far_field_points_per_frequency=19 * 73,
        segment_count=66,
    )

    assert estimate > DEFAULT_MAX_PROJECT_BYTES


def test_project_size_estimate_accepts_the_41_point_g5rv_default() -> None:
    estimate = estimate_project_bytes(
        frequency_count=41,
        far_field_points_per_frequency=10 * 37,
        segment_count=66,
    )

    assert estimate < DEFAULT_MAX_PROJECT_BYTES


def test_auto_pattern_uses_the_finest_step_that_fits() -> None:
    budget = choose_pattern_step(
        frequency_count=41,
        segment_count=66,
        candidate_steps=(1.0, 2.0, 5.0, 10.0),
        counts_for_step=_counts,
    )

    assert budget.far_field_enabled is True
    assert budget.pattern_step_deg == 2.0
    assert budget.reduced is False


def test_auto_pattern_coarsens_for_larger_sweeps() -> None:
    few = choose_pattern_step(
        frequency_count=11,
        segment_count=66,
        candidate_steps=(1.0, 2.0, 5.0, 10.0),
        counts_for_step=_counts,
    )
    tiny = choose_pattern_step(
        frequency_count=1,
        segment_count=66,
        candidate_steps=(1.0, 2.0, 5.0, 10.0),
        counts_for_step=_counts,
    )

    assert few.pattern_step_deg == 2.0
    assert tiny.pattern_step_deg == 1.0


def test_auto_pattern_uses_coarser_fallbacks_for_larger_sweeps() -> None:
    mid = choose_pattern_step(
        frequency_count=61,
        segment_count=66,
        candidate_steps=(1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        counts_for_step=_counts,
    )
    wide = choose_pattern_step(
        frequency_count=301,
        segment_count=66,
        candidate_steps=(1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        counts_for_step=_counts,
    )

    assert mid.pattern_step_deg == 5.0
    assert wide.pattern_step_deg == 10.0


def test_pattern_snapshots_allow_a_fine_pattern_for_a_dense_sweep() -> None:
    budget = choose_pattern_step(
        frequency_count=200,
        pattern_frequency_count=5,
        segment_count=66,
        candidate_steps=(1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        counts_for_step=_counts,
    )

    assert budget.pattern_step_deg == 1.0
    assert budget.pattern_frequency_count == 5
    assert budget.far_field_enabled is True
    assert budget.estimated_project_bytes < DEFAULT_MAX_PROJECT_BYTES


def test_many_pattern_snapshots_use_the_finest_compressed_step() -> None:
    thirteen = choose_pattern_step(
        frequency_count=200,
        pattern_frequency_count=13,
        segment_count=66,
        candidate_steps=(1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        counts_for_step=_counts,
    )
    twenty_one = choose_pattern_step(
        frequency_count=200,
        pattern_frequency_count=21,
        segment_count=66,
        candidate_steps=(1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        counts_for_step=_counts,
    )

    assert thirteen.pattern_step_deg == 2.0
    assert twenty_one.pattern_step_deg == 2.0
    assert thirteen.estimated_project_bytes < DEFAULT_MAX_PROJECT_BYTES
    assert twenty_one.estimated_project_bytes < DEFAULT_MAX_PROJECT_BYTES
    assert thirteen.estimated_json_bytes > thirteen.estimated_project_bytes


def test_project_size_estimate_separates_sweep_and_pattern_counts() -> None:
    dense_pattern = estimate_project_bytes(
        frequency_count=200,
        pattern_frequency_count=200,
        far_field_points_per_frequency=1387,
        segment_count=66,
    )
    snapshots = estimate_project_bytes(
        frequency_count=200,
        pattern_frequency_count=5,
        far_field_points_per_frequency=1387,
        segment_count=66,
    )

    assert snapshots < dense_pattern
    compressed = estimate_compressed_project_bytes(
        frequency_count=200,
        pattern_frequency_count=5,
        far_field_points_per_frequency=1387,
        segment_count=66,
    )
    assert compressed < snapshots
    with pytest.raises(ValueError, match="pattern_frequency_count"):
        estimate_project_bytes(
            frequency_count=10,
            pattern_frequency_count=-1,
            far_field_points_per_frequency=1,
            segment_count=1,
        )


def test_auto_pattern_disables_far_field_when_nothing_fits() -> None:
    budget = choose_pattern_step(
        frequency_count=1_000,
        segment_count=2_000,
        candidate_steps=(1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        counts_for_step=_counts,
    )

    assert budget.far_field_enabled is False
    assert budget.pattern_step_deg is None
    assert budget.far_field_points_per_frequency == 0
    assert budget.reduced is True


def test_requested_step_is_a_maximum_and_can_only_coarsen() -> None:
    reduced = choose_pattern_step(
        frequency_count=41,
        segment_count=66,
        candidate_steps=(1.0, 2.0, 5.0, 10.0),
        counts_for_step=_counts,
        requested_step_deg=5.0,
    )
    exact = choose_pattern_step(
        frequency_count=41,
        segment_count=66,
        candidate_steps=(1.0, 2.0, 5.0, 10.0),
        counts_for_step=_counts,
        requested_step_deg=10.0,
    )

    assert reduced.pattern_step_deg == 5.0
    assert reduced.reduced is False
    assert exact.pattern_step_deg == 10.0
    assert exact.reduced is False


def test_budget_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="frequency_count"):
        estimate_project_bytes(
            frequency_count=0,
            far_field_points_per_frequency=1,
            segment_count=1,
        )
    with pytest.raises(ValueError, match="candidate_steps"):
        choose_pattern_step(
            frequency_count=1,
            segment_count=1,
            candidate_steps=(),
            counts_for_step=_counts,
        )


def test_batch_pattern_budget_sums_every_band() -> None:
    from antennadesk.domain.simulation.budget import choose_batch_pattern_step

    budget = choose_batch_pattern_step(
        frequency_counts=(15, 15, 15),
        segment_counts=(33, 33, 33),
        candidate_steps=(1.0, 2.0, 5.0, 10.0),
        counts_for_step=_counts,
        pattern_frequency_count=1,
    )

    assert budget.far_field_enabled is True
    assert budget.pattern_step_deg in {1.0, 2.0, 5.0, 10.0}
    assert budget.pattern_frequency_count == 3
    assert budget.estimated_project_bytes < DEFAULT_MAX_PROJECT_BYTES


def test_batch_pattern_budget_accepts_per_band_pattern_counts() -> None:
    from antennadesk.domain.simulation.budget import choose_batch_pattern_step

    budget = choose_batch_pattern_step(
        frequency_counts=(15, 15, 15),
        segment_counts=(33, 33, 33),
        candidate_steps=(1.0, 2.0, 5.0, 10.0),
        counts_for_step=_counts,
        pattern_frequency_counts=(5, 5, 3),
    )

    assert budget.far_field_enabled is True
    assert budget.pattern_frequency_count == 13


def test_batch_pattern_budget_rejects_misaligned_pattern_counts() -> None:
    from antennadesk.domain.simulation.budget import choose_batch_pattern_step

    with pytest.raises(ValueError, match="pattern_frequency_counts"):
        choose_batch_pattern_step(
            frequency_counts=(15, 15),
            segment_counts=(33, 33),
            candidate_steps=(1.0, 2.0, 5.0, 10.0),
            counts_for_step=_counts,
            pattern_frequency_counts=(5,),
        )


def test_batch_pattern_budget_respects_a_requested_maximum() -> None:
    from antennadesk.domain.simulation.budget import choose_batch_pattern_step

    budget = choose_batch_pattern_step(
        frequency_counts=(15, 15),
        segment_counts=(33, 33),
        candidate_steps=(1.0, 2.0, 5.0, 10.0),
        counts_for_step=_counts,
        pattern_frequency_count=1,
        requested_step_deg=5.0,
    )

    assert budget.pattern_step_deg is not None
    assert budget.pattern_step_deg >= 5.0
