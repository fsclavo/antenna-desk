# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.simulation.frequency import MAX_FREQUENCIES, FrequencyPlan


def test_single_frequency() -> None:
    plan = FrequencyPlan.single(7_100_000.0)
    assert plan.is_single is True
    assert plan.step_hz == 0.0
    assert plan.frequencies_hz == (7_100_000.0,)


def test_sweep() -> None:
    plan = FrequencyPlan.sweep(6_900_000.0, 7_300_000.0, 21)
    assert plan.is_single is False
    assert plan.step_hz == pytest.approx(20_000.0)
    assert len(plan.frequencies_hz) == 21
    assert plan.frequencies_hz[0] == pytest.approx(6_900_000.0)
    assert plan.frequencies_hz[-1] == pytest.approx(7_300_000.0)


def test_single_requires_equal_start_and_stop() -> None:
    with pytest.raises(ValueError, match="start_hz == stop_hz"):
        FrequencyPlan(start_hz=7_000_000.0, stop_hz=7_100_000.0, count=1)


def test_stop_must_not_be_below_start() -> None:
    with pytest.raises(ValueError, match="greater than or equal"):
        FrequencyPlan(start_hz=7_100_000.0, stop_hz=7_000_000.0, count=2)


def test_count_must_be_positive_and_bounded() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        FrequencyPlan(start_hz=7_000_000.0, stop_hz=7_000_000.0, count=0)
    with pytest.raises(ValueError, match="must not exceed"):
        FrequencyPlan(
            start_hz=7_000_000.0,
            stop_hz=7_100_000.0,
            count=MAX_FREQUENCIES + 1,
        )


def test_sweep_requires_at_least_two_points() -> None:
    with pytest.raises(ValueError, match="at least two"):
        FrequencyPlan.sweep(7_000_000.0, 7_100_000.0, 1)


def test_frequencies_must_be_positive() -> None:
    with pytest.raises(ValueError, match="positive"):
        FrequencyPlan.single(0.0)
