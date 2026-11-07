# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Family optimizer descriptor and objective model."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from ..antennas.design import AntennaDesignParameters
from ..common.units import ensure_non_negative
from .constraints import ConstraintViolation
from .variables import OptimizationVariable


class FamilyOptimizationObjective(StrEnum):
    TARGET_IMPEDANCE = "target_impedance"
    MIN_SWR = "min_swr"
    MAX_GAIN = "max_gain"
    MAX_FRONT_TO_BACK = "max_front_to_back"
    MAX_EFFICIENCY = "max_efficiency"
    MAX_BANDWIDTH = "max_bandwidth"
    MULTI_OBJECTIVE = "multi_objective"


@dataclass(frozen=True, slots=True)
class OptimizationWeights:
    gain: float = 1.0
    front_to_back: float = 1.0
    swr: float = 1.0
    efficiency: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("gain", self.gain),
            ("front_to_back", self.front_to_back),
            ("swr", self.swr),
            ("efficiency", self.efficiency),
        ):
            ensure_non_negative(value, name=f"weight_{name}")
        if (
            self.gain == 0.0
            and self.front_to_back == 0.0
            and self.swr == 0.0
            and self.efficiency == 0.0
        ):
            raise ValueError("at least one multi-objective weight must be positive")


ParameterBuilder = Callable[[Mapping[str, float]], AntennaDesignParameters]
ParameterValidator = Callable[[Mapping[str, float]], tuple[ConstraintViolation, ...]]


@dataclass(frozen=True, slots=True)
class AntennaOptimizerDescriptor:
    """The complete optimizer contract for one family or generator variant."""

    key: str
    variables: tuple[OptimizationVariable, ...]
    initial_values: Mapping[str, float]
    build_parameters: ParameterBuilder
    validate: ParameterValidator
    objectives: frozenset[FamilyOptimizationObjective]
    default_objective: FamilyOptimizationObjective = FamilyOptimizationObjective.TARGET_IMPEDANCE
    start_points: tuple[Mapping[str, float], ...] = field(default_factory=tuple)
    supports_band_aware: bool = False
    supports_robust: bool = False

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("optimizer key must not be empty")
        if not self.variables:
            raise ValueError("an optimizer requires at least one variable")
        names = [variable.name for variable in self.variables]
        if len(names) != len(set(names)):
            raise ValueError("optimizer variable names must be unique")
        if set(self.initial_values) != set(names):
            raise ValueError("initial values must cover every optimizer variable")
        if self.default_objective not in self.objectives:
            raise ValueError("default objective must be supported")
        for point in self.start_points:
            if set(point) != set(names):
                raise ValueError("each start point must cover every variable")
