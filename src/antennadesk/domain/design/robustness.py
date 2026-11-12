# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded tolerance and robustness scenarios for critical dimensions.

The analysis perturbs selected continuous length/radius variables by a single
user-specified fractional tolerance. It evaluates corner cases and a seeded
uniform Monte Carlo sample. It does not assume a physical distribution,
correlate dimensions, or claim a calibrated manufacturing tolerance.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import StrEnum

from ..optimization.variables import OptimizationVariable, VariableKind

MAX_ROBUSTNESS_RUNS = 300
MAX_CORNER_DIMENSIONS = 5
DEFAULT_MONTE_CARLO_SAMPLES = 30
ROBUSTNESS_DIMENSION_UNITS = frozenset({"m", "radius"})


class RobustnessScenarioKind(StrEnum):
    NOMINAL = "nominal"
    CORNER = "corner"
    MONTE_CARLO = "monte_carlo"


@dataclass(frozen=True, slots=True)
class RobustnessSpec:
    target_frequency_hz: float
    tolerance: float
    variable_names: tuple[str, ...]
    include_corners: bool = True
    monte_carlo_samples: int = DEFAULT_MONTE_CARLO_SAMPLES
    seed: int = 0
    swr_limit: float = 2.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.target_frequency_hz) or self.target_frequency_hz <= 0.0:
            raise ValueError("target_frequency_hz must be positive and finite")
        if not math.isfinite(self.tolerance) or not 0.0 < self.tolerance <= 0.5:
            raise ValueError("tolerance must be between 0 and 0.5")
        names = tuple(self.variable_names)
        if not names or any(not name.strip() for name in names):
            raise ValueError("at least one non-empty variable name is required")
        if len(names) != len(set(names)):
            raise ValueError("robustness variable names must be unique")
        if len(names) > MAX_CORNER_DIMENSIONS:
            raise ValueError(f"at most {MAX_CORNER_DIMENSIONS} critical dimensions are supported")
        if not 0 <= self.monte_carlo_samples <= 200:
            raise ValueError("monte_carlo_samples must be between 0 and 200")
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        if not math.isfinite(self.swr_limit) or self.swr_limit <= 1.0:
            raise ValueError("swr_limit must be greater than 1")
        if self.include_corners and self.corner_count > 2**MAX_CORNER_DIMENSIONS:
            raise ValueError("too many corner combinations")
        if self.total_runs > MAX_ROBUSTNESS_RUNS:
            raise ValueError(
                f"a robustness analysis may contain at most {MAX_ROBUSTNESS_RUNS} runs"
            )

    @property
    def corner_count(self) -> int:
        return 2 ** len(self.variable_names) if self.include_corners else 0

    @property
    def total_runs(self) -> int:
        return 1 + self.corner_count + self.monte_carlo_samples


@dataclass(frozen=True, slots=True)
class RobustnessScenario:
    kind: RobustnessScenarioKind
    values: tuple[tuple[str, float], ...]
    swr: float | None = None
    resistance_ohm: float | None = None
    reactance_ohm: float | None = None
    impedance_magnitude_ohm: float | None = None
    error: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", RobustnessScenarioKind(self.kind))
        object.__setattr__(
            self,
            "values",
            tuple((str(name), float(value)) for name, value in self.values),
        )

    @property
    def valid(self) -> bool:
        return not self.error and self.swr is not None

    def value_map(self) -> dict[str, float]:
        return dict(self.values)


@dataclass(frozen=True, slots=True)
class HistogramBin:
    left: float
    right: float
    count: int


@dataclass(frozen=True, slots=True)
class MonteCarloStatistics:
    count: int
    mean_swr: float | None
    median_swr: float | None
    p90_swr: float | None
    p95_swr: float | None
    min_swr: float | None
    max_swr: float | None
    passed: int
    pass_fraction: float | None


