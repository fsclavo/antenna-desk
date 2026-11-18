# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared bounds and validation helpers for family descriptors."""

from __future__ import annotations

import math

from ..constraints import ConstraintViolation
from ..descriptor import FamilyOptimizationObjective

COMMON_OBJECTIVES = frozenset(
    {
        FamilyOptimizationObjective.TARGET_IMPEDANCE,
        FamilyOptimizationObjective.MIN_SWR,
        FamilyOptimizationObjective.MIN_SWR_OPERATING,
        FamilyOptimizationObjective.MAX_GAIN,
        FamilyOptimizationObjective.MAX_FRONT_TO_BACK,
        FamilyOptimizationObjective.MAX_EFFICIENCY,
        FamilyOptimizationObjective.MAX_BANDWIDTH,
        FamilyOptimizationObjective.MULTI_OBJECTIVE,
    }
)


def around(
    value: float,
    fraction: float,
    *,
    minimum: float = 0.0,
    maximum: float | None = None,
) -> tuple[float, float]:
    """Return a search interval relative to the current value.

    The current value carries the family's frequency scaling, so a fixed
    metre floor must not move a valid VHF/UHF design. ``minimum`` is reserved
    for a genuine physical or numerical floor; if the current value is below
    it, the descriptor invariant reports the design as unsupported instead of
    clamping the search to a different antenna.
    """

    low = max(minimum, value * (1.0 - fraction))
    high = value * (1.0 + fraction)
    if maximum is not None:
        high = min(maximum, high)
    if high <= low:
        high = low + max(abs(value) * 0.01, 1e-3)
    return low, high


def radius_around(value: float) -> tuple[float, float]:
    return around(value, 0.5, minimum=1e-4, maximum=0.02)


def conductor_floor_m(wire_radius_m: float, *, factor: float = 2.0) -> float:
    """Return a positive conductor-clearance floor for a gap or spacing.

    The 1 µm term is a numerical floor, not a construction reference. The
    ``factor`` is the number of radii the gap must clear; the default is one
    conductor diameter.
    """

    return max(factor * abs(wire_radius_m) + 1e-9, 1e-6)


def relative_step(low: float, high: float) -> float:
    """Return a numerical step scaled to the search span.

    A fixed 10 mm step is meaningless for a 20 mm UHF element and unnecessarily
    fine for a 20 m dipole. The local search uses the same span-normalized step
    that the optimizer table displays.
    """

    return max((high - low) / 100.0, 1e-6)


def violation(name: str, amount: float, message_key: str) -> ConstraintViolation:
    return ConstraintViolation(
        name=name,
        amount=max(amount, 0.0),
        message_key=message_key,
    )


def positive_violation(name: str, value: float) -> ConstraintViolation | None:
    if not math.isfinite(value) or value <= 0.0:
        return violation(name, 1.0, "optimize.constraint.positive")
    return None


def non_negative_violation(name: str, value: float) -> ConstraintViolation | None:
    if not math.isfinite(value) or value < 0.0:
        return violation(name, 1.0, "optimize.constraint.non_negative")
    return None


def collect(
    *violations: ConstraintViolation | None,
) -> tuple[ConstraintViolation, ...]:
    return tuple(item for item in violations if item is not None)
