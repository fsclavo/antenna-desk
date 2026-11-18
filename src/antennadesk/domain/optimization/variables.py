# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded design variables shared by every family optimizer."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from enum import StrEnum


class VariableKind(StrEnum):
    CONTINUOUS = "continuous"
    INTEGER = "integer"
    CHOICE = "choice"


class BoundIssueKind(StrEnum):
    """Why an initial value cannot anchor a bounded optimizer run."""

    OUTSIDE = "outside"
    NON_FINITE = "non_finite"
    DEGENERATE_SPAN = "degenerate_span"
    UNREPRESENTABLE = "unrepresentable"


@dataclass(frozen=True, slots=True)
class VariableBoundIssue:
    """One variable whose current value violates the descriptor invariant."""

    variable: str
    value: float
    minimum: float
    maximum: float
    kind: BoundIssueKind

    @property
    def reason_key(self) -> str:
        return f"optimize.unavailable.bounds.{self.kind.value}"

    def reason_values(self, family: str) -> dict[str, object]:
        return {
            "family": family,
            "variable": self.variable,
            "value": self.value,
            "minimum": self.minimum,
            "maximum": self.maximum,
        }

    def describe(self, family: str) -> str:
        bounds = f"[{self.minimum:.6g}, {self.maximum:.6g}]"
        if self.kind is BoundIssueKind.NON_FINITE:
            return f"{family}.{self.variable} has a non-finite initial value; bounds {bounds}"
        if self.kind is BoundIssueKind.DEGENERATE_SPAN:
            return (
                f"{family}.{self.variable} has a degenerate search span around "
                f"{self.value:.6g}; bounds {bounds}"
            )
        if self.kind is BoundIssueKind.UNREPRESENTABLE:
            return (
                f"{family}.{self.variable}={self.value:.6g} is not representable; bounds {bounds}"
            )
        return f"{family}.{self.variable}={self.value:.6g} is outside its search bounds {bounds}"


