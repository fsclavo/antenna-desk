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
