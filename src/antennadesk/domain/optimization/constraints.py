# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Hard and soft constraints for family optimizers."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum


class ConstraintSeverity(StrEnum):
    HARD = "hard"
    SOFT = "soft"


class OptimizationMetric(StrEnum):
    SWR = "swr"
    TARGET_ERROR_OHM = "target_error_ohm"
    GAIN_DB = "max_gain_db"
    FRONT_TO_BACK_DB = "front_to_back_db"
    EFFICIENCY_PERCENT = "efficiency_percent"
    BANDWIDTH_HZ = "bandwidth_hz"


@dataclass(frozen=True, slots=True)
class ConstraintViolation:
    """A hard feasibility violation returned by a family validator."""

    name: str
    amount: float
    message_key: str
    severity: ConstraintSeverity = ConstraintSeverity.HARD

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.message_key.strip():
            raise ValueError("constraint name and message key must not be empty")
        if not math.isfinite(self.amount) or self.amount < 0.0:
            raise ValueError("constraint amount must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class SoftConstraint:
    """A preference penalty applied after a successful simulation."""

    metric: OptimizationMetric
    minimum: float | None = None
    maximum: float | None = None
    weight: float = 1.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "metric", OptimizationMetric(self.metric))
        if self.minimum is None and self.maximum is None:
            raise ValueError("a soft constraint requires a minimum or maximum")
        if self.minimum is not None and self.maximum is not None and self.maximum < self.minimum:
            raise ValueError("soft constraint maximum must not be below its minimum")
        if not math.isfinite(self.weight) or self.weight < 0.0:
            raise ValueError("soft constraint weight must be finite and non-negative")

    def normalized_violation(self, metrics: dict[str, float]) -> float:
        value = metrics.get(self.metric.value)
        if value is None or not math.isfinite(value):
            return 1.0
        violation = 0.0
        if self.minimum is not None and value < self.minimum:
            scale = max(abs(self.minimum), 1e-9)
            violation = max(violation, (self.minimum - value) / scale)
        if self.maximum is not None and value > self.maximum:
            scale = max(abs(self.maximum), 1e-9)
            violation = max(violation, (value - self.maximum) / scale)
        return violation * self.weight
