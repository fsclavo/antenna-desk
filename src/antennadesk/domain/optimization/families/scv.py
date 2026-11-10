# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimizer descriptor for half-square and bobtail-curtain arrays."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from ...antennas.scv import ScvParameters
from ..constraints import ConstraintViolation
from ..descriptor import AntennaOptimizerDescriptor, FamilyOptimizationObjective
from ..variables import OptimizationVariable
from .common import (
    around,
    collect,
    non_negative_violation,
    positive_violation,
    radius_around,
    violation,
)

_OBJECTIVES = frozenset(
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


def scv_descriptor(parameters: ScvParameters) -> AntennaOptimizerDescriptor:
    horizontal_low, horizontal_high = around(parameters.horizontal_length_m, 0.2, minimum=0.5)
    vertical_low, vertical_high = around(parameters.vertical_height_m, 0.2, minimum=0.5)
    base_low, base_high = around(parameters.base_height_m, 0.5, minimum=0.0)
    feed_high = max(0.01, parameters.vertical_height_m * 0.95)
    radius_low, radius_high = radius_around(parameters.wire_radius_m)
    variables = (
        OptimizationVariable(
            "horizontal_length_m",
            "scv.horizontal_length",
            "optimize.group.geometry",
            horizontal_low,
            horizontal_high,
            step=0.01,
        ),
        OptimizationVariable(
            "vertical_height_m",
            "scv.vertical_height",
            "optimize.group.geometry",
            vertical_low,
            vertical_high,
            step=0.01,
        ),
        OptimizationVariable(
            "base_height_m",
            "field.base_height",
            "optimize.group.geometry",
            base_low,
            base_high,
            step=0.01,
        ),
        OptimizationVariable(
            "feed_offset_m",
            "scv.feed_offset",
            "optimize.group.feed",
            0.0,
            feed_high,
            step=0.01,
        ),
        OptimizationVariable(
            "wire_radius_m",
            "scv.wire_radius",
            "optimize.group.conductor",
            radius_low,
            radius_high,
            unit="radius",
            step=0.0001,
        ),
    )
    initial = {
        "horizontal_length_m": parameters.horizontal_length_m,
        "vertical_height_m": parameters.vertical_height_m,
        "base_height_m": parameters.base_height_m,
        "feed_offset_m": parameters.feed_offset_m,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> ScvParameters:
        return replace(
            parameters,
            horizontal_length_m=values["horizontal_length_m"],
            vertical_height_m=values["vertical_height_m"],
            base_height_m=values["base_height_m"],
            feed_offset_m=values["feed_offset_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("horizontal_length_m", values["horizontal_length_m"]),
            positive_violation("vertical_height_m", values["vertical_height_m"]),
            non_negative_violation("base_height_m", values["base_height_m"]),
            non_negative_violation("feed_offset_m", values["feed_offset_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        ]
        if values["feed_offset_m"] >= values["vertical_height_m"]:
            issues.append(
                violation(
                    "feed_offset_m",
                    values["feed_offset_m"] - values["vertical_height_m"] + 1e-9,
                    "optimize.constraint.feed_offset",
                )
            )
        return collect(*issues)

    return AntennaOptimizerDescriptor(
        key=parameters.kind.value,
        variables=variables,
        initial_values=initial,
        build_parameters=build,
        validate=validate,
        objectives=_OBJECTIVES,
        default_objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
    )
