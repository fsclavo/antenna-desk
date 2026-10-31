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
