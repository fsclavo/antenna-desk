# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.spec import SimulationSpec


def test_snapshot_frequencies_keep_the_endpoints_and_the_requested_count() -> None:
    plan = FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 200)

    snapshots = plan.snapshot_frequencies(5)

    assert len(snapshots) == 5
    assert snapshots[0] == pytest.approx(plan.start_hz)
    assert snapshots[-1] == pytest.approx(plan.stop_hz)
    assert all(
        any(abs(snapshot - frequency) < 1e-6 for frequency in plan.frequencies_hz)
        for snapshot in snapshots
    )


def test_snapshot_frequencies_include_the_preferred_design_frequency() -> None:
    plan = FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 200)
    preferred = 14_100_000.0

    snapshots = plan.snapshot_frequencies(5, preferred_frequency_hz=preferred)
    nearest = min(plan.frequencies_hz, key=lambda value: abs(value - preferred))

    assert len(snapshots) == 5
    assert snapshots[0] == pytest.approx(plan.start_hz)
    assert snapshots[-1] == pytest.approx(plan.stop_hz)
    assert any(abs(snapshot - nearest) < 1e-6 for snapshot in snapshots)


def test_snapshot_frequencies_return_the_whole_short_plan() -> None:
    plan = FrequencyPlan.sweep(7_000_000.0, 7_200_000.0, 5)

    assert plan.snapshot_frequencies(10) == plan.frequencies_hz
    assert plan.snapshot_frequencies(5) == plan.frequencies_hz
    assert plan.snapshot_frequencies(1) == (plan.start_hz,)
    with pytest.raises(ValueError, match="max_count"):
        plan.snapshot_frequencies(0)


def test_simulation_spec_snaps_pattern_frequencies_to_the_plan() -> None:
    plan = FrequencyPlan.sweep(7_000_000.0, 7_200_000.0, 11)

    spec = SimulationSpec(
        frequency_plan=plan,
        pattern_frequencies_hz=(7_044_000.0, 7_100_000.0, 7_200_000.0),
    )

    assert spec.pattern_frequencies_hz == pytest.approx((7_040_000.0, 7_100_000.0, 7_200_000.0))


def test_simulation_spec_rejects_pattern_frequencies_outside_the_plan() -> None:
    plan = FrequencyPlan.sweep(7_000_000.0, 7_200_000.0, 11)

    with pytest.raises(ValueError, match="outside the frequency plan"):
        SimulationSpec(
            frequency_plan=plan,
            pattern_frequencies_hz=(6_900_000.0,),
        )
    with pytest.raises(ValueError, match="outside the frequency plan"):
        SimulationSpec(
            frequency_plan=plan,
            pattern_frequencies_hz=(7_300_000.0,),
        )


def test_simulation_spec_single_frequency_pattern_must_match() -> None:
    plan = FrequencyPlan.single(7_100_000.0)

    spec = SimulationSpec(
        frequency_plan=plan,
        pattern_frequencies_hz=(7_100_000.0,),
    )
    assert spec.pattern_frequencies_hz == (7_100_000.0,)
    with pytest.raises(ValueError, match="single-frequency plan"):
        SimulationSpec(
            frequency_plan=plan,
            pattern_frequencies_hz=(7_200_000.0,),
        )
