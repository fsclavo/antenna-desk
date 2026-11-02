# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimize selected Yagi element lengths and gaps."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from enum import StrEnum

from ...domain.antennas.yagi import YagiElement, YagiParameters
from ...domain.common.units import wavelength_m
from ...domain.design.yagi_reference import (
    MAX_YAGI_ELEMENTS,
    MIN_YAGI_ELEMENTS,
    dl6wu_elements,
)
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


def resize_yagi(parameters: YagiParameters, count: int) -> YagiParameters:
    """Add trailing directors or remove trailing elements.

    Added directors follow the DL6WU reference scaled to the design frequency;
    existing elements and the driven-element index are preserved. The count
    may not remove the driven element.
    """

    minimum = max(MIN_YAGI_ELEMENTS, parameters.driven_index + 1)
    if count < minimum:
        raise ValueError(f"a Yagi needs at least {minimum} elements")
    elements = list(parameters.elements)
    if count <= len(elements):
        return replace(parameters, elements=tuple(elements[:count]))
    if count > MAX_YAGI_ELEMENTS:
        raise ValueError(f"a Yagi is limited to {MAX_YAGI_ELEMENTS} elements")

    reference = dl6wu_elements(count)
    wavelength = wavelength_m(parameters.frequency_hz)
    for index in range(len(elements), count):
        length_factor, position_factor = reference[index]
        previous_position_factor = reference[index - 1][1]
        gap = (position_factor - previous_position_factor) * wavelength
        previous = elements[-1]
        elements.append(
            YagiElement(
                position_m=previous.position_m + gap,
                length_m=length_factor * wavelength,
                radius_m=previous.radius_m,
            )
        )
    return replace(parameters, elements=tuple(elements))


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
