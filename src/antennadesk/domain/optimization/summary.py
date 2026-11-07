# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compact, reproducible records of completed optimizer runs."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from ..common.time import ensure_utc
from ..common.units import ensure_non_negative

OPTIMIZATION_SUMMARY_METHOD = "family_hybrid"
OPTIMIZATION_SUMMARY_VERSION = 1


class OptimizationMode(StrEnum):
    """How many operating points and tolerance scenarios a run evaluates."""

    SINGLE = "single"
    BAND_AWARE = "band_aware"
    ROBUST = "robust"


class RecommendationSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class OptimizationRecommendation:
    """One deterministic, translatable post-run recommendation."""

    key: str
    severity: RecommendationSeverity = RecommendationSeverity.INFO
    variables: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("recommendation key must not be empty")
        object.__setattr__(self, "severity", RecommendationSeverity(self.severity))
        object.__setattr__(self, "variables", tuple(self.variables))


def _finite_mapping(values: Mapping[str, float], name: str) -> dict[str, float]:
    result = {str(key): float(value) for key, value in values.items()}
    for key, value in result.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} value for {key!r} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class OptimizationSummary:
    """The persisted summary of one optimization run.

    The full evaluation log is intentionally not stored. This record keeps the
    configuration and the winning vector so a user can reproduce or audit the
    run without inflating the project file.
    """

    mode: OptimizationMode
    objective: str
    status: str
    budget_profile: str
    evaluations: int
    seed: int
    best_values: Mapping[str, float]
    best_metrics: Mapping[str, float]
    completed_at: datetime
    method: str = OPTIMIZATION_SUMMARY_METHOD
    version: int = OPTIMIZATION_SUMMARY_VERSION
    band_edges_hz: tuple[float, ...] = ()
    tolerance: float = 0.0
    weights: Mapping[str, float] = field(default_factory=dict)
    constraints: tuple[str, ...] = ()
    recommendations: tuple[OptimizationRecommendation, ...] = ()

    def __post_init__(self) -> None:
        if not self.method.strip():
            raise ValueError("summary method must not be empty")
        if self.version < 1:
            raise ValueError("summary version must be positive")
        if not self.objective.strip():
            raise ValueError("summary objective must not be empty")
        if not self.status.strip():
            raise ValueError("summary status must not be empty")
        if not self.budget_profile.strip():
            raise ValueError("summary budget profile must not be empty")
        ensure_non_negative(self.evaluations, name="summary_evaluations")
        ensure_non_negative(self.seed, name="summary_seed")
        ensure_non_negative(self.tolerance, name="summary_tolerance")
        if self.tolerance >= 1.0:
            raise ValueError("summary tolerance must be smaller than 1")
        ensure_utc(self.completed_at, name="summary_completed_at")
        object.__setattr__(self, "mode", OptimizationMode(self.mode))
        edges = tuple(float(frequency) for frequency in self.band_edges_hz)
        for frequency in edges:
            if not math.isfinite(frequency) or frequency <= 0.0:
                raise ValueError("summary band edges must be positive and finite")
        object.__setattr__(self, "band_edges_hz", tuple(sorted(set(edges))))
        object.__setattr__(
            self,
            "best_values",
            _finite_mapping(self.best_values, "best_values"),
        )
        object.__setattr__(
            self,
            "best_metrics",
            _finite_mapping(self.best_metrics, "best_metrics"),
        )
        object.__setattr__(
            self,
            "weights",
            _finite_mapping(self.weights, "weights"),
        )
        object.__setattr__(self, "constraints", tuple(self.constraints))
        object.__setattr__(self, "recommendations", tuple(self.recommendations))
