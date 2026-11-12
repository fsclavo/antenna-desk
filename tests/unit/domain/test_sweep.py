# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded parameter-sweep axes and result summaries."""

from __future__ import annotations

import pytest

from antennadesk.domain.design.sweep import (
    MAX_SWEEP_POINTS,
    ParameterSweepResult,
    SweepAxis,
    SweepMetric,
    SweepPlan,
    SweepPoint,
    axis_values,
)
from antennadesk.domain.optimization.variables import OptimizationVariable, VariableKind


def _continuous() -> OptimizationVariable:
    return OptimizationVariable(
        "length_m",
        "field.length",
        "optimize.group.geometry",
        8.0,
        12.0,
        step=0.1,
    )


def _integer() -> OptimizationVariable:
    return OptimizationVariable(
        "radial_count",
        "vertical.radial_count",
        "optimize.group.loads",
        4.0,
        10.0,
        kind=VariableKind.INTEGER,
        unit="count",
        step=1.0,
    )


def _axis(name: str = "length_m", values: tuple[float, ...] = (9.0, 10.0, 11.0)) -> SweepAxis:
    return SweepAxis(name=name, label_key="field.length", unit="m", values=values)


def test_axis_values_are_bounded_and_ordered() -> None:
    values = axis_values(_continuous(), 9.0, 11.0, 5)

    assert values == (9.0, 9.5, 10.0, 10.5, 11.0)


def test_integer_axis_deduplicates_rounded_values() -> None:
    values = axis_values(_integer(), 4.0, 5.0, 6)

    assert values == (4.0, 5.0)


def test_axis_values_are_clamped_to_variable_bounds() -> None:
    values = axis_values(_continuous(), 0.0, 100.0, 3)

    assert values == (8.0, 10.0, 12.0)


def test_choice_axis_uses_discrete_values() -> None:
    variable = OptimizationVariable(
        "ratio",
        "component_calculator.turns_ratio",
        "optimize.group.loads",
        1.0,
        16.0,
        kind=VariableKind.CHOICE,
        unit="ratio",
        choices=(1.0, 4.0, 9.0, 16.0),
    )

    assert axis_values(variable, 2.0, 16.0, 10) == (4.0, 9.0, 16.0)


def test_axis_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="increasing"):
        SweepAxis("a", "field.length", "m", (10.0, 9.0))
    with pytest.raises(ValueError, match="finite"):
        SweepAxis("a", "field.length", "m", (1.0, float("inf")))


def test_plan_budget_and_duplicate_axis_validation() -> None:
    plan = SweepPlan(
        x_axis=_axis(),
        y_axis=_axis("height_m", (8.0, 9.0)),
        metric=SweepMetric.SWR,
        target_frequency_hz=7_100_000.0,
    )

    assert plan.point_count == 6
    assert plan.is_two_dimensional is True
    with pytest.raises(ValueError, match="different variables"):
        SweepPlan(
            x_axis=_axis(),
            y_axis=_axis(),
            metric=SweepMetric.SWR,
            target_frequency_hz=7_100_000.0,
        )


def test_plan_rejects_more_than_the_budget() -> None:
    too_many = tuple(float(value) for value in range(MAX_SWEEP_POINTS))

    with pytest.raises(ValueError, match="at most"):
        SweepPlan(
            x_axis=_axis(values=too_many),
            y_axis=_axis("height_m", (8.0, 9.0)),
            metric=SweepMetric.SWR,
            target_frequency_hz=7_100_000.0,
        )


def test_best_swr_point_uses_only_valid_finite_points() -> None:
    plan = SweepPlan(
        x_axis=_axis(),
        y_axis=None,
        metric=SweepMetric.SWR,
        target_frequency_hz=7_100_000.0,
    )
    result = ParameterSweepResult(
        plan=plan,
        points=(
            SweepPoint(9.0, swr=2.0, resistance_ohm=50.0),
            SweepPoint(10.0, swr=1.2, resistance_ohm=50.0),
            SweepPoint(11.0, error="invalid"),
        ),
    )

    best = result.best_swr_point

    assert best is not None
    assert best.x_value == 10.0
    assert result.valid_count == 2


def test_metric_returns_the_requested_value() -> None:
    point = SweepPoint(
        x_value=10.0,
        swr=1.5,
        resistance_ohm=50.0,
        reactance_ohm=-10.0,
        impedance_magnitude_ohm=51.0,
    )

    assert point.metric(SweepMetric.SWR) == pytest.approx(1.5)
    assert point.metric(SweepMetric.RESISTANCE) == pytest.approx(50.0)
    assert point.metric(SweepMetric.REACTANCE) == pytest.approx(-10.0)
    assert point.metric(SweepMetric.IMPEDANCE_MAGNITUDE) == pytest.approx(51.0)
