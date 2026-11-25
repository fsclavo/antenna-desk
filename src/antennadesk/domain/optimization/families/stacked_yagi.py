# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded spacing/phase optimizer for the stacked-Yagi composed family."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from ...antennas.polarization import Polarization
from ...antennas.stacked_yagi import StackedYagiParameters
from ..constraints import ConstraintViolation
from ..descriptor import AntennaOptimizerDescriptor, FamilyOptimizationObjective
from ..variables import OptimizationVariable, VariableKind
from .common import COMMON_OBJECTIVES, collect, relative_step, violation


def stacked_yagi_descriptor(
    parameters: StackedYagiParameters,
) -> AntennaOptimizerDescriptor:
    maximum_spacing = parameters.maximum_spacing_m
    if maximum_spacing is None:
        raise ValueError("the stack needs a max_top_height_m envelope to optimize spacing")
    minimum_spacing = parameters.minimum_spacing_m
    if maximum_spacing <= minimum_spacing:
        raise ValueError("the stack top-height envelope leaves no searchable spacing")

    variables = (
        OptimizationVariable(
            "spacing_m",
            "stacked_yagi.spacing",
            "optimize.group.geometry",
            minimum_spacing,
            maximum_spacing,
            step=relative_step(minimum_spacing, maximum_spacing),
        ),
        OptimizationVariable(
            "phase_step_deg",
            "stacked_yagi.phase_step",
            "optimize.group.feed",
            -180.0,
            180.0,
            unit="deg",
            step=0.5,
        ),
        OptimizationVariable(
            "amplitude_ratio",
            "stacked_yagi.amplitude_ratio",
            "optimize.group.feed",
            0.05,
            2.0,
            unit="fraction",
            step=0.01,
            locked_by_default=True,
        ),
        OptimizationVariable(
            "count",
            "stacked_yagi.level_count",
            "optimize.group.geometry",
            2.0,
            4.0,
            kind=VariableKind.CHOICE,
            unit="count",
            choices=(2.0, 3.0, 4.0),
            locked_by_default=True,
        ),
        OptimizationVariable(
            "max_top_height_m",
            "stacked_yagi.max_top_height",
            "optimize.group.geometry",
            1e-9,
            parameters.max_top_height_m,
            step=max(1e-6, parameters.max_top_height_m / 1000.0),
            locked_by_default=True,
        ),
    )
    initial = {
        "spacing_m": parameters.spacing_m,
        "phase_step_deg": parameters.phase_step_deg,
        "amplitude_ratio": parameters.amplitude_ratio,
        "count": float(parameters.count),
        "max_top_height_m": parameters.max_top_height_m,
    }

    def build(values: Mapping[str, float]) -> StackedYagiParameters:
        return replace(
            parameters,
            count=round(values["count"]),
            spacing_m=values["spacing_m"],
            phase_step_deg=values["phase_step_deg"],
            amplitude_ratio=values["amplitude_ratio"],
            max_top_height_m=values["max_top_height_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        def stack_top_m(candidate: Mapping[str, float]) -> float:
            half_span = (
                parameters.element_span_m / 2.0
                if parameters.yagi.polarization is Polarization.VERTICAL
                else 0.0
            )
            return (
                parameters.yagi.height_m
                + (round(candidate["count"]) - 1) * candidate["spacing_m"]
                + half_span
            )

        issues = [
            (
                violation(
                    "spacing_m",
                    minimum_spacing - values["spacing_m"],
                    "optimize.constraint.stacked_yagi_overlap",
                )
                if values["spacing_m"] < minimum_spacing
                else None
            ),
            (
                violation(
                    "spacing_m",
                    values["spacing_m"] - maximum_spacing,
                    "optimize.constraint.stacked_yagi_envelope",
                )
                if values["spacing_m"] > maximum_spacing
                else None
            ),
            (
                violation(
                    "phase_step_deg",
                    abs(values["phase_step_deg"]) - 180.0,
                    "stacked_yagi.constraint.phase",
                )
                if abs(values["phase_step_deg"]) > 180.0
                else None
            ),
            (
                violation(
                    "max_top_height_m",
                    stack_top_m(values) - values["max_top_height_m"],
                    "optimize.constraint.stacked_yagi_envelope",
                )
                if values["max_top_height_m"] > 0.0
                and stack_top_m(values) > values["max_top_height_m"] + 1e-9
                else None
            ),
            (
                violation(
                    "amplitude_ratio",
                    max(0.05 - values["amplitude_ratio"], values["amplitude_ratio"] - 2.0),
                    "stacked_yagi.constraint.amplitude_ratio",
                )
                if not 0.05 <= values["amplitude_ratio"] <= 2.0
                else None
            ),
        ]
        return collect(*issues)

    return AntennaOptimizerDescriptor(
        key="stacked_yagi",
        variables=variables,
        initial_values=initial,
        build_parameters=build,
        validate=validate,
        objectives=COMMON_OBJECTIVES,
        default_objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
        context_note_key="stacked_yagi.optimizer_note",
    )
