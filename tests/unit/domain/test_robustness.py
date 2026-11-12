# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Corner-case and Monte Carlo robustness models."""

from __future__ import annotations

import pytest

from antennadesk.domain.design.robustness import (
    RobustnessResult,
    RobustnessScenario,
    RobustnessScenarioKind,
    RobustnessSpec,
    corner_value_sets,
    monte_carlo_value_sets,
    robustness_variables,
)
from antennadesk.domain.optimization.variables import OptimizationVariable, VariableKind


def _length(name: str = "length_m", value: float = 10.0) -> OptimizationVariable:
    return OptimizationVariable(
        name,
        "field.length",
        "optimize.group.geometry",
        value * 0.8,
        value * 1.2,
        step=0.01,
    )


def _height() -> OptimizationVariable:
    return OptimizationVariable(
        "height_m",
        "field.height",
        "optimize.group.geometry",
        6.0,
        10.0,
        step=0.01,
    )


def _spec(**overrides: object) -> RobustnessSpec:
    values: dict[str, object] = {
        "target_frequency_hz": 7_100_000.0,
        "tolerance": 0.02,
        "variable_names": ("length_m",),
        "include_corners": True,
        "monte_carlo_samples": 10,
        "seed": 0,
        "swr_limit": 2.0,
    }
    values.update(overrides)
    return RobustnessSpec(**values)  # type: ignore[arg-type]


def test_spec_budget_and_validation() -> None:
    spec = _spec(variable_names=("length_m", "height_m"))

    assert spec.corner_count == 4
    assert spec.total_runs == 15
    with pytest.raises(ValueError, match="tolerance"):
        _spec(tolerance=0.0)
    with pytest.raises(ValueError, match="critical dimensions"):
        _spec(variable_names=tuple(f"v{index}" for index in range(6)))
    with pytest.raises(ValueError, match="between 0 and 200"):
        _spec(monte_carlo_samples=201)


def test_corner_sets_cover_all_sign_combinations() -> None:
    variables = (_length(), _height())
    base = {"length_m": 10.0, "height_m": 8.0}

    values = corner_value_sets(base, variables, 0.1)

    assert len(values) == 4
    assert {(round(item["length_m"], 6), round(item["height_m"], 6)) for item in values} == {
        (9.0, 7.2),
        (9.0, 8.8),
        (11.0, 7.2),
        (11.0, 8.8),
    }
    assert base == {"length_m": 10.0, "height_m": 8.0}


def test_corner_sets_clamp_to_variable_bounds() -> None:
    variable = OptimizationVariable(
        "length_m",
        "field.length",
        "optimize.group.geometry",
        10.0,
        12.0,
        step=0.01,
    )
    base = {"length_m": 10.0}

    values = corner_value_sets(base, (variable,), 0.1)

    assert {item["length_m"] for item in values} == {10.0, 11.0}


def test_monte_carlo_is_seeded_and_bounded() -> None:
    variables = (_length(), _height())
    base = {"length_m": 10.0, "height_m": 8.0}

    first = monte_carlo_value_sets(base, variables, 0.05, 8, 42)
    second = monte_carlo_value_sets(base, variables, 0.05, 8, 42)
    other = monte_carlo_value_sets(base, variables, 0.05, 8, 43)

    assert first == second
    assert first != other
    assert len(first) == 8
    for values in first:
        assert 9.5 <= values["length_m"] <= 10.5
        assert 7.6 <= values["height_m"] <= 8.4


def _scenario(kind: RobustnessScenarioKind, swr: float) -> RobustnessScenario:
    return RobustnessScenario(
        kind=kind,
        values=(("length_m", 10.0),),
        swr=swr,
        resistance_ohm=50.0,
    )


def test_result_statistics_worst_corner_and_histogram() -> None:
    spec = _spec()
    result = RobustnessResult(
        spec=spec,
        scenarios=(
            _scenario(RobustnessScenarioKind.NOMINAL, 1.1),
            _scenario(RobustnessScenarioKind.CORNER, 1.8),
            _scenario(RobustnessScenarioKind.CORNER, 2.4),
            _scenario(RobustnessScenarioKind.MONTE_CARLO, 1.2),
            _scenario(RobustnessScenarioKind.MONTE_CARLO, 1.6),
            _scenario(RobustnessScenarioKind.MONTE_CARLO, 2.2),
        ),
    )

    assert result.nominal is not None
    assert result.nominal.swr == pytest.approx(1.1)
    assert result.worst_corner is not None
    assert result.worst_corner.swr == pytest.approx(2.4)
    stats = result.statistics
    assert stats.count == 3
    assert stats.median_swr == pytest.approx(1.6)
    assert stats.p90_swr == pytest.approx(2.2)
    assert stats.passed == 2
    assert stats.pass_fraction == pytest.approx(2 / 3)
    assert sum(item.count for item in result.histogram) == 3


def test_robustness_variables_resolve_only_length_and_radius() -> None:
    continuous = _length()
    integer = OptimizationVariable(
        "count",
        "vertical.radial_count",
        "optimize.group.loads",
        1.0,
        10.0,
        kind=VariableKind.INTEGER,
        unit="count",
    )

    assert robustness_variables((continuous, integer), ("length_m",)) == (continuous,)
    with pytest.raises(ValueError, match="continuous"):
        robustness_variables((continuous, integer), ("count",))
    with pytest.raises(ValueError, match="unknown"):
        robustness_variables((continuous,), ("missing",))