@dataclass(frozen=True, slots=True)
class OptimizationVariable:
    """One bounded variable in a family design vector.

    ``unit`` is a presentation hint: ``m`` for a length, ``deg`` for an angle,
    ``count`` for a dimensionless count, and ``radius`` for a conductor radius.
    """

    name: str
    label_key: str
    group: str
    minimum: float
    maximum: float
    kind: VariableKind = VariableKind.CONTINUOUS
    unit: str = "m"
    step: float = 0.001
    choices: tuple[float, ...] = ()
    locked_by_default: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("variable name must not be empty")
        if not self.label_key.strip() or not self.group.strip():
            raise ValueError("variable labels and groups must not be empty")
        if not math.isfinite(self.minimum) or not math.isfinite(self.maximum):
            raise ValueError("variable bounds must be finite")
        if self.maximum <= self.minimum:
            raise ValueError("variable maximum must exceed minimum")
        if self.step <= 0.0:
            raise ValueError("variable step must be positive")
        object.__setattr__(self, "kind", VariableKind(self.kind))
        if self.kind is VariableKind.CHOICE:
            if not self.choices:
                raise ValueError("choice variables require at least one choice")
            choices = tuple(sorted(float(choice) for choice in self.choices))
            object.__setattr__(self, "choices", choices)
            if choices[0] < self.minimum or choices[-1] > self.maximum:
                raise ValueError("choice values must lie inside the variable bounds")
        elif self.choices:
            raise ValueError("only choice variables may define choices")

    def clamp(self, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError(f"variable {self.name!r} must be finite")
        clipped = min(max(value, self.minimum), self.maximum)
        if self.kind is VariableKind.INTEGER:
            return float(round(clipped))
        if self.kind is VariableKind.CHOICE:
            return min(self.choices, key=lambda choice: abs(choice - clipped))
        return clipped

    def from_fraction(self, fraction: float) -> float:
        fraction = min(max(fraction, 0.0), 1.0)
        if self.kind is VariableKind.CHOICE:
            index = min(int(fraction * len(self.choices)), len(self.choices) - 1)
            return self.choices[index]
        value = self.minimum + fraction * (self.maximum - self.minimum)
        return self.clamp(value)

    def to_fraction(self, value: float) -> float:
        value = self.clamp(value)
        if self.kind is VariableKind.CHOICE:
            index = self.choices.index(value)
            return index / max(len(self.choices) - 1, 1)
        span = self.maximum - self.minimum
        return 0.0 if span <= 0.0 else (value - self.minimum) / span

    def next_value(self, value: float, direction: int) -> float:
        """Return the adjacent integer/choice value, or a step for continuous."""

        if self.kind is VariableKind.INTEGER:
            return self.clamp(round(value) + (1 if direction > 0 else -1))
        if self.kind is VariableKind.CHOICE:
            index = self.choices.index(self.clamp(value))
            return self.choices[
                min(max(index + (1 if direction > 0 else -1), 0), len(self.choices) - 1)
            ]
        return self.clamp(value + direction * self.step)


def variable_bound_issue(
    variable: OptimizationVariable,
    value: float,
) -> VariableBoundIssue | None:
    """Return the invariant violation for one initial value, if any.

    The span rule follows ADR-0046: a length search interval must be at least
    1 µm or 0.1 % of the value scale, whichever is larger. Non-length units use
    the same relative rule with a smaller numerical floor. It is a numerical
    non-degeneracy rule, not a physical construction reference.
    """

    if not math.isfinite(value):
        return VariableBoundIssue(
            variable=variable.name,
            value=value,
            minimum=variable.minimum,
            maximum=variable.maximum,
            kind=BoundIssueKind.NON_FINITE,
        )
    if value < variable.minimum or value > variable.maximum:
        return VariableBoundIssue(
            variable=variable.name,
            value=value,
            minimum=variable.minimum,
            maximum=variable.maximum,
            kind=BoundIssueKind.OUTSIDE,
        )
    span = variable.maximum - variable.minimum
    # ADR-0046 states the absolute floor in metres. Other units (F, H, ratios,
    # angles, counts) use the same relative rule with a smaller numerical floor.
    numerical_floor = 1e-6 if variable.unit in {"m", "radius"} else 1e-12
    scale = max(abs(value), numerical_floor)
    if span < max(numerical_floor, 0.001 * scale):
        return VariableBoundIssue(
            variable=variable.name,
            value=value,
            minimum=variable.minimum,
            maximum=variable.maximum,
            kind=BoundIssueKind.DEGENERATE_SPAN,
        )
    if variable.kind is VariableKind.INTEGER and not math.isclose(value, round(value)):
        return VariableBoundIssue(
            variable=variable.name,
            value=value,
            minimum=variable.minimum,
            maximum=variable.maximum,
            kind=BoundIssueKind.UNREPRESENTABLE,
        )
    if variable.kind is VariableKind.CHOICE and not any(
        math.isclose(value, choice) for choice in variable.choices
    ):
        return VariableBoundIssue(
            variable=variable.name,
            value=value,
            minimum=variable.minimum,
            maximum=variable.maximum,
            kind=BoundIssueKind.UNREPRESENTABLE,
        )
    return None


def variables_at_bounds(
    variables: Sequence[OptimizationVariable],
    values: Mapping[str, float],
    *,
    locked: frozenset[str] = frozenset(),
    fraction: float = 0.01,
) -> tuple[str, ...]:
    """Return continuous, unlocked variables within ``fraction`` of a bound."""

    if not math.isfinite(fraction) or fraction < 0.0 or fraction >= 0.5:
        raise ValueError("bound fraction must be finite and between 0 and 0.5")
    hits: list[str] = []
    for variable in variables:
        if variable.kind is not VariableKind.CONTINUOUS or variable.name in locked:
            continue
        value = values.get(variable.name)
        if value is None or not math.isfinite(value):
            continue
        margin = (variable.maximum - variable.minimum) * fraction
        if value <= variable.minimum + margin or value >= variable.maximum - margin:
            hits.append(variable.name)
    return tuple(hits)


# Installation context, feed placement, and conductor radius are editable but
# unchecked by default: they are not the dimensions users typically retune.
# ``height_m`` is installation height for most families, but it is the radiator
# length for verticals and phased verticals, so those keys are exempt.
DEFAULT_LOCKED_VARIABLES = frozenset(
    {
        "wire_radius_m",
        "transformer_ratio",
        "feed_ratio",
        "feed_offset_m",
        "feed_height_m",
        "end_height_m",
        "counterpoise_height_m",
        "apex_height_m",
        "base_height_m",
        "ring_height_m",
    }
)
RADIATOR_HEIGHT_KEYS = frozenset({"vertical", "phased_vertical"})


def apply_default_locks(
    key: str,
    variables: Sequence[OptimizationVariable],
) -> tuple[OptimizationVariable, ...]:
    """Return variables with the default search scope applied."""

    locked_names = set(DEFAULT_LOCKED_VARIABLES)
    if key not in RADIATOR_HEIGHT_KEYS:
        locked_names.add("height_m")
    return tuple(
        replace(variable, locked_by_default=True) if variable.name in locked_names else variable
        for variable in variables
    )