@dataclass(frozen=True, slots=True)
class RobustnessResult:
    spec: RobustnessSpec
    scenarios: tuple[RobustnessScenario, ...]
    cancelled: bool = False
    message: str = ""

    @property
    def nominal(self) -> RobustnessScenario | None:
        return next(
            (
                scenario
                for scenario in self.scenarios
                if scenario.kind is RobustnessScenarioKind.NOMINAL
            ),
            None,
        )

    @property
    def corners(self) -> tuple[RobustnessScenario, ...]:
        return tuple(
            scenario
            for scenario in self.scenarios
            if scenario.kind is RobustnessScenarioKind.CORNER
        )

    @property
    def monte_carlo(self) -> tuple[RobustnessScenario, ...]:
        return tuple(
            scenario
            for scenario in self.scenarios
            if scenario.kind is RobustnessScenarioKind.MONTE_CARLO
        )

    @property
    def worst_corner(self) -> RobustnessScenario | None:
        valid = [
            scenario for scenario in self.corners if scenario.valid and scenario.swr is not None
        ]
        if not valid:
            return None
        return max(
            valid,
            key=lambda scenario: scenario.swr if scenario.swr is not None else -math.inf,
        )

    @property
    def statistics(self) -> MonteCarloStatistics:
        values = [
            scenario.swr
            for scenario in self.monte_carlo
            if scenario.valid and scenario.swr is not None and math.isfinite(scenario.swr)
        ]
        ordered = sorted(value for value in values if value is not None)
        if not ordered:
            return MonteCarloStatistics(0, None, None, None, None, None, None, 0, None)
        passed = sum(1 for value in ordered if value <= self.spec.swr_limit)
        return MonteCarloStatistics(
            count=len(ordered),
            mean_swr=sum(ordered) / len(ordered),
            median_swr=_percentile(ordered, 0.5),
            p90_swr=_percentile(ordered, 0.9),
            p95_swr=_percentile(ordered, 0.95),
            min_swr=ordered[0],
            max_swr=ordered[-1],
            passed=passed,
            pass_fraction=passed / len(ordered),
        )

    @property
    def histogram(self) -> tuple[HistogramBin, ...]:
        values = [
            scenario.swr
            for scenario in self.monte_carlo
            if scenario.valid and scenario.swr is not None and math.isfinite(scenario.swr)
        ]
        valid = [value for value in values if value is not None]
        if not valid:
            return ()
        low = min(valid)
        high = max(valid)
        if math.isclose(low, high, rel_tol=0.0, abs_tol=1e-12):
            return (HistogramBin(low, high, len(valid)),)
        bin_count = min(12, max(4, round(math.sqrt(len(valid)))))
        width = (high - low) / bin_count
        counts = [0] * bin_count
        for value in valid:
            index = min(int((value - low) / width), bin_count - 1)
            counts[index] += 1
        return tuple(
            HistogramBin(low + index * width, low + (index + 1) * width, count)
            for index, count in enumerate(counts)
        )


def _percentile(ordered: list[float], fraction: float) -> float:
    if not ordered:
        raise ValueError("percentile requires at least one value")
    index = math.ceil(fraction * len(ordered)) - 1
    return ordered[min(max(index, 0), len(ordered) - 1)]


def _perturbed_value(
    variable: OptimizationVariable,
    value: float,
    factor: float,
) -> float:
    return variable.clamp(value * (1.0 + factor))


def corner_value_sets(
    base_values: dict[str, float],
    variables: tuple[OptimizationVariable, ...],
    tolerance: float,
) -> tuple[dict[str, float], ...]:
    """Return unique sign combinations for the selected dimensions."""

    if not variables:
        return ()
    scenarios: dict[tuple[float, ...], dict[str, float]] = {}
    for signs in _sign_combinations(len(variables)):
        values = dict(base_values)
        for variable, sign in zip(variables, signs, strict=True):
            values[variable.name] = _perturbed_value(
                variable,
                base_values[variable.name],
                sign * tolerance,
            )
        key = tuple(round(values[variable.name], 12) for variable in variables)
        scenarios.setdefault(key, values)
    return tuple(scenarios.values())


def _sign_combinations(count: int) -> tuple[tuple[int, ...], ...]:
    combinations: list[tuple[int, ...]] = [()]
    for _ in range(count):
        combinations = [(*prefix, sign) for prefix in combinations for sign in (-1, 1)]
    return tuple(combinations)


def monte_carlo_value_sets(
    base_values: dict[str, float],
    variables: tuple[OptimizationVariable, ...],
    tolerance: float,
    count: int,
    seed: int,
) -> tuple[dict[str, float], ...]:
    """Return a deterministic uniform multiplicative Monte Carlo sample."""

    if count < 0:
        raise ValueError("count must be non-negative")
    if count == 0 or not variables:
        return ()
    rng = random.Random(seed)  # noqa: S311 — deterministic analysis, not cryptography
    samples: list[dict[str, float]] = []
    for _ in range(count):
        values = dict(base_values)
        for variable in variables:
            factor = rng.uniform(-tolerance, tolerance)
            values[variable.name] = _perturbed_value(
                variable,
                base_values[variable.name],
                factor,
            )
        samples.append(values)
    return tuple(samples)


def robustness_variables(
    variables: tuple[OptimizationVariable, ...],
    names: tuple[str, ...],
) -> tuple[OptimizationVariable, ...]:
    """Resolve selected names to continuous length/radius variables."""

    by_name = {variable.name: variable for variable in variables}
    resolved: list[OptimizationVariable] = []
    for name in names:
        variable = by_name.get(name)
        if variable is None:
            raise ValueError(f"unknown robustness variable: {name}")
        if variable.kind is not VariableKind.CONTINUOUS:
            raise ValueError(f"robustness variable {name} must be continuous")
        if variable.unit not in ROBUSTNESS_DIMENSION_UNITS:
            raise ValueError(f"robustness variable {name} must be a length or radius")
        resolved.append(variable)
    return tuple(resolved)
