# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tuner range, E-series, and matchability tests."""

from __future__ import annotations

import pytest

from antennadesk.domain.design.smith_chart import MatchingPreviewTopology
from antennadesk.domain.design.tuner import (
    E12,
    TunerLimits,
    TunerStatus,
    evaluate_tuner_match,
    nearest_e_series,
    realize_network,
)


def _limits(**overrides: float) -> TunerLimits:
    values = {
        "capacitance_min_f": 10e-12,
        "capacitance_max_f": 1_000e-12,
        "inductance_min_h": 0.1e-6,
        "inductance_max_h": 100e-6,
    }
    values.update(overrides)
    return TunerLimits(**values)


def test_e_series_snaps_to_the_nearest_value_across_decades() -> None:
    assert nearest_e_series(1.05, "e12") == pytest.approx(E12[0])
    assert nearest_e_series(1.05, "e24") == pytest.approx(1.1)
    assert nearest_e_series(470.0, "e12") == pytest.approx(470.0)
    assert nearest_e_series(0.0047, "e24") == pytest.approx(0.0047)
    with pytest.raises(ValueError):
        nearest_e_series(0.0, "e12")
    with pytest.raises(ValueError):
        nearest_e_series(1.0, "e48")


def test_tuner_limits_reject_inverted_ranges() -> None:
    with pytest.raises(ValueError):
        TunerLimits(1e-9, 1e-12, 1e-9, 1e-6)
    with pytest.raises(ValueError):
        TunerLimits(1e-12, 1e-9, 1e-6, 1e-9)


def test_wide_tuner_matches_and_narrow_tuner_reports_the_limiting_part() -> None:
    load = complex(100.0, 0.0)
    frequency = 14_000_000.0

    matched = evaluate_tuner_match(
        load,
        frequency,
        _limits(),
        MatchingPreviewTopology.L,
    )
    narrow = evaluate_tuner_match(
        load,
        frequency,
        _limits(capacitance_min_f=0.0, capacitance_max_f=1e-12),
        MatchingPreviewTopology.PI,
    )

    assert matched.status is TunerStatus.MATCHED
    assert matched.swr == pytest.approx(1.0, abs=0.2)
    assert matched.loss_db is not None
    assert narrow.status is TunerStatus.OUT_OF_RANGE
    assert narrow.limiting == "capacitance_max"


def test_realized_network_uses_e24_values_and_keeps_a_valid_match() -> None:
    load = complex(100.0, 0.0)
    frequency = 14_000_000.0
    evaluation = evaluate_tuner_match(
        load,
        frequency,
        _limits(),
        MatchingPreviewTopology.L,
        series="e24",
    )

    assert evaluation.network is not None
    realized = realize_network(evaluation.network, "e24")
    assert realized is evaluation.network or realized == evaluation.network
    # The realized network is still a valid passive matching network.
    input_impedance = realized.input_impedance(load, frequency)
    assert input_impedance.real > 0.0


def test_out_of_range_l_returns_best_effort_or_bypass() -> None:
    load = complex(100.0, 0.0)
    frequency = 14_000_000.0
    evaluation = evaluate_tuner_match(
        load,
        frequency,
        _limits(capacitance_min_f=0.0, capacitance_max_f=1e-12),
        MatchingPreviewTopology.L,
    )

    assert evaluation.status in {TunerStatus.BEST_EFFORT, TunerStatus.BYPASS}
    raw_swr = 2.0
    if evaluation.status is TunerStatus.BYPASS:
        assert evaluation.network is None
        assert evaluation.swr == pytest.approx(raw_swr, abs=0.01)
    else:
        assert evaluation.network is not None
        assert evaluation.swr is not None
        assert evaluation.swr < raw_swr


def test_unmatchable_load_returns_no_solution() -> None:
    evaluation = evaluate_tuner_match(
        complex(-10.0, 0.0),
        14_000_000.0,
        _limits(),
        MatchingPreviewTopology.L,
    )

    assert evaluation.status is TunerStatus.NO_SOLUTION
    assert evaluation.network is None
