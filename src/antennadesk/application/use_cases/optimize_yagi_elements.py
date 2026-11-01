# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimize selected Yagi element lengths and gaps."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum

from ...domain.antennas.yagi import YagiParameters
from ...domain.optimization.multi_variable import BoundedResult, BoundedVariable
from ...domain.optimization.synthesis import SynthesisTarget
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .optimize_elements import (
    ElementOptimizationObjective,
    OptimizeElements,
    OptimizeElementsCommand,
)

BuildYagiParameters = Callable[[Mapping[str, float]], YagiParameters]


class YagiOptimizationObjective(StrEnum):
    TARGET_IMPEDANCE = "target_impedance"
    MAX_GAIN = "max_gain"
    MAX_FRONT_TO_BACK = "max_front_to_back"


@dataclass(frozen=True, slots=True)
class OptimizeYagiElementsCommand:
    build_parameters: BuildYagiParameters
    variables: tuple[BoundedVariable, ...]
    start_values: Mapping[str, float]
    target: SynthesisTarget
    base_spec: SimulationSpec
    objective: YagiOptimizationObjective = YagiOptimizationObjective.TARGET_IMPEDANCE
    max_evaluations: int = 81
    samples: int = 5
    passes: int = 4
    cancel_token: CancelToken | None = None


@dataclass(frozen=True, slots=True)
class OptimizeYagiElements:
    solver: AntennaSolver

    def execute(self, command: OptimizeYagiElementsCommand) -> BoundedResult:
        return OptimizeElements(self.solver).execute(
            OptimizeElementsCommand(
                build_parameters=command.build_parameters,
                variables=command.variables,
                start_values=command.start_values,
                target=command.target,
                base_spec=command.base_spec,
                objective=ElementOptimizationObjective(command.objective.value),
                max_evaluations=command.max_evaluations,
                samples=command.samples,
                passes=command.passes,
                cancel_token=command.cancel_token,
            )
        )
