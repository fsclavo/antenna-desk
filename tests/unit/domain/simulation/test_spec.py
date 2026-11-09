# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Simulation specification defaults."""

from __future__ import annotations

import pytest

from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.spec import (
    DEFAULT_TIMEOUT_S,
    MAX_TIMEOUT_S,
    SimulationSpec,
)


def test_default_solver_timeout_is_three_minutes() -> None:
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))

    assert spec.timeout_s == pytest.approx(180.0)
    assert pytest.approx(180.0) == DEFAULT_TIMEOUT_S


def test_solver_timeout_accepts_an_override_and_rejects_too_large_values() -> None:
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        timeout_s=300.0,
    )
    assert spec.timeout_s == pytest.approx(300.0)

    with pytest.raises(ValueError, match="timeout_s"):
        SimulationSpec(
            frequency_plan=FrequencyPlan.single(7_100_000.0),
            timeout_s=MAX_TIMEOUT_S + 1.0,
        )
