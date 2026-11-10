# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimizer descriptor for the wire dipole."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from ...antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from ..constraints import ConstraintViolation
from ..descriptor import AntennaOptimizerDescriptor, FamilyOptimizationObjective
from ..variables import OptimizationVariable
from .common import around, collect, non_negative_violation, positive_violation, radius_around

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


def dipole_descriptor(parameters: DipoleParameters) -> AntennaOptimizerDescriptor:
    length_low, length_high = around(parameters.total_length_m, 0.15, minimum=0.1)
    height_low, height_high = around(parameters.height_m, 0.25, minimum=0.0)
    radius_low, radius_high = radius_around(parameters.wire_radius_m)
    variables = (
        OptimizationVariable(
            name="total_length_m",
            label_key="field.length",
            group="optimize.group.geometry",
            minimum=length_low,
            maximum=length_high,
            step=0.01,
        ),
        OptimizationVariable(
            name="height_m",
            label_key="field.height",
            group="optimize.group.geometry",
            minimum=height_low,
            maximum=height_high,
            step=0.01,
        ),
        OptimizationVariable(
            name="wire_radius_m",
            label_key="field.wire_radius",
            group="optimize.group.conductor",
            minimum=radius_low,
            maximum=radius_high,
            unit="radius",
            step=0.0001,
        ),
    )
    initial = {
        "total_length_m": parameters.total_length_m,
        "height_m": parameters.height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> DipoleParameters:
        return replace(
            parameters,
            total_length_m=values["total_length_m"],
            height_m=values["height_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        return collect(
            positive_violation("total_length_m", values["total_length_m"]),
            non_negative_violation("height_m", values["height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        )

    return AntennaOptimizerDescriptor(
        key=ANTENNA_TYPE_WIRE_DIPOLE,
        variables=variables,
        initial_values=initial,
        build_parameters=build,
        validate=validate,
        objectives=_OBJECTIVES,
        default_objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
    )


__all__ = ["dipole_descriptor"]
