# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded design variables shared by every family optimizer."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, replace
from enum import StrEnum


class VariableKind(StrEnum):
    CONTINUOUS = "continuous"
    INTEGER = "integer"
    CHOICE = "choice"


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
