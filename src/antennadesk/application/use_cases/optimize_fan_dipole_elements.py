# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimize selected fan-dipole element lengths against an impedance target."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from ...domain.antennas.fan_dipole import FanDipoleParameters
from ...domain.optimization.multi_variable import BoundedResult, BoundedVariable
from ...domain.optimization.synthesis import SynthesisTarget
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .optimize_elements import OptimizeElements, OptimizeElementsCommand

BuildFanParameters = Callable[[Mapping[str, float]], FanDipoleParameters]


@dataclass(frozen=True, slots=True)
class OptimizeFanDipoleElementsCommand:
    build_parameters: BuildFanParameters
    variables: tuple[BoundedVariable, ...]
    start_values: Mapping[str, float]
    target: SynthesisTarget
    base_spec: SimulationSpec
    max_evaluations: int = 81
    samples: int = 5
    passes: int = 4
    cancel_token: CancelToken | None = None


@dataclass(frozen=True, slots=True)
class OptimizeFanDipoleElements:
    solver: AntennaSolver

    def execute(self, command: OptimizeFanDipoleElementsCommand) -> BoundedResult:
        return OptimizeElements(self.solver).execute(
            OptimizeElementsCommand(
                build_parameters=command.build_parameters,
                variables=command.variables,
                start_values=command.start_values,
                target=command.target,
                base_spec=command.base_spec,
                max_evaluations=command.max_evaluations,
                samples=command.samples,
                passes=command.passes,
                cancel_token=command.cancel_token,
            )
        )
