# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.simulation.bands import (
    amateur_band_for,
    band_snapshot_frequencies,
)
from antennadesk.domain.simulation.frequency import FrequencyPlan


def test_amateur_band_lookup() -> None:
    assert amateur_band_for(7_100_000.0).name == "40m"
    assert amateur_band_for(14_100_000.0).name == "20m"
    assert amateur_band_for(7_400_000.0) is None
    assert amateur_band_for(10_158_000.0).name == "30m"
    assert amateur_band_for(24_700_000.0).name == "12m"
    assert amateur_band_for(70_100_000.0).name == "4m"
    assert amateur_band_for(145_500_000.0).name == "2m"
    assert amateur_band_for(223_500_000.0).name == "1.25m"
    assert amateur_band_for(433_000_000.0).name == "70cm"
    assert amateur_band_for(915_000_000.0).name == "33cm"
    assert amateur_band_for(1_296_000_000.0).name == "23cm"
    assert amateur_band_for(10_300_000.0) is None


def test_band_snapshots_cover_multiple_hf_bands() -> None:
    plan = FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 200)

    snapshots = band_snapshot_frequencies(plan)

    assert len(snapshots) == 9
    assert snapshots[0] == pytest.approx(3_766_000.0, abs=200_000.0)
    assert any(6_900_000.0 <= value <= 7_300_000.0 for value in snapshots)
    assert any(13_900_000.0 <= value <= 14_400_000.0 for value in snapshots)
    assert any(20_900_000.0 <= value <= 21_500_000.0 for value in snapshots)
    assert any(27_900_000.0 <= value <= 29_800_000.0 for value in snapshots)
    assert all(plan.start_hz <= value <= plan.stop_hz for value in snapshots)


def test_band_snapshots_prefer_the_design_frequency() -> None:
    plan = FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 200)

    snapshots = band_snapshot_frequencies(
        plan,
        preferred_frequency_hz=14_100_000.0,
    )

    assert any(abs(value - 14_100_000.0) <= 200_000.0 for value in snapshots)


def test_band_snapshots_fill_a_narrow_single_band_plan() -> None:
    plan = FrequencyPlan.sweep(6_700_000.0, 7_500_000.0, 31)

    snapshots = band_snapshot_frequencies(
        plan,
        preferred_frequency_hz=7_100_000.0,
    )

    assert len(snapshots) == 5
    assert snapshots[0] == pytest.approx(plan.start_hz)
    assert snapshots[-1] == pytest.approx(plan.stop_hz)
    assert any(abs(value - 7_100_000.0) < 1.0 for value in snapshots)


def test_band_snapshots_respect_the_maximum() -> None:
    plan = FrequencyPlan.sweep(1_800_000.0, 54_000_000.0, 200)

    snapshots = band_snapshot_frequencies(plan, max_count=5)

    assert len(snapshots) == 5
    with pytest.raises(ValueError, match="max_count"):
        band_snapshot_frequencies(plan, min_count=6, max_count=5)


def test_amateur_band_lookup_by_stable_id() -> None:
    from antennadesk.domain.simulation.bands import amateur_band_by_id

    assert amateur_band_by_id("40m").start_hz == 7_000_000.0
    assert amateur_band_by_id("23cm").stop_hz == 1_300_000_000.0
    assert amateur_band_by_id("unknown") is None


def test_band_snapshots_include_vhf_and_uhf_bands() -> None:
    plan = FrequencyPlan.sweep(50_000_000.0, 1_300_000_000.0, 1_000)

    snapshots = band_snapshot_frequencies(plan, max_count=20)

    assert any(144_000_000.0 <= value <= 148_000_000.0 for value in snapshots)
    assert any(420_000_000.0 <= value <= 450_000_000.0 for value in snapshots)
    assert any(1_240_000_000.0 <= value <= 1_300_000_000.0 for value in snapshots)
