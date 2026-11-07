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
    """Return a practical search interval around the current value."""

    low = max(minimum, value * (1.0 - fraction))
    high = value * (1.0 + fraction)
    if maximum is not None:
        high = min(maximum, high)
    if high <= low:
        high = low + max(abs(value) * 0.01, 1e-3)
    return low, high


def radius_around(value: float) -> tuple[float, float]:
    return around(value, 0.5, minimum=1e-4, maximum=0.02)


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
