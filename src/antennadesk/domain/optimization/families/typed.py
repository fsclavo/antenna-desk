# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimizer descriptors for the remaining first-class typed families."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import replace

from ...antennas.beverage import BeverageParameters
from ...antennas.biquad import BiquadParameters
from ...antennas.discone import DisconeParameters
from ...antennas.endfed import EndFedParameters
from ...antennas.fan_dipole import FanDipoleParameters, FanElement
from ...antennas.folded_dipole import FoldedDipoleParameters
from ...antennas.hexbeam import HexbeamParameters
from ...antennas.inverted_l import InvertedLParameters
from ...antennas.inverted_v import InvertedVParameters
from ...antennas.j_pole import JPoleParameters
from ...antennas.loaded_dipole import LoadedDipoleParameters
from ...antennas.loop import LoopParameters
from ...antennas.moxon import MoxonParameters
from ...antennas.ocfd import OCFDParameters
from ...antennas.phased_vertical import PhasedVerticalParameters
from ...antennas.quad_beam import QuadBeamParameters
from ...antennas.ringo import RingoParameters
from ...antennas.t2fd import T2FDParameters
from ...antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ...antennas.trap_dipole import TrapDipoleParameters
from ...antennas.trap_yagi import TrapYagiParameters
from ...antennas.zepp import ZeppParameters
from ..constraints import ConstraintViolation
from ..descriptor import (
    AntennaOptimizerDescriptor,
    FamilyOptimizationObjective,
    ParameterBuilder,
    ParameterValidator,
)
from ..variables import OptimizationVariable, VariableKind
from .common import (
    COMMON_OBJECTIVES,
    around,
    collect,
    non_negative_violation,
    positive_violation,
    radius_around,
    violation,
)


def _length(
    name: str,
    label_key: str,
    group: str,
    value: float,
    fraction: float = 0.2,
    minimum: float = 0.1,
) -> OptimizationVariable:
    low, high = around(value, fraction, minimum=minimum)
    return OptimizationVariable(name, label_key, group, low, high, step=0.01)


def _radius(value: float) -> OptimizationVariable:
    low, high = radius_around(value)
    return OptimizationVariable(
        "wire_radius_m",
        "field.wire_radius",
        "optimize.group.conductor",
        low,
        high,
        unit="radius",
        step=0.0001,
    )


def _choice_ratio(name: str, label_key: str, value: float) -> OptimizationVariable:
    choices = tuple(sorted({value, 1.0, 4.0, 6.0, 9.0, 16.0, 49.0}))
    return OptimizationVariable(
        name,
        label_key,
        "optimize.group.loads",
        choices[0],
        choices[-1],
        kind=VariableKind.CHOICE,
        unit="ratio",
        choices=choices,
    )


def _descriptor(
    key: str,
    variables: tuple[OptimizationVariable, ...],
    initial: Mapping[str, float],
    build_parameters: ParameterBuilder,
    validate: ParameterValidator,
    default_objective: FamilyOptimizationObjective = FamilyOptimizationObjective.TARGET_IMPEDANCE,
    *,
    supports_boom_constraint: bool = False,
) -> AntennaOptimizerDescriptor:
    return AntennaOptimizerDescriptor(
        key=key,
        variables=variables,
        initial_values=initial,
        build_parameters=build_parameters,
        validate=validate,
        objectives=COMMON_OBJECTIVES,
        default_objective=default_objective,
        supports_boom_constraint=supports_boom_constraint,
    )


