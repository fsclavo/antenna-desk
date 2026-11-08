# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimizer descriptor for a fixed-topology Yagi."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from ...antennas.polarization import Polarization
from ...antennas.yagi import ANTENNA_TYPE_YAGI, YagiMatchType, YagiParameters
from ..constraints import ConstraintViolation
from ..descriptor import AntennaOptimizerDescriptor, FamilyOptimizationObjective
from ..variables import OptimizationVariable
from .common import around, collect, non_negative_violation, positive_violation, violation

_OBJECTIVES = frozenset(
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

# The optimizer may adjust the starting taper, but it must not invert it.
# A small tolerance preserves published designs that are not strictly
# monotonic, such as the NBS five-element reference.
_DIRECTOR_LENGTH_RATIO_TOLERANCE = 0.01
_DIRECTOR_GAP_RATIO_TOLERANCE = 0.05


def yagi_descriptor(parameters: YagiParameters) -> AntennaOptimizerDescriptor:
    elements = parameters.elements
    if not elements:
        raise ValueError("a Yagi optimizer requires at least one element")
    variables: list[OptimizationVariable] = []
    initial: dict[str, float] = {}
    max_radius = max(element.radius_m for element in elements)

    for index, element in enumerate(elements):
        low, high = around(element.length_m, 0.12, minimum=0.05)
        name = f"length_{index}"
        variables.append(
            OptimizationVariable(
                name,
                "field.element_length",
                "optimize.group.geometry",
                low,
                high,
                step=0.01,
            )
        )
        initial[name] = element.length_m

    min_gap = max(4.0 * max_radius, 0.001)
    for index in range(1, len(elements)):
        current_gap = elements[index].position_m - elements[index - 1].position_m
        low, high = around(current_gap, 0.3, minimum=min_gap)
        name = f"gap_{index}"
        variables.append(
            OptimizationVariable(
                name,
                "yagi_optimize.current_gap",
                "optimize.group.geometry",
                low,
                high,
                step=0.01,
            )
        )
        initial[name] = current_gap

    height_low, height_high = around(parameters.height_m, 0.3, minimum=0.1)
    variables.append(
        OptimizationVariable(
            "height_m",
            "field.height",
            "optimize.group.geometry",
            height_low,
            height_high,
            step=0.01,
        )
    )
    initial["height_m"] = parameters.height_m

    if parameters.driven_folded:
        fold_low, fold_high = around(
            parameters.driven_fold_spacing_m,
            0.3,
            minimum=4.0 * max_radius,
        )
        variables.append(
            OptimizationVariable(
                "driven_fold_spacing_m",
                "yagi.fold_spacing",
                "optimize.group.geometry",
                fold_low,
                fold_high,
                step=0.001,
            )
        )
        initial["driven_fold_spacing_m"] = parameters.driven_fold_spacing_m

    if parameters.match_type is YagiMatchType.BETA_HAIRPIN:
        length_low, length_high = around(
            parameters.match_length_m,
            0.3,
            minimum=8.0 * max_radius,
        )
        variables.append(
            OptimizationVariable(
                "match_length_m",
                "yagi.match_length",
                "optimize.group.loads",
                length_low,
                length_high,
                step=0.001,
            )
        )
        initial["match_length_m"] = parameters.match_length_m
        spacing_low, spacing_high = around(
            parameters.match_spacing_m,
            0.3,
            minimum=4.0 * max_radius,
        )
        variables.append(
            OptimizationVariable(
                "match_spacing_m",
                "yagi.match_spacing",
                "optimize.group.loads",
                spacing_low,
                spacing_high,
                step=0.001,
            )
        )
        initial["match_spacing_m"] = parameters.match_spacing_m

    initial_lengths = {index: initial[f"length_{index}"] for index in range(len(elements))}
    initial_gaps = {index: initial[f"gap_{index}"] for index in range(1, len(elements))}

    def build(values: Mapping[str, float]) -> YagiParameters:
        updated_elements = list(elements)
        for index, element in enumerate(updated_elements):
            updated_elements[index] = replace(
                element,
                length_m=values[f"length_{index}"],
            )
        positions = [updated_elements[0].position_m]
        for index in range(1, len(updated_elements)):
            positions.append(positions[-1] + values[f"gap_{index}"])
        updated_elements = [
            replace(element, position_m=positions[index])
            for index, element in enumerate(updated_elements)
        ]
        updated = replace(
            parameters,
            elements=tuple(updated_elements),
            height_m=values["height_m"],
        )
        if "driven_fold_spacing_m" in values:
            updated = replace(
                updated,
                driven_fold_spacing_m=values["driven_fold_spacing_m"],
            )
        if "match_length_m" in values:
            updated = replace(
                updated,
                match_length_m=values["match_length_m"],
                match_spacing_m=values["match_spacing_m"],
            )
        return updated

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            non_negative_violation("height_m", values["height_m"])
        ]
        for index in range(len(elements)):
            issues.append(positive_violation(f"length_{index}", values[f"length_{index}"]))
        for index in range(1, len(elements)):
            gap = values[f"gap_{index}"]
            if gap < min_gap:
                issues.append(
                    violation(
                        f"gap_{index}",
                        min_gap - gap,
                        "optimize.constraint.conductor_spacing",
                    )
                )
        if "driven_fold_spacing_m" in values:
            spacing = values["driven_fold_spacing_m"]
            if spacing < 4.0 * max_radius:
                issues.append(
                    violation(
                        "driven_fold_spacing_m",
                        4.0 * max_radius - spacing,
                        "optimize.constraint.conductor_spacing",
                    )
                )
        if "match_length_m" in values:
            if values["match_length_m"] < 8.0 * max_radius:
                issues.append(
                    violation(
                        "match_length_m",
                        8.0 * max_radius - values["match_length_m"],
                        "optimize.constraint.match_length",
                    )
                )
            if values["match_spacing_m"] < 4.0 * max_radius:
                issues.append(
                    violation(
                        "match_spacing_m",
                        4.0 * max_radius - values["match_spacing_m"],
                        "optimize.constraint.conductor_spacing",
                    )
                )
        for index in range(parameters.driven_index + 1, len(elements)):
            previous = values[f"length_{index - 1}"]
            current = values[f"length_{index}"]
            if previous <= 0.0 or current <= 0.0:
                continue
            initial_ratio = initial_lengths[index] / initial_lengths[index - 1]
            ratio = current / previous
            minimum_ratio = initial_ratio * (1.0 - _DIRECTOR_LENGTH_RATIO_TOLERANCE)
            maximum_ratio = (
                1.0
                if initial_ratio <= 1.0
                else initial_ratio * (1.0 + _DIRECTOR_LENGTH_RATIO_TOLERANCE)
            )
            if ratio < minimum_ratio:
                issues.append(
                    violation(
                        f"length_{index}",
                        minimum_ratio - ratio,
                        "optimize.constraint.director_length_taper",
                    )
                )
            elif ratio > maximum_ratio:
                issues.append(
                    violation(
                        f"length_{index}",
                        ratio - maximum_ratio,
                        "optimize.constraint.director_length_taper",
                    )
                )
        for index in range(max(2, parameters.driven_index + 1), len(elements)):
            previous = values[f"gap_{index - 1}"]
            current = values[f"gap_{index}"]
            if previous <= 0.0 or current <= 0.0:
                continue
            initial_ratio = initial_gaps[index] / initial_gaps[index - 1]
            ratio = current / previous
            minimum_ratio = initial_ratio * (1.0 - _DIRECTOR_GAP_RATIO_TOLERANCE)
            maximum_ratio = initial_ratio * (1.0 + _DIRECTOR_GAP_RATIO_TOLERANCE)
            if ratio < minimum_ratio:
                issues.append(
                    violation(
                        f"gap_{index}",
                        minimum_ratio - ratio,
                        "optimize.constraint.director_gap_taper",
                    )
                )
            elif ratio > maximum_ratio:
                issues.append(
                    violation(
                        f"gap_{index}",
                        ratio - maximum_ratio,
                        "optimize.constraint.director_gap_taper",
                    )
                )
        if parameters.polarization is Polarization.VERTICAL:
            longest = max(values[f"length_{index}"] for index in range(len(elements)))
            if values["height_m"] < longest / 2.0:
                issues.append(
                    violation(
                        "height_m",
                        longest / 2.0 - values["height_m"],
                        "optimize.constraint.vertical_clearance",
                    )
                )
        return collect(*issues)

    return AntennaOptimizerDescriptor(
        key=ANTENNA_TYPE_YAGI,
        variables=tuple(variables),
        initial_values=initial,
        build_parameters=build,
        validate=validate,
        objectives=_OBJECTIVES,
        default_objective=FamilyOptimizationObjective.MAX_GAIN,
        supports_boom_constraint=True,
    )
