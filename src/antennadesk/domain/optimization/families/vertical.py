# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimizer descriptor for the vertical radiator and its radial/load system."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from ...antennas.vertical import (
    ANTENNA_TYPE_VERTICAL,
    MAX_RADIALS,
    MAX_TOP_HAT_WIRES,
    VerticalParameters,
)
from ..constraints import ConstraintViolation
from ..descriptor import AntennaOptimizerDescriptor, FamilyOptimizationObjective
from ..variables import OptimizationVariable, VariableKind
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
        FamilyOptimizationObjective.MAX_GAIN,
        FamilyOptimizationObjective.MAX_EFFICIENCY,
        FamilyOptimizationObjective.MAX_BANDWIDTH,
        FamilyOptimizationObjective.MULTI_OBJECTIVE,
    }
)


def vertical_descriptor(parameters: VerticalParameters) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = []
    initial: dict[str, float] = {}
    height_low, height_high = around(parameters.height_m, 0.25, minimum=0.5)
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
    base_low, base_high = around(parameters.base_height_m, 0.5, minimum=0.0)
    variables.append(
        OptimizationVariable(
            "base_height_m",
            "field.base_height",
            "optimize.group.geometry",
            base_low,
            base_high,
            step=0.01,
        )
    )
    initial["base_height_m"] = parameters.base_height_m

    if parameters.radial_count > 0:
        radial_low, radial_high = around(parameters.radial_length_m, 0.3, minimum=0.1)
        variables.append(
            OptimizationVariable(
                "radial_length_m",
                "vertical.radial_length",
                "optimize.group.loads",
                radial_low,
                radial_high,
                step=0.01,
            )
        )
        initial["radial_length_m"] = parameters.radial_length_m
        radial_count_low = max(1, round(parameters.radial_count * 0.5))
        radial_count_high = min(
            MAX_RADIALS,
            max(parameters.radial_count + 4, round(parameters.radial_count * 2)),
        )
        variables.append(
            OptimizationVariable(
                "radial_count",
                "vertical.radial_count",
                "optimize.group.loads",
                float(radial_count_low),
                float(radial_count_high),
                kind=VariableKind.INTEGER,
                unit="count",
                step=1.0,
            )
        )
        initial["radial_count"] = float(parameters.radial_count)
        variables.append(
            OptimizationVariable(
                "radial_angle_deg",
                "vertical.radial_angle",
                "optimize.group.geometry",
                0.0,
                360.0,
                unit="deg",
                step=1.0,
            )
        )
        initial["radial_angle_deg"] = parameters.radial_angle_deg

    if parameters.loading_coil_enabled:
        coil_low, coil_high = around(
            parameters.loading_coil_inductance_h,
            0.5,
            minimum=1e-9,
        )
        variables.append(
            OptimizationVariable(
                "loading_coil_inductance_h",
                "vertical.loading_coil_inductance",
                "optimize.group.loads",
                coil_low,
                coil_high,
                unit="H",
                step=1e-7,
            )
        )
        initial["loading_coil_inductance_h"] = parameters.loading_coil_inductance_h
        offset_high = max(0.01, parameters.height_m * 0.95)
        variables.append(
            OptimizationVariable(
                "loading_coil_offset_m",
                "vertical.loading_coil_offset",
                "optimize.group.loads",
                0.0,
                offset_high,
                step=0.01,
            )
        )
        initial["loading_coil_offset_m"] = parameters.loading_coil_offset_m

    if parameters.top_hat_enabled:
        hat_low, hat_high = around(parameters.top_hat_radius_m, 0.5, minimum=0.05)
        variables.append(
            OptimizationVariable(
                "top_hat_radius_m",
                "vertical.top_hat_radius",
                "optimize.group.loads",
                hat_low,
                hat_high,
                step=0.01,
            )
        )
        initial["top_hat_radius_m"] = parameters.top_hat_radius_m
        top_hat_low = max(1, parameters.top_hat_wire_count - 2)
        top_hat_high = min(
            MAX_TOP_HAT_WIRES,
            max(parameters.top_hat_wire_count + 4, parameters.top_hat_wire_count * 2),
        )
        variables.append(
            OptimizationVariable(
                "top_hat_wire_count",
                "vertical.top_hat_wires",
                "optimize.group.loads",
                float(top_hat_low),
                float(top_hat_high),
                kind=VariableKind.INTEGER,
                unit="count",
                step=1.0,
            )
        )
        initial["top_hat_wire_count"] = float(parameters.top_hat_wire_count)

    radius_low, radius_high = radius_around(parameters.wire_radius_m)
    variables.append(
        OptimizationVariable(
            "wire_radius_m",
            "vertical.wire_radius",
            "optimize.group.conductor",
            radius_low,
            radius_high,
            unit="radius",
            step=0.0001,
        )
    )
    initial["wire_radius_m"] = parameters.wire_radius_m

    def build(values: Mapping[str, float]) -> VerticalParameters:
        return replace(
            parameters,
            height_m=values.get("height_m", parameters.height_m),
            base_height_m=values.get("base_height_m", parameters.base_height_m),
            radial_length_m=values.get("radial_length_m", parameters.radial_length_m),
            radial_count=round(values.get("radial_count", float(parameters.radial_count))),
            radial_angle_deg=values.get("radial_angle_deg", parameters.radial_angle_deg),
            loading_coil_offset_m=values.get(
                "loading_coil_offset_m",
                parameters.loading_coil_offset_m,
            ),
            loading_coil_inductance_h=values.get(
                "loading_coil_inductance_h",
                parameters.loading_coil_inductance_h,
            ),
            top_hat_radius_m=values.get("top_hat_radius_m", parameters.top_hat_radius_m),
            top_hat_wire_count=round(
                values.get("top_hat_wire_count", float(parameters.top_hat_wire_count))
            ),
            wire_radius_m=values.get("wire_radius_m", parameters.wire_radius_m),
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("height_m", values["height_m"]),
            non_negative_violation("base_height_m", values["base_height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        ]
        if "radial_length_m" in values:
            if values["radial_count"] < 1.0:
                issues.append(violation("radial_count", 1.0, "optimize.constraint.radial_count"))
            issues.append(positive_violation("radial_length_m", values["radial_length_m"]))
        if "loading_coil_inductance_h" in values:
            issues.append(
                non_negative_violation(
                    "loading_coil_inductance_h",
                    values["loading_coil_inductance_h"],
                )
            )
            if values["loading_coil_offset_m"] > values["height_m"]:
                issues.append(
                    violation(
                        "loading_coil_offset_m",
                        values["loading_coil_offset_m"] - values["height_m"],
                        "optimize.constraint.coil_offset",
                    )
                )
        if "top_hat_radius_m" in values:
            issues.append(positive_violation("top_hat_radius_m", values["top_hat_radius_m"]))
            if values["top_hat_wire_count"] < 1.0:
                issues.append(
                    violation("top_hat_wire_count", 1.0, "optimize.constraint.top_hat_wires")
                )
        return collect(*issues)

    return AntennaOptimizerDescriptor(
        key=ANTENNA_TYPE_VERTICAL,
        variables=tuple(variables),
        initial_values=initial,
        build_parameters=build,
        validate=validate,
        objectives=_OBJECTIVES,
        default_objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
    )