def folded_dipole_descriptor(parameters: FoldedDipoleParameters) -> AntennaOptimizerDescriptor:
    variables = (
        _length(
            "total_length_m",
            "field.length",
            "optimize.group.geometry",
            parameters.total_length_m,
            0.15,
        ),
        _length(
            "height_m", "field.height", "optimize.group.geometry", parameters.height_m, 0.25, 0.0
        ),
        _length(
            "spacing_m", "field.spacing", "optimize.group.geometry", parameters.spacing_m, 0.5, 0.01
        ),
        _radius(parameters.wire_radius_m),
    )
    initial = {
        "total_length_m": parameters.total_length_m,
        "height_m": parameters.height_m,
        "spacing_m": parameters.spacing_m,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> FoldedDipoleParameters:
        return replace(
            parameters,
            total_length_m=values["total_length_m"],
            height_m=values["height_m"],
            spacing_m=values["spacing_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        return collect(
            positive_violation("total_length_m", values["total_length_m"]),
            non_negative_violation("height_m", values["height_m"]),
            positive_violation("spacing_m", values["spacing_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        )

    return _descriptor("folded_dipole", variables, initial, build, validate)


def loop_descriptor(parameters: LoopParameters) -> AntennaOptimizerDescriptor:
    variables = (
        _length(
            "circumference_m",
            "field.circumference",
            "optimize.group.geometry",
            parameters.circumference_m,
            0.15,
        ),
        _length(
            "height_m", "field.height", "optimize.group.geometry", parameters.height_m, 0.25, 0.0
        ),
        _radius(parameters.wire_radius_m),
    )
    initial = {
        "circumference_m": parameters.circumference_m,
        "height_m": parameters.height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> LoopParameters:
        return replace(
            parameters,
            circumference_m=values["circumference_m"],
            height_m=values["height_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        return collect(
            positive_violation("circumference_m", values["circumference_m"]),
            non_negative_violation("height_m", values["height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        )

    return _descriptor("loop", variables, initial, build, validate)


def inverted_v_descriptor(parameters: InvertedVParameters) -> AntennaOptimizerDescriptor:
    angle_low = max(30.0, parameters.included_angle_deg - 20.0)
    angle_high = min(175.0, parameters.included_angle_deg + 20.0)
    variables = (
        _length(
            "leg_length_m",
            "inverted_v.leg_length",
            "optimize.group.geometry",
            parameters.leg_length_m,
            0.15,
        ),
        _length(
            "apex_height_m",
            "inverted_v.apex_height",
            "optimize.group.geometry",
            parameters.apex_height_m,
            0.25,
            0.1,
        ),
        OptimizationVariable(
            "included_angle_deg",
            "inverted_v.included_angle",
            "optimize.group.geometry",
            angle_low,
            angle_high,
            unit="deg",
            step=1.0,
        ),
        _radius(parameters.wire_radius_m),
    )
    initial = {
        "leg_length_m": parameters.leg_length_m,
        "apex_height_m": parameters.apex_height_m,
        "included_angle_deg": parameters.included_angle_deg,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> InvertedVParameters:
        return replace(
            parameters,
            leg_length_m=values["leg_length_m"],
            apex_height_m=values["apex_height_m"],
            included_angle_deg=values["included_angle_deg"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        angle = values["included_angle_deg"]
        end_height = values["apex_height_m"] - values["leg_length_m"] * math.cos(
            math.radians(angle) / 2.0
        )
        return collect(
            positive_violation("leg_length_m", values["leg_length_m"]),
            non_negative_violation("apex_height_m", values["apex_height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
            None
            if 0.0 < angle < 180.0
            else violation("included_angle_deg", 1.0, "optimize.constraint.positive"),
            None
            if end_height >= 0.0
            else violation("apex_height_m", -end_height, "optimize.constraint.positive"),
        )

    return _descriptor("inverted_v", variables, initial, build, validate)


def inverted_l_descriptor(parameters: InvertedLParameters) -> AntennaOptimizerDescriptor:
    variables = (
        _length(
            "vertical_height_m",
            "inverted_l.vertical_height",
            "optimize.group.geometry",
            parameters.vertical_height_m,
        ),
        _length(
            "horizontal_length_m",
            "inverted_l.horizontal_length",
            "optimize.group.geometry",
            parameters.horizontal_length_m,
        ),
        _length(
            "base_height_m",
            "field.base_height",
            "optimize.group.geometry",
            parameters.base_height_m,
            0.5,
            0.0,
        ),
        _radius(parameters.wire_radius_m),
    )
    initial = {
        "vertical_height_m": parameters.vertical_height_m,
        "horizontal_length_m": parameters.horizontal_length_m,
        "base_height_m": parameters.base_height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> InvertedLParameters:
        return replace(
            parameters,
            vertical_height_m=values["vertical_height_m"],
            horizontal_length_m=values["horizontal_length_m"],
            base_height_m=values["base_height_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        return collect(
            positive_violation("vertical_height_m", values["vertical_height_m"]),
            positive_violation("horizontal_length_m", values["horizontal_length_m"]),
            non_negative_violation("base_height_m", values["base_height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        )

    return _descriptor("inverted_l", variables, initial, build, validate)


def j_pole_descriptor(parameters: JPoleParameters) -> AntennaOptimizerDescriptor:
    variables = [
        _length(
            "radiator_height_m",
            "j_pole.radiator_height",
            "optimize.group.geometry",
            parameters.radiator_height_m,
            0.15,
        ),
        _length(
            "stub_length_m",
            "j_pole.stub_length",
            "optimize.group.geometry",
            parameters.stub_length_m,
            0.15,
        ),
        _length(
            "spacing_m",
            "j_pole.spacing",
            "optimize.group.geometry",
            parameters.spacing_m,
            0.5,
            0.01,
        ),
        _length(
            "feed_offset_m",
            "j_pole.feed_offset",
            "optimize.group.feed",
            parameters.feed_offset_m,
            0.5,
            0.0,
        ),
        _length(
            "base_height_m",
            "j_pole.base_height",
            "optimize.group.geometry",
            parameters.base_height_m,
            0.5,
            0.01,
        ),
        _radius(parameters.wire_radius_m),
    ]
    if parameters.folded:
        variables.append(
            _length("gap_m", "j_pole.gap", "optimize.group.geometry", parameters.gap_m, 0.5, 0.001)
        )
    initial = {
        "radiator_height_m": parameters.radiator_height_m,
        "stub_length_m": parameters.stub_length_m,
        "spacing_m": parameters.spacing_m,
        "feed_offset_m": parameters.feed_offset_m,
        "base_height_m": parameters.base_height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }
    if parameters.folded:
        initial["gap_m"] = parameters.gap_m

    def build(values: Mapping[str, float]) -> JPoleParameters:
        return replace(
            parameters,
            radiator_height_m=values["radiator_height_m"],
            stub_length_m=values["stub_length_m"],
            spacing_m=values["spacing_m"],
            feed_offset_m=values["feed_offset_m"],
            base_height_m=values["base_height_m"],
            gap_m=values.get("gap_m", parameters.gap_m),
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("radiator_height_m", values["radiator_height_m"]),
            positive_violation("stub_length_m", values["stub_length_m"]),
            positive_violation("spacing_m", values["spacing_m"]),
            non_negative_violation("feed_offset_m", values["feed_offset_m"]),
            positive_violation("base_height_m", values["base_height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        ]
        if values["feed_offset_m"] >= values["stub_length_m"]:
            issues.append(
                violation(
                    "feed_offset_m",
                    values["feed_offset_m"] - values["stub_length_m"] + 1e-9,
                    "optimize.constraint.feed_offset",
                )
            )
        if not parameters.folded and values["radiator_height_m"] < values["stub_length_m"]:
            issues.append(
                violation(
                    "radiator_height_m",
                    values["stub_length_m"] - values["radiator_height_m"],
                    "optimize.constraint.positive",
                )
            )
        if "gap_m" in values:
            issues.append(positive_violation("gap_m", values["gap_m"]))
        return collect(*issues)

    return _descriptor("j_pole", tuple(variables), initial, build, validate)


def ringo_descriptor(parameters: RingoParameters) -> AntennaOptimizerDescriptor:
    variables = (
        _length(
            "radiator_height_m",
            "ringo.radiator_height",
            "optimize.group.geometry",
            parameters.radiator_height_m,
            0.15,
        ),
        _length(
            "ring_diameter_m",
            "ringo.ring_diameter",
            "optimize.group.geometry",
            parameters.ring_diameter_m,
            0.5,
            0.01,
        ),
        _length(
            "ring_height_m",
            "ringo.ring_height",
            "optimize.group.geometry",
            parameters.ring_height_m,
            0.5,
            0.01,
        ),
        _radius(parameters.wire_radius_m),
    )
    initial = {
        "radiator_height_m": parameters.radiator_height_m,
        "ring_diameter_m": parameters.ring_diameter_m,
        "ring_height_m": parameters.ring_height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> RingoParameters:
        return replace(
            parameters,
            radiator_height_m=values["radiator_height_m"],
            ring_diameter_m=values["ring_diameter_m"],
            ring_height_m=values["ring_height_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        return collect(
            positive_violation("radiator_height_m", values["radiator_height_m"]),
            positive_violation("ring_diameter_m", values["ring_diameter_m"]),
            positive_violation("ring_height_m", values["ring_height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        )

    return _descriptor("ringo", variables, initial, build, validate)


def ocfd_descriptor(parameters: OCFDParameters) -> AntennaOptimizerDescriptor:
    variables = (
        _length(
            "total_length_m",
            "field.length",
            "optimize.group.geometry",
            parameters.total_length_m,
            0.15,
        ),
        OptimizationVariable(
            "feed_ratio",
            "ocfd.feed_offset",
            "optimize.group.feed",
            0.05,
            0.95,
            unit="fraction",
            step=0.01,
        ),
        _length(
            "height_m", "field.height", "optimize.group.geometry", parameters.height_m, 0.25, 0.0
        ),
        _radius(parameters.wire_radius_m),
        _choice_ratio("transformer_ratio", "ocfd.transformer_ratio", parameters.transformer_ratio),
    )
    initial = {
        "total_length_m": parameters.total_length_m,
        "feed_ratio": parameters.feed_ratio,
        "height_m": parameters.height_m,
        "wire_radius_m": parameters.wire_radius_m,
        "transformer_ratio": parameters.transformer_ratio,
    }

    def build(values: Mapping[str, float]) -> OCFDParameters:
        return replace(
            parameters,
            total_length_m=values["total_length_m"],
            feed_ratio=values["feed_ratio"],
            height_m=values["height_m"],
            wire_radius_m=values["wire_radius_m"],
            transformer_ratio=values["transformer_ratio"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        return collect(
            positive_violation("total_length_m", values["total_length_m"]),
            None
            if 0.0 < values["feed_ratio"] < 1.0
            else violation("feed_ratio", 1.0, "optimize.constraint.positive"),
            non_negative_violation("height_m", values["height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
            positive_violation("transformer_ratio", values["transformer_ratio"]),
        )

    return _descriptor("ocfd", variables, initial, build, validate)


def endfed_descriptor(parameters: EndFedParameters) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = [
        _length("length_m", "field.length", "optimize.group.geometry", parameters.length_m, 0.12),
        _length(
            "feed_height_m",
            "endfed.feed_height",
            "optimize.group.feed",
            parameters.feed_height_m,
            0.25,
            0.0,
        ),
        _length(
            "end_height_m",
            "endfed.end_height",
            "optimize.group.feed",
            parameters.end_height_m,
            0.25,
            0.0,
        ),
        _radius(parameters.wire_radius_m),
        _choice_ratio(
            "transformer_ratio",
            "endfed.transformer_ratio",
            parameters.transformer_ratio,
        ),
    ]
    initial = {
        "length_m": parameters.length_m,
        "feed_height_m": parameters.feed_height_m,
        "end_height_m": parameters.end_height_m,
        "wire_radius_m": parameters.wire_radius_m,
        "transformer_ratio": parameters.transformer_ratio,
    }
    if parameters.coil_active:
        low, high = around(
            parameters.loading_coil_offset_m,
            0.15,
            minimum=0.1,
        )
        variables.append(
            OptimizationVariable(
                "loading_coil_offset_m",
                "endfed.loading_coil_offset",
                "optimize.group.loads",
                low,
                high,
                step=0.01,
            )
        )
        initial["loading_coil_offset_m"] = parameters.loading_coil_offset_m
        low, high = around(
            parameters.loading_coil_inductance_h,
            0.5,
            minimum=1e-9,
        )
        variables.append(
            OptimizationVariable(
                "loading_coil_inductance_h",
                "endfed.loading_coil_inductance",
                "optimize.group.loads",
                low,
                high,
                unit="H",
                step=1e-7,
            )
        )
        initial["loading_coil_inductance_h"] = parameters.loading_coil_inductance_h
        if parameters.loading_coil_resistance_ohm > 0.0:
            low_r, high_r = around(
                parameters.loading_coil_resistance_ohm,
                0.9,
                minimum=0.0,
            )
            variables.append(
                OptimizationVariable(
                    "loading_coil_resistance_ohm",
                    "endfed.loading_coil_resistance",
                    "optimize.group.loads",
                    low_r,
                    high_r,
                    unit="ohm",
                    step=0.01,
                )
            )
            initial["loading_coil_resistance_ohm"] = parameters.loading_coil_resistance_ohm
    if parameters.counterpoise_length_m > 0.0:
        low, high = around(parameters.counterpoise_length_m, 0.3, minimum=0.1)
        variables.append(
            OptimizationVariable(
                "counterpoise_length_m",
                "endfed.counterpoise_length",
                "optimize.group.loads",
                low,
                high,
                step=0.01,
            )
        )
        initial["counterpoise_length_m"] = parameters.counterpoise_length_m
        low, high = around(parameters.counterpoise_height_m, 0.5, minimum=0.0)
        variables.append(
            OptimizationVariable(
                "counterpoise_height_m",
                "endfed.counterpoise_height",
                "optimize.group.loads",
                low,
                high,
                step=0.01,
            )
        )
        initial["counterpoise_height_m"] = parameters.counterpoise_height_m
        if parameters.counterpoise_azimuth_deg is not None:
            variables.append(
                OptimizationVariable(
                    "counterpoise_azimuth_deg",
                    "endfed.counterpoise_azimuth",
                    "optimize.group.loads",
                    0.0,
                    360.0,
                    unit="deg",
                    step=1.0,
                )
            )
            initial["counterpoise_azimuth_deg"] = parameters.counterpoise_azimuth_deg

    def build(values: Mapping[str, float]) -> EndFedParameters:
        return replace(
            parameters,
            length_m=values["length_m"],
            feed_height_m=values["feed_height_m"],
            end_height_m=values["end_height_m"],
            wire_radius_m=values["wire_radius_m"],
            transformer_ratio=values["transformer_ratio"],
            counterpoise_length_m=values.get(
                "counterpoise_length_m", parameters.counterpoise_length_m
            ),
            counterpoise_height_m=values.get(
                "counterpoise_height_m", parameters.counterpoise_height_m
            ),
            counterpoise_azimuth_deg=values.get(
                "counterpoise_azimuth_deg", parameters.counterpoise_azimuth_deg
            ),
            loading_coil_offset_m=values.get(
                "loading_coil_offset_m", parameters.loading_coil_offset_m
            ),
            loading_coil_inductance_h=values.get(
                "loading_coil_inductance_h", parameters.loading_coil_inductance_h
            ),
            loading_coil_resistance_ohm=values.get(
                "loading_coil_resistance_ohm", parameters.loading_coil_resistance_ohm
            ),
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("length_m", values["length_m"]),
            non_negative_violation("feed_height_m", values["feed_height_m"]),
            non_negative_violation("end_height_m", values["end_height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
            positive_violation("transformer_ratio", values["transformer_ratio"]),
        ]
        if abs(values["end_height_m"] - values["feed_height_m"]) > values["length_m"] + 1e-9:
            issues.append(
                violation(
                    "end_height_m",
                    abs(values["end_height_m"] - values["feed_height_m"]) - values["length_m"],
                    "optimize.constraint.endfed_height",
                )
            )
        if "counterpoise_length_m" in values:
            issues.append(
                non_negative_violation("counterpoise_length_m", values["counterpoise_length_m"])
            )
            issues.append(
                non_negative_violation("counterpoise_height_m", values["counterpoise_height_m"])
            )
        if "loading_coil_offset_m" in values:
            issues.append(
                positive_violation(
                    "loading_coil_offset_m",
                    values["loading_coil_offset_m"],
                )
            )
            if values["loading_coil_offset_m"] >= values["length_m"]:
                issues.append(
                    violation(
                        "loading_coil_offset_m",
                        values["loading_coil_offset_m"] - values["length_m"],
                        "optimize.constraint.endfed_coil_offset",
                    )
                )
            issues.append(
                positive_violation(
                    "loading_coil_inductance_h",
                    values["loading_coil_inductance_h"],
                )
            )
            if "loading_coil_resistance_ohm" in values:
                issues.append(
                    non_negative_violation(
                        "loading_coil_resistance_ohm",
                        values["loading_coil_resistance_ohm"],
                    )
                )
        return collect(*issues)

    return _descriptor("endfed", tuple(variables), initial, build, validate)


def fan_dipole_descriptor(parameters: FanDipoleParameters) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = []
    initial: dict[str, float] = {}
    for index, element in enumerate(parameters.elements):
        length_low, length_high = around(element.length_m, 0.15, minimum=0.1)
        variables.append(
            OptimizationVariable(
                f"length_{index}",
                "field.element_length",
                "optimize.group.geometry",
                length_low,
                length_high,
                step=0.01,
            )
        )
        initial[f"length_{index}"] = element.length_m
        angle_low = max(10.0, element.included_angle_deg - 15.0)
        angle_high = min(175.0, element.included_angle_deg + 15.0)
        variables.append(
            OptimizationVariable(
                f"angle_{index}",
                "inverted_v.included_angle",
                "optimize.group.geometry",
                angle_low,
                angle_high,
                unit="deg",
                step=1.0,
            )
        )
        initial[f"angle_{index}"] = element.included_angle_deg
    apex_low, apex_high = around(parameters.apex_height_m, 0.25, minimum=0.5)
    variables.append(
        OptimizationVariable(
            "apex_height_m",
            "field.height",
            "optimize.group.geometry",
            apex_low,
            apex_high,
            step=0.01,
        )
    )
    initial["apex_height_m"] = parameters.apex_height_m
    variables.append(_radius(parameters.wire_radius_m))
    initial["wire_radius_m"] = parameters.wire_radius_m

    def build(values: Mapping[str, float]) -> FanDipoleParameters:
        elements = tuple(
            FanElement(
                length_m=values[f"length_{index}"],
                included_angle_deg=values[f"angle_{index}"],
            )
            for index in range(len(parameters.elements))
        )
        return replace(
            parameters,
            elements=elements,
            apex_height_m=values["apex_height_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("apex_height_m", values["apex_height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        ]
        angles: list[float] = []
        for index, _element in enumerate(parameters.elements):
            length = values[f"length_{index}"]
            angle = values[f"angle_{index}"]
            angles.append(angle)
            issues.append(positive_violation(f"length_{index}", length))
            if not 0.0 < angle <= 180.0:
                issues.append(violation(f"angle_{index}", 1.0, "optimize.constraint.positive"))
            end_height = values["apex_height_m"] - (length / 2.0) * math.cos(
                math.radians(angle) / 2.0
            )
            if end_height < 0.0:
                issues.append(
                    violation(
                        f"length_{index}",
                        -end_height,
                        "optimize.constraint.positive",
                    )
                )
        for index, first in enumerate(angles):
            for second in angles[index + 1 :]:
                if math.isclose(first, second, abs_tol=0.5):
                    issues.append(
                        violation(
                            "included_angle_deg",
                            0.5 - abs(first - second),
                            "optimize.constraint.fan_angles",
                        )
                    )
        return collect(*issues)

    return _descriptor("fan_dipole", tuple(variables), initial, build, validate)


def trap_dipole_descriptor(parameters: TrapDipoleParameters) -> AntennaOptimizerDescriptor:
    variables = (
        _length(
            "inner_length_m",
            "trap_dipole.inner_length",
            "optimize.group.geometry",
            parameters.inner_length_m,
            0.15,
        ),
        _length(
            "outer_length_m",
            "trap_dipole.outer_length",
            "optimize.group.geometry",
            parameters.outer_length_m,
            0.2,
        ),
        _length(
            "height_m", "field.height", "optimize.group.geometry", parameters.height_m, 0.25, 0.0
        ),
        OptimizationVariable(
            "trap_frequency_hz",
            "trap_dipole.trap_frequency",
            "optimize.group.loads",
            max(parameters.frequency_hz * 1.05, parameters.trap_frequency_hz * 0.85),
            max(
                parameters.trap_frequency_hz * 1.15,
                max(parameters.frequency_hz * 1.05, parameters.trap_frequency_hz * 0.85) + 1000.0,
            ),
            unit="Hz",
            step=1000.0,
        ),
        OptimizationVariable(
            "trap_inductance_h",
            "trap_dipole.trap_inductance",
            "optimize.group.loads",
            max(1e-9, parameters.trap_inductance_h * 0.5),
            parameters.trap_inductance_h * 1.5,
            unit="H",
            step=1e-7,
        ),
        _radius(parameters.wire_radius_m),
    )
    initial = {
        "inner_length_m": parameters.inner_length_m,
        "outer_length_m": parameters.outer_length_m,
        "height_m": parameters.height_m,
        "trap_frequency_hz": parameters.trap_frequency_hz,
        "trap_inductance_h": parameters.trap_inductance_h,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> TrapDipoleParameters:
        return replace(
            parameters,
            inner_length_m=values["inner_length_m"],
            outer_length_m=values["outer_length_m"],
            height_m=values["height_m"],
            trap_frequency_hz=values["trap_frequency_hz"],
            trap_inductance_h=values["trap_inductance_h"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        return collect(
            positive_violation("inner_length_m", values["inner_length_m"]),
            positive_violation("outer_length_m", values["outer_length_m"]),
            non_negative_violation("height_m", values["height_m"]),
            positive_violation("trap_frequency_hz", values["trap_frequency_hz"]),
            positive_violation("trap_inductance_h", values["trap_inductance_h"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
            None
            if values["trap_frequency_hz"] > parameters.frequency_hz
            else violation("trap_frequency_hz", 1.0, "optimize.constraint.trap_frequency"),
        )

    return _descriptor("trap_dipole", variables, initial, build, validate)


def t2fd_descriptor(parameters: T2FDParameters) -> AntennaOptimizerDescriptor:
    variables = (
        _length("length_m", "t2fd.length", "optimize.group.geometry", parameters.length_m, 0.15),
        _length(
            "spacing_m", "t2fd.spacing", "optimize.group.geometry", parameters.spacing_m, 0.3, 0.01
        ),
        _length(
            "height_m", "field.height", "optimize.group.geometry", parameters.height_m, 0.25, 0.0
        ),
        OptimizationVariable(
            "termination_resistance_ohm",
            "t2fd.termination",
            "optimize.group.loads",
            *around(
                parameters.termination_resistance_ohm,
                0.5,
                minimum=10.0,
            ),
            unit="ohm",
            step=1.0,
        ),
        _choice_ratio(
            "transformer_ratio",
            "t2fd.transformer",
            parameters.transformer_ratio,
        ),
        _radius(parameters.wire_radius_m),
    )
    initial = {
        "length_m": parameters.length_m,
        "spacing_m": parameters.spacing_m,
        "height_m": parameters.height_m,
        "termination_resistance_ohm": parameters.termination_resistance_ohm,
        "transformer_ratio": parameters.transformer_ratio,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> T2FDParameters:
        return replace(
            parameters,
            length_m=values["length_m"],
            spacing_m=values["spacing_m"],
            height_m=values["height_m"],
            termination_resistance_ohm=values["termination_resistance_ohm"],
            transformer_ratio=values["transformer_ratio"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        return collect(
            positive_violation("length_m", values["length_m"]),
            positive_violation("spacing_m", values["spacing_m"]),
            non_negative_violation("height_m", values["height_m"]),
            positive_violation("termination_resistance_ohm", values["termination_resistance_ohm"]),
            positive_violation("transformer_ratio", values["transformer_ratio"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        )

    return _descriptor("t2fd", variables, initial, build, validate)


def transmission_line_doublet_descriptor(
    parameters: TransmissionLineDoubletParameters,
) -> AntennaOptimizerDescriptor:
    line_choices = tuple(
        sorted(
            {
                parameters.line_impedance_ohm,
                300.0,
                400.0,
                450.0,
                600.0,
            }
        )
    )
    velocity_low = max(0.5, parameters.line_velocity_factor - 0.1)
    velocity_high = min(1.0, parameters.line_velocity_factor + 0.05)
    if velocity_high <= velocity_low:
        velocity_high = velocity_low + 0.01
    variables = (
        _length(
            "dipole_total_length_m",
            "field.length",
            "optimize.group.geometry",
            parameters.dipole_total_length_m,
            0.15,
        ),
        _length(
            "height_m",
            "field.height",
            "optimize.group.geometry",
            parameters.height_m,
            0.25,
            0.0,
        ),
        _length(
            "feed_height_m",
            "endfed.feed_height",
            "optimize.group.feed",
            parameters.feed_height_m,
            0.5,
            0.0,
        ),
        OptimizationVariable(
            "line_impedance_ohm",
            "g5rv.line_impedance",
            "optimize.group.loads",
            line_choices[0],
            line_choices[-1],
            kind=VariableKind.CHOICE,
            unit="ohm",
            choices=line_choices,
            step=1.0,
        ),
        _length(
            "line_length_m",
            "g5rv.line_length",
            "optimize.group.loads",
            parameters.line_length_m,
            0.25,
            0.1,
        ),
        OptimizationVariable(
            "line_velocity_factor",
            "g5rv.velocity_factor",
            "optimize.group.loads",
            velocity_low,
            velocity_high,
            step=0.001,
        ),
        _radius(parameters.wire_radius_m),
    )
    initial = {
        "dipole_total_length_m": parameters.dipole_total_length_m,
        "height_m": parameters.height_m,
        "feed_height_m": parameters.feed_height_m,
        "line_impedance_ohm": parameters.line_impedance_ohm,
        "line_length_m": parameters.line_length_m,
        "line_velocity_factor": parameters.line_velocity_factor,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> TransmissionLineDoubletParameters:
        return replace(
            parameters,
            dipole_total_length_m=values["dipole_total_length_m"],
            height_m=values["height_m"],
            feed_height_m=values["feed_height_m"],
            line_impedance_ohm=values["line_impedance_ohm"],
            line_length_m=values["line_length_m"],
            line_velocity_factor=values["line_velocity_factor"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        return collect(
            positive_violation("dipole_total_length_m", values["dipole_total_length_m"]),
            non_negative_violation("height_m", values["height_m"]),
            non_negative_violation("feed_height_m", values["feed_height_m"]),
            positive_violation("line_impedance_ohm", values["line_impedance_ohm"]),
            positive_violation("line_length_m", values["line_length_m"]),
            None
            if 0.0 < values["line_velocity_factor"] <= 1.0
            else violation("line_velocity_factor", 1.0, "optimize.constraint.positive"),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        )

    return _descriptor(
        parameters.preset.antenna_type,
        variables,
        initial,
        build,
        validate,
    )


def zepp_descriptor(parameters: ZeppParameters) -> AntennaOptimizerDescriptor:
    variables = (
        _length(
            "radiator_length_m",
            "zepp.radiator_length",
            "optimize.group.geometry",
            parameters.radiator_length_m,
            0.15,
        ),
        _length(
            "matching_section_length_m",
            "zepp.matching_length",
            "optimize.group.geometry",
            parameters.matching_section_length_m,
            0.15,
        ),
        _length(
            "spacing_m",
            "zepp.spacing",
            "optimize.group.geometry",
            parameters.spacing_m,
            0.5,
            max(0.002, 2.0 * parameters.wire_radius_m + 0.001),
        ),
        _length(
            "base_height_m",
            "field.base_height",
            "optimize.group.geometry",
            parameters.base_height_m,
            0.5,
            0.01,
        ),
        _radius(parameters.wire_radius_m),
    )
    initial = {
        "radiator_length_m": parameters.radiator_length_m,
        "matching_section_length_m": parameters.matching_section_length_m,
        "spacing_m": parameters.spacing_m,
        "base_height_m": parameters.base_height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> ZeppParameters:
        return replace(
            parameters,
            radiator_length_m=values["radiator_length_m"],
            matching_section_length_m=values["matching_section_length_m"],
            spacing_m=values["spacing_m"],
            base_height_m=values["base_height_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        return collect(
            positive_violation("radiator_length_m", values["radiator_length_m"]),
            positive_violation("matching_section_length_m", values["matching_section_length_m"]),
            positive_violation("spacing_m", values["spacing_m"]),
            None
            if values["spacing_m"] > 2.0 * values["wire_radius_m"]
            else violation(
                "spacing_m",
                2.0 * values["wire_radius_m"] - values["spacing_m"] + 1e-9,
                "optimize.constraint.conductor_spacing",
            ),
            non_negative_violation("base_height_m", values["base_height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        )

    return _descriptor("zepp", variables, initial, build, validate)


def biquad_descriptor(parameters: BiquadParameters) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = [
        _length(
            "loop_side_m",
            "biquad.loop_side",
            "optimize.group.geometry",
            parameters.loop_side_m,
            0.15,
            0.01,
        ),
        _length(
            "base_height_m",
            "field.base_height",
            "optimize.group.geometry",
            parameters.base_height_m,
            0.5,
            0.0,
        ),
    ]
    if parameters.reflector_enabled:
        variables.append(
            _length(
                "reflector_spacing_m",
                "biquad.reflector_spacing",
                "optimize.group.geometry",
                parameters.reflector_spacing_m,
                0.3,
                0.001,
            )
        )
    variables.append(_radius(parameters.wire_radius_m))
    initial = {
        "loop_side_m": parameters.loop_side_m,
        "base_height_m": parameters.base_height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }
    if parameters.reflector_enabled:
        initial["reflector_spacing_m"] = parameters.reflector_spacing_m

    def build(values: Mapping[str, float]) -> BiquadParameters:
        return replace(
            parameters,
            loop_side_m=values["loop_side_m"],
            base_height_m=values["base_height_m"],
            reflector_spacing_m=values.get(
                "reflector_spacing_m",
                parameters.reflector_spacing_m,
            ),
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        spacing = values.get(
            "reflector_spacing_m",
            parameters.reflector_spacing_m,
        )
        issues: list[ConstraintViolation | None] = [
            positive_violation("loop_side_m", values["loop_side_m"]),
            non_negative_violation("base_height_m", values["base_height_m"]),
            positive_violation("reflector_spacing_m", spacing),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        ]
        if values["wire_radius_m"] > 0.0 and spacing <= 2.0 * values["wire_radius_m"]:
            issues.append(
                violation(
                    "reflector_spacing_m",
                    2.0 * values["wire_radius_m"] - spacing,
                    "optimize.constraint.reflector_spacing",
                )
            )
        return collect(*issues)

    return _descriptor(
        parameters.kind.antenna_type,
        tuple(variables),
        initial,
        build,
        validate,
    )


def beverage_descriptor(parameters: BeverageParameters) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = [
        _length(
            "length_m",
            "field.length",
            "optimize.group.geometry",
            parameters.length_m,
            0.2,
            0.1,
        ),
        _length(
            "height_m",
            "field.height",
            "optimize.group.geometry",
            parameters.height_m,
            0.5,
            0.1,
        ),
    ]
    if parameters.termination_enabled:
        low, high = around(
            parameters.termination_resistance_ohm,
            0.5,
            minimum=1.0,
        )
        variables.append(
            OptimizationVariable(
                "termination_resistance_ohm",
                "beverage.termination_resistance",
                "optimize.group.loads",
                low,
                high,
                unit="ohm",
                step=1.0,
            )
        )
    variables.append(_radius(parameters.wire_radius_m))
    initial = {
        "length_m": parameters.length_m,
        "height_m": parameters.height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }
    if parameters.termination_enabled:
        initial["termination_resistance_ohm"] = parameters.termination_resistance_ohm

    def build(values: Mapping[str, float]) -> BeverageParameters:
        return replace(
            parameters,
            length_m=values["length_m"],
            height_m=values["height_m"],
            termination_resistance_ohm=values.get(
                "termination_resistance_ohm",
                parameters.termination_resistance_ohm,
            ),
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        resistance = values.get(
            "termination_resistance_ohm",
            parameters.termination_resistance_ohm,
        )
        return collect(
            positive_violation("length_m", values["length_m"]),
            positive_violation("height_m", values["height_m"]),
            positive_violation("termination_resistance_ohm", resistance),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        )

    return _descriptor(
        "beverage",
        tuple(variables),
        initial,
        build,
        validate,
    )


def loaded_dipole_descriptor(
    parameters: LoadedDipoleParameters,
) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = []
    if not parameters.link_open:
        variables.append(
            _length(
                "total_length_m",
                "field.length",
                "optimize.group.geometry",
                parameters.total_length_m,
                0.15,
                0.1,
            )
        )
    variables.extend(
        [
            _length(
                "link_offset_m",
                "loaded_dipole.link_offset",
                "optimize.group.geometry",
                parameters.link_offset_m,
                0.5,
                0.01,
            ),
            _length(
                "height_m",
                "field.height",
                "optimize.group.geometry",
                parameters.height_m,
                0.5,
                0.1,
            ),
        ]
    )
    if parameters.loading_coil_enabled and not parameters.link_open:
        low, high = around(
            parameters.loading_coil_inductance_h,
            0.75,
            minimum=1e-9,
        )
        variables.append(
            OptimizationVariable(
                "loading_coil_inductance_h",
                "loaded_dipole.coil_inductance",
                "optimize.group.loads",
                low,
                high,
                unit="H",
                step=1e-7,
            )
        )
        low_r, high_r = around(
            parameters.loading_coil_resistance_ohm,
            0.9,
            minimum=0.0,
        )
        variables.append(
            OptimizationVariable(
                "loading_coil_resistance_ohm",
                "loaded_dipole.coil_resistance",
                "optimize.group.loads",
                low_r,
                high_r,
                unit="ohm",
                step=0.01,
            )
        )
    variables.append(_radius(parameters.wire_radius_m))
    initial = {
        "link_offset_m": parameters.link_offset_m,
        "height_m": parameters.height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }
    if not parameters.link_open:
        initial["total_length_m"] = parameters.total_length_m
    if parameters.loading_coil_enabled and not parameters.link_open:
        initial["loading_coil_inductance_h"] = parameters.loading_coil_inductance_h
        initial["loading_coil_resistance_ohm"] = parameters.loading_coil_resistance_ohm

    def build(values: Mapping[str, float]) -> LoadedDipoleParameters:
        return replace(
            parameters,
            total_length_m=values.get(
                "total_length_m",
                parameters.total_length_m,
            ),
            link_offset_m=values["link_offset_m"],
            height_m=values["height_m"],
            loading_coil_inductance_h=values.get(
                "loading_coil_inductance_h",
                parameters.loading_coil_inductance_h,
            ),
            loading_coil_resistance_ohm=values.get(
                "loading_coil_resistance_ohm",
                parameters.loading_coil_resistance_ohm,
            ),
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        total_length = values.get("total_length_m", parameters.total_length_m)
        offset = values["link_offset_m"]
        issues: list[ConstraintViolation | None] = [
            positive_violation("total_length_m", total_length),
            positive_violation("link_offset_m", offset),
            non_negative_violation("height_m", values["height_m"]),
            non_negative_violation(
                "loading_coil_inductance_h",
                values.get(
                    "loading_coil_inductance_h",
                    parameters.loading_coil_inductance_h,
                ),
            ),
            non_negative_violation(
                "loading_coil_resistance_ohm",
                values.get(
                    "loading_coil_resistance_ohm",
                    parameters.loading_coil_resistance_ohm,
                ),
            ),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        ]
        if offset > 0.0 and 2.0 * offset > total_length:
            issues.append(
                violation(
                    "link_offset_m",
                    2.0 * offset - total_length,
                    "loaded_dipole.constraint.offset",
                )
            )
        return collect(*issues)

    return _descriptor(
        "loaded_dipole",
        tuple(variables),
        initial,
        build,
        validate,
    )


def phased_vertical_descriptor(
    parameters: PhasedVerticalParameters,
) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = [
        _length(
            "height_m",
            "field.height",
            "optimize.group.geometry",
            parameters.height_m,
            0.25,
            0.5,
        ),
        _length(
            "spacing_m",
            "phased_vertical.spacing",
            "optimize.group.geometry",
            parameters.spacing_m,
            0.5,
            0.05,
        ),
        _length(
            "base_height_m",
            "field.base_height",
            "optimize.group.geometry",
            parameters.base_height_m,
            0.5,
            0.0,
        ),
        OptimizationVariable(
            "phase_step_deg",
            "phased_vertical.phase_step",
            "optimize.group.feed",
            -180.0,
            180.0,
            unit="deg",
            step=0.5,
        ),
        OptimizationVariable(
            "amplitude_taper",
            "phased_vertical.amplitude_taper",
            "optimize.group.feed",
            0.0,
            0.9,
            unit="fraction",
            step=0.01,
        ),
    ]
    if parameters.radial_count > 0:
        variables.append(
            _length(
                "radial_length_m",
                "vertical.radial_length",
                "optimize.group.geometry",
                parameters.radial_length_m,
                0.5,
                0.1,
            )
        )
    variables.append(_radius(parameters.wire_radius_m))
    initial = {
        "height_m": parameters.height_m,
        "spacing_m": parameters.spacing_m,
        "base_height_m": parameters.base_height_m,
        "phase_step_deg": parameters.phase_step_deg,
        "amplitude_taper": parameters.amplitude_taper,
        "wire_radius_m": parameters.wire_radius_m,
    }
    if parameters.radial_count > 0:
        initial["radial_length_m"] = parameters.radial_length_m

    def build(values: Mapping[str, float]) -> PhasedVerticalParameters:
        return replace(
            parameters,
            height_m=values["height_m"],
            spacing_m=values["spacing_m"],
            base_height_m=values["base_height_m"],
            phase_step_deg=values["phase_step_deg"],
            amplitude_taper=values["amplitude_taper"],
            radial_length_m=values.get(
                "radial_length_m",
                parameters.radial_length_m,
            ),
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("height_m", values["height_m"]),
            positive_violation("spacing_m", values["spacing_m"]),
            non_negative_violation("base_height_m", values["base_height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
            positive_violation(
                "radial_length_m",
                values.get("radial_length_m", parameters.radial_length_m),
            )
            if parameters.radial_count > 0
            else None,
        ]
        if values["spacing_m"] <= 2.0 * values["wire_radius_m"]:
            issues.append(
                violation(
                    "spacing_m",
                    2.0 * values["wire_radius_m"] - values["spacing_m"],
                    "optimize.constraint.conductor_spacing",
                )
            )
        if abs(values["phase_step_deg"]) > 360.0:
            issues.append(
                violation(
                    "phase_step_deg",
                    abs(values["phase_step_deg"]) - 360.0,
                    "phased_vertical.constraint.phase",
                )
            )
        if not 0.0 <= values["amplitude_taper"] <= 0.9:
            issues.append(
                violation(
                    "amplitude_taper",
                    max(values["amplitude_taper"] - 0.9, -values["amplitude_taper"]),
                    "phased_vertical.constraint.amplitude_taper",
                )
            )
        return collect(*issues)

    return _descriptor(
        "phased_vertical",
        tuple(variables),
        initial,
        build,
        validate,
        default_objective=FamilyOptimizationObjective.MAX_GAIN,
    )


def discone_descriptor(parameters: DisconeParameters) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = [
        _length(
            "cone_height_m",
            "discone.cone_height",
            "optimize.group.geometry",
            parameters.cone_height_m,
            0.3,
            0.05,
        ),
        _length(
            "cone_radius_m",
            "discone.cone_radius",
            "optimize.group.geometry",
            parameters.cone_radius_m,
            0.3,
            0.05,
        ),
        _length(
            "disc_radius_m",
            "discone.disc_radius",
            "optimize.group.geometry",
            parameters.disc_radius_m,
            0.3,
            0.05,
        ),
        _length(
            "base_height_m",
            "field.base_height",
            "optimize.group.geometry",
            parameters.base_height_m,
            0.5,
            0.0,
        ),
        _radius(parameters.wire_radius_m),
    ]
    initial = {
        "cone_height_m": parameters.cone_height_m,
        "cone_radius_m": parameters.cone_radius_m,
        "disc_radius_m": parameters.disc_radius_m,
        "base_height_m": parameters.base_height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> DisconeParameters:
        return replace(
            parameters,
            cone_height_m=values["cone_height_m"],
            cone_radius_m=values["cone_radius_m"],
            disc_radius_m=values["disc_radius_m"],
            base_height_m=values["base_height_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("cone_height_m", values["cone_height_m"]),
            positive_violation("cone_radius_m", values["cone_radius_m"]),
            positive_violation("disc_radius_m", values["disc_radius_m"]),
            non_negative_violation("base_height_m", values["base_height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        ]
        for name in ("cone_height_m", "cone_radius_m", "disc_radius_m"):
            amount = values[name]
            if amount <= 2.0 * values["wire_radius_m"]:
                issues.append(
                    violation(
                        name,
                        2.0 * values["wire_radius_m"] - amount,
                        "optimize.constraint.conductor_spacing",
                    )
                )
        if values["disc_radius_m"] < values["cone_radius_m"]:
            issues.append(
                violation(
                    "disc_radius_m",
                    values["cone_radius_m"] - values["disc_radius_m"],
                    "discone.constraint.disc_radius",
                )
            )
        return collect(*issues)

    return _descriptor(
        "discone",
        tuple(variables),
        initial,
        build,
        validate,
        default_objective=FamilyOptimizationObjective.MAX_GAIN,
    )


def hexbeam_descriptor(parameters: HexbeamParameters) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = [
        _length(
            "driver_half_length_m",
            "hexbeam.driver_half",
            "optimize.group.geometry",
            parameters.driver_half_length_m,
            0.12,
            0.05,
        ),
        _length(
            "reflector_half_length_m",
            "hexbeam.reflector_half",
            "optimize.group.geometry",
            parameters.reflector_half_length_m,
            0.12,
            0.05,
        ),
        _length(
            "turning_radius_m",
            "hexbeam.turning_radius",
            "optimize.group.geometry",
            parameters.turning_radius_m,
            0.2,
            0.05,
        ),
        _length(
            "tip_gap_m",
            "hexbeam.tip_gap",
            "optimize.group.geometry",
            parameters.tip_gap_m,
            0.3,
            0.01,
        ),
        _length(
            "height_m",
            "field.height",
            "optimize.group.geometry",
            parameters.height_m,
            0.5,
            0.0,
        ),
        _radius(parameters.wire_radius_m),
    ]
    initial = {
        "driver_half_length_m": parameters.driver_half_length_m,
        "reflector_half_length_m": parameters.reflector_half_length_m,
        "turning_radius_m": parameters.turning_radius_m,
        "tip_gap_m": parameters.tip_gap_m,
        "height_m": parameters.height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> HexbeamParameters:
        return replace(
            parameters,
            driver_half_length_m=values["driver_half_length_m"],
            reflector_half_length_m=values["reflector_half_length_m"],
            turning_radius_m=values["turning_radius_m"],
            tip_gap_m=values["tip_gap_m"],
            height_m=values["height_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("driver_half_length_m", values["driver_half_length_m"]),
            positive_violation("reflector_half_length_m", values["reflector_half_length_m"]),
            positive_violation("turning_radius_m", values["turning_radius_m"]),
            positive_violation("tip_gap_m", values["tip_gap_m"]),
            non_negative_violation("height_m", values["height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        ]
        if values["driver_half_length_m"] <= 1.5 * values["turning_radius_m"]:
            issues.append(
                violation(
                    "driver_half_length_m",
                    1.5 * values["turning_radius_m"] - values["driver_half_length_m"],
                    "hexbeam.constraint.driver_length",
                )
            )
        minimum_reflector = values["turning_radius_m"] + abs(
            values["turning_radius_m"] / 2.0 - values["tip_gap_m"]
        )
        if values["reflector_half_length_m"] <= minimum_reflector:
            issues.append(
                violation(
                    "reflector_half_length_m",
                    minimum_reflector - values["reflector_half_length_m"],
                    "hexbeam.constraint.reflector_length",
                )
            )
        if values["tip_gap_m"] <= 2.0 * values["wire_radius_m"]:
            issues.append(
                violation(
                    "tip_gap_m",
                    2.0 * values["wire_radius_m"] - values["tip_gap_m"],
                    "optimize.constraint.conductor_spacing",
                )
            )
        return collect(*issues)

    return _descriptor(
        "hexbeam",
        tuple(variables),
        initial,
        build,
        validate,
        default_objective=FamilyOptimizationObjective.MAX_GAIN,
    )


def trap_yagi_descriptor(parameters: TrapYagiParameters) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = [
        _length(
            "driven_length_m",
            "field.length",
            "optimize.group.geometry",
            parameters.driven_length_m,
            0.15,
            0.1,
        ),
        OptimizationVariable(
            "reflector_scale",
            "trap_yagi.reflector_scale",
            "optimize.group.geometry",
            1.0,
            1.2,
            unit="fraction",
            step=0.005,
        ),
        _length(
            "reflector_spacing_m",
            "trap_yagi.reflector_spacing",
            "optimize.group.geometry",
            parameters.reflector_spacing_m,
            0.3,
            0.05,
        ),
        _length(
            "trap_inset_m",
            "trap_yagi.trap_inset",
            "optimize.group.loads",
            parameters.trap_inset_m,
            0.2,
            0.05,
        ),
        OptimizationVariable(
            "trap_inductance_h",
            "trap_yagi.trap_inductance",
            "optimize.group.loads",
            parameters.trap_inductance_h * 0.5,
            parameters.trap_inductance_h * 2.0,
            unit="H",
            step=1e-8,
        ),
        _length(
            "height_m",
            "field.height",
            "optimize.group.geometry",
            parameters.height_m,
            0.5,
            0.0,
        ),
        _radius(parameters.wire_radius_m),
    ]
    if parameters.element_count == 3:
        variables.insert(
            3,
            OptimizationVariable(
                "director_scale",
                "trap_yagi.director_scale",
                "optimize.group.geometry",
                0.8,
                1.0,
                unit="fraction",
                step=0.005,
            ),
        )
        variables.insert(
            4,
            _length(
                "director_spacing_m",
                "trap_yagi.director_spacing",
                "optimize.group.geometry",
                parameters.director_spacing_m,
                0.3,
                0.05,
            ),
        )
    initial = {
        "driven_length_m": parameters.driven_length_m,
        "reflector_scale": parameters.reflector_scale,
        "reflector_spacing_m": parameters.reflector_spacing_m,
        "trap_inset_m": parameters.trap_inset_m,
        "trap_inductance_h": parameters.trap_inductance_h,
        "height_m": parameters.height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }
    if parameters.element_count == 3:
        initial["director_scale"] = parameters.director_scale
        initial["director_spacing_m"] = parameters.director_spacing_m

    def build(values: Mapping[str, float]) -> TrapYagiParameters:
        return replace(
            parameters,
            driven_length_m=values["driven_length_m"],
            reflector_scale=values["reflector_scale"],
            reflector_spacing_m=values["reflector_spacing_m"],
            trap_inset_m=values["trap_inset_m"],
            trap_inductance_h=values["trap_inductance_h"],
            height_m=values["height_m"],
            wire_radius_m=values["wire_radius_m"],
            director_scale=values.get("director_scale", parameters.director_scale),
            director_spacing_m=values.get("director_spacing_m", parameters.director_spacing_m),
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("driven_length_m", values["driven_length_m"]),
            positive_violation("reflector_spacing_m", values["reflector_spacing_m"]),
            positive_violation("trap_inset_m", values["trap_inset_m"]),
            positive_violation("trap_inductance_h", values["trap_inductance_h"]),
            non_negative_violation("height_m", values["height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
            positive_violation(
                "director_spacing_m",
                values.get("director_spacing_m", parameters.director_spacing_m),
            )
            if parameters.element_count == 3
            else None,
        ]
        shortest_half = (
            values["driven_length_m"]
            * min(1.0, values["reflector_scale"], values.get("director_scale", 1.0))
            / 2.0
        )
        if values["trap_inset_m"] >= shortest_half:
            issues.append(
                violation(
                    "trap_inset_m",
                    values["trap_inset_m"] - shortest_half,
                    "trap_yagi.constraint.trap_inset",
                )
            )
        if values["trap_inset_m"] <= 2.0 * values["wire_radius_m"]:
            issues.append(
                violation(
                    "trap_inset_m",
                    2.0 * values["wire_radius_m"] - values["trap_inset_m"],
                    "optimize.constraint.conductor_spacing",
                )
            )
        if values["reflector_spacing_m"] <= 2.0 * values["wire_radius_m"]:
            issues.append(
                violation(
                    "reflector_spacing_m",
                    2.0 * values["wire_radius_m"] - values["reflector_spacing_m"],
                    "optimize.constraint.conductor_spacing",
                )
            )
        if (
            parameters.element_count == 3
            and values.get("director_spacing_m", parameters.director_spacing_m)
            <= 2.0 * values["wire_radius_m"]
        ):
            issues.append(
                violation(
                    "director_spacing_m",
                    2.0 * values["wire_radius_m"]
                    - values.get("director_spacing_m", parameters.director_spacing_m),
                    "optimize.constraint.conductor_spacing",
                )
            )
        if not 1.0 <= values["reflector_scale"] <= 1.2:
            issues.append(
                violation(
                    "reflector_scale",
                    max(
                        values["reflector_scale"] - 1.2,
                        1.0 - values["reflector_scale"],
                    ),
                    "trap_yagi.constraint.reflector_scale",
                )
            )
        if parameters.element_count == 3:
            director_scale = values.get("director_scale", parameters.director_scale)
            if not 0.8 <= director_scale <= 1.0:
                issues.append(
                    violation(
                        "director_scale",
                        max(director_scale - 1.0, 0.8 - director_scale),
                        "trap_yagi.constraint.director_scale",
                    )
                )
        return collect(*issues)

    return _descriptor(
        "trap_yagi",
        tuple(variables),
        initial,
        build,
        validate,
        default_objective=FamilyOptimizationObjective.MAX_GAIN,
    )


def quad_beam_descriptor(parameters: QuadBeamParameters) -> AntennaOptimizerDescriptor:
    variables: list[OptimizationVariable] = [
        _length(
            "loop_side_m",
            "quad_beam.loop_side",
            "optimize.group.geometry",
            parameters.loop_side_m,
            0.15,
            0.1,
        ),
        _length(
            "reflector_spacing_m",
            "quad_beam.reflector_spacing",
            "optimize.group.geometry",
            parameters.reflector_spacing_m,
            0.3,
            0.05,
        ),
        _length(
            "height_m",
            "field.height",
            "optimize.group.geometry",
            parameters.height_m,
            0.5,
            0.0,
        ),
        OptimizationVariable(
            "reflector_scale",
            "quad_beam.reflector_scale",
            "optimize.group.geometry",
            1.0,
            1.2,
            unit="fraction",
            step=0.005,
        ),
        _radius(parameters.wire_radius_m),
    ]
    if parameters.element_count == 3:
        variables.insert(
            2,
            _length(
                "director_spacing_m",
                "quad_beam.director_spacing",
                "optimize.group.geometry",
                parameters.director_spacing_m,
                0.3,
                0.05,
            ),
        )
        variables.insert(
            3,
            OptimizationVariable(
                "director_scale",
                "quad_beam.director_scale",
                "optimize.group.geometry",
                0.8,
                1.0,
                unit="fraction",
                step=0.005,
            ),
        )
    initial = {
        "loop_side_m": parameters.loop_side_m,
        "reflector_spacing_m": parameters.reflector_spacing_m,
        "height_m": parameters.height_m,
        "reflector_scale": parameters.reflector_scale,
        "wire_radius_m": parameters.wire_radius_m,
    }
    if parameters.element_count == 3:
        initial["director_spacing_m"] = parameters.director_spacing_m
        initial["director_scale"] = parameters.director_scale

    def build(values: Mapping[str, float]) -> QuadBeamParameters:
        return replace(
            parameters,
            loop_side_m=values["loop_side_m"],
            reflector_spacing_m=values["reflector_spacing_m"],
            height_m=values["height_m"],
            reflector_scale=values["reflector_scale"],
            director_spacing_m=values.get("director_spacing_m", parameters.director_spacing_m),
            director_scale=values.get("director_scale", parameters.director_scale),
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("loop_side_m", values["loop_side_m"]),
            positive_violation("reflector_spacing_m", values["reflector_spacing_m"]),
            non_negative_violation("height_m", values["height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
            positive_violation(
                "director_spacing_m",
                values.get("director_spacing_m", parameters.director_spacing_m),
            )
            if parameters.element_count == 3
            else None,
        ]
        if values["loop_side_m"] <= 2.0 * values["wire_radius_m"]:
            issues.append(
                violation(
                    "loop_side_m",
                    2.0 * values["wire_radius_m"] - values["loop_side_m"],
                    "optimize.constraint.conductor_spacing",
                )
            )
        if values["reflector_spacing_m"] <= 2.0 * values["wire_radius_m"]:
            issues.append(
                violation(
                    "reflector_spacing_m",
                    2.0 * values["wire_radius_m"] - values["reflector_spacing_m"],
                    "optimize.constraint.conductor_spacing",
                )
            )
        if (
            parameters.element_count == 3
            and values.get("director_spacing_m", parameters.director_spacing_m)
            <= 2.0 * values["wire_radius_m"]
        ):
            issues.append(
                violation(
                    "director_spacing_m",
                    2.0 * values["wire_radius_m"]
                    - values.get("director_spacing_m", parameters.director_spacing_m),
                    "optimize.constraint.conductor_spacing",
                )
            )
        if not 1.0 <= values["reflector_scale"] <= 1.2:
            issues.append(
                violation(
                    "reflector_scale",
                    max(
                        values["reflector_scale"] - 1.2,
                        1.0 - values["reflector_scale"],
                    ),
                    "quad_beam.constraint.reflector_scale",
                )
            )
        if parameters.element_count == 3:
            director_scale = values.get("director_scale", parameters.director_scale)
            if not 0.8 <= director_scale <= 1.0:
                issues.append(
                    violation(
                        "director_scale",
                        max(director_scale - 1.0, 0.8 - director_scale),
                        "quad_beam.constraint.director_scale",
                    )
                )
        return collect(*issues)

    return _descriptor(
        "quad_beam",
        tuple(variables),
        initial,
        build,
        validate,
        default_objective=FamilyOptimizationObjective.MAX_GAIN,
    )


def moxon_descriptor(parameters: MoxonParameters) -> AntennaOptimizerDescriptor:
    variables = (
        _length("width_m", "moxon.width", "optimize.group.geometry", parameters.width_m, 0.15),
        _length("depth_m", "moxon.depth", "optimize.group.geometry", parameters.depth_m, 0.25),
        _length(
            "reflector_tip_m",
            "moxon.reflector_tip",
            "optimize.group.geometry",
            parameters.reflector_tip_m,
            0.5,
            0.001,
        ),
        _length(
            "driven_tip_m",
            "moxon.driven_tip",
            "optimize.group.geometry",
            parameters.driven_tip_m,
            0.5,
            0.001,
        ),
        _length(
            "height_m", "field.height", "optimize.group.geometry", parameters.height_m, 0.25, 0.1
        ),
        _radius(parameters.wire_radius_m),
    )
    initial = {
        "width_m": parameters.width_m,
        "depth_m": parameters.depth_m,
        "reflector_tip_m": parameters.reflector_tip_m,
        "driven_tip_m": parameters.driven_tip_m,
        "height_m": parameters.height_m,
        "wire_radius_m": parameters.wire_radius_m,
    }

    def build(values: Mapping[str, float]) -> MoxonParameters:
        return replace(
            parameters,
            width_m=values["width_m"],
            depth_m=values["depth_m"],
            reflector_tip_m=values["reflector_tip_m"],
            driven_tip_m=values["driven_tip_m"],
            height_m=values["height_m"],
            wire_radius_m=values["wire_radius_m"],
        )

    def validate(values: Mapping[str, float]) -> tuple[ConstraintViolation, ...]:
        issues: list[ConstraintViolation | None] = [
            positive_violation("width_m", values["width_m"]),
            positive_violation("depth_m", values["depth_m"]),
            positive_violation("reflector_tip_m", values["reflector_tip_m"]),
            positive_violation("driven_tip_m", values["driven_tip_m"]),
            positive_violation("height_m", values["height_m"]),
            positive_violation("wire_radius_m", values["wire_radius_m"]),
        ]
        if values["reflector_tip_m"] + values["driven_tip_m"] >= values["depth_m"]:
            issues.append(
                violation(
                    "reflector_tip_m",
                    values["reflector_tip_m"] + values["driven_tip_m"] - values["depth_m"],
                    "optimize.constraint.moxon_gap",
                )
            )
        return collect(*issues)

    return _descriptor(
        "moxon",
        variables,
        initial,
        build,
        validate,
        default_objective=FamilyOptimizationObjective.MAX_GAIN,
        supports_boom_constraint=True,
    )
