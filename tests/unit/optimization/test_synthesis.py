# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for bounded feed-point impedance synthesis."""

from __future__ import annotations

import pytest

from antennadesk.domain.optimization.synthesis import (
    SynthesisEvaluation,
    SynthesisStatus,
    SynthesisTarget,
    SynthesisVariable,
    rank_evaluations,
    swr_for_resistance,
    synthesize_grid,
)


def _target() -> SynthesisTarget:
    return SynthesisTarget(7_100_000.0, 50.0, 0.0)


def _evaluate(values: dict[str, float]) -> SynthesisEvaluation:
    x = values["x"]
    y = values["y"]
    impedance = complex(50.0 + 20.0 * (x - 2.0), 10.0 * (y - 3.0))
    return SynthesisEvaluation(0, dict(values), impedance)


def test_synthesis_finds_best_grid_point() -> None:
    result = synthesize_grid(
        _evaluate,
        (
            SynthesisVariable("x", 1.0, 3.0),
            SynthesisVariable("y", 2.0, 4.0),
        ),
        _target(),
        max_evaluations=9,
    )

    assert result.status is SynthesisStatus.CONVERGED
    assert result.best_values == {"x": 2.0, "y": 3.0}
    assert result.best_impedance_ohm == pytest.approx(50.0 + 0.0j)
    assert result.best_error_ohm == pytest.approx(0.0)
    assert len(result.evaluations) == 9


def test_swr_for_resistance_uses_the_requested_reference() -> None:
    assert swr_for_resistance(complex(100.0, 0.0), 100.0) == pytest.approx(1.0)
    assert swr_for_resistance(complex(50.0, 0.0), 100.0) == pytest.approx(2.0)
    assert swr_for_resistance(complex(-100.0, 0.0), 100.0) == pytest.approx(float("inf"))


def test_synthesis_target_swr_uses_the_target_resistance() -> None:
    target = SynthesisTarget(7_100_000.0, 100.0, 25.0)
    reactive_target = SynthesisTarget(7_100_000.0, 100.0, -40.0)

    assert target.swr(complex(100.0, 0.0)) == pytest.approx(1.0)
    assert target.swr(complex(50.0, 25.0)) == reactive_target.swr(complex(50.0, 25.0))


def test_rank_evaluations_orders_by_impedance_error() -> None:
    target = _target()
    evaluations = (
        SynthesisEvaluation(1, {"x": 1.0}, complex(70.0, 0.0)),
        SynthesisEvaluation(2, {"x": 2.0}, complex(50.0, 0.0)),
        SynthesisEvaluation(3, {"x": 3.0}, None, error="failed"),
    )

    ordered = rank_evaluations(evaluations, target)

    assert [evaluation.index for evaluation in ordered] == [2, 1, 3]


def test_synthesis_reports_cancellation() -> None:
    result = synthesize_grid(
        _evaluate,
        (SynthesisVariable("x", 1.0, 3.0),),
        _target(),
        max_evaluations=9,
        cancel_check=lambda: True,
    )

    assert result.status is SynthesisStatus.CANCELLED
    assert result.best_values is None
    assert not result.evaluations


def test_synthesis_reports_no_valid_evaluation() -> None:
    def failing(values: dict[str, float]) -> SynthesisEvaluation:
        return SynthesisEvaluation(0, dict(values), None, error="solver failed")

    result = synthesize_grid(
        failing,
        (SynthesisVariable("x", 1.0, 3.0),),
        _target(),
        max_evaluations=9,
    )

    assert result.status is SynthesisStatus.ERROR
    assert result.best_values is None
    assert result.evaluations[0].error == "solver failed"


def test_synthesis_target_requires_positive_resistance() -> None:
    with pytest.raises(ValueError, match="resistance"):
        SynthesisTarget(7_100_000.0, 0.0, 0.0)


def test_synthesis_variable_requires_ordered_bounds() -> None:
    with pytest.raises(ValueError, match="maximum"):
        SynthesisVariable("x", 3.0, 1.0)
