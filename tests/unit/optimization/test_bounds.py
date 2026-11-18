# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""HF2: descriptor bound invariants and no silent initial clamping."""

from __future__ import annotations

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.optimization.descriptor import (
    AntennaOptimizerDescriptor,
    FamilyOptimizationObjective,
    OptimizerBoundsError,
)
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.optimization.variables import (
    BoundIssueKind,
    OptimizationVariable,
    VariableKind,
)

_FOOT_M = 0.3048


def _moxon_2_4() -> MoxonParameters:
    scale = 14_170_000.0 / 2_400_000_000.0
    return MoxonParameters(
        frequency_hz=2_400_000_000.0,
        width_m=25.0 * _FOOT_M * scale,
        depth_m=9.57 * _FOOT_M * scale,
        reflector_tip_m=4.85 * _FOOT_M * scale,
        driven_tip_m=4.00 * _FOOT_M * scale,
        height_m=1.0,
        wire_radius_m=0.0005,
    )


def _vertical_2_4() -> VerticalParameters:
    return VerticalParameters(
        frequency_hz=2_400_000_000.0,
        height_m=0.03125,
        base_height_m=0.005,
    )


def _yagi_5_8() -> YagiParameters:
    return YagiParameters(
        frequency_hz=5_800_000_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=0.026, radius_m=0.0005),
            YagiElement(position_m=0.008, length_m=0.025, radius_m=0.0005),
        ),
        height_m=0.5,
    )


def _cebik_moxon_20m() -> MoxonParameters:
    return MoxonParameters(
        frequency_hz=14_170_000.0,
        width_m=25.00 * _FOOT_M,
        depth_m=9.57 * _FOOT_M,
        reflector_tip_m=4.85 * _FOOT_M,
        driven_tip_m=4.00 * _FOOT_M,
        height_m=10.0,
        wire_radius_m=0.000912,
    )


def _simple_descriptor(
    variable: OptimizationVariable,
    initial: float,
) -> AntennaOptimizerDescriptor:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    return AntennaOptimizerDescriptor(
        key="test_bounds",
        variables=(variable,),
        initial_values={variable.name: initial},
        build_parameters=lambda values: parameters,
        validate=lambda values: (),
        objectives=frozenset({FamilyOptimizationObjective.TARGET_IMPEDANCE}),
    )


@pytest.mark.parametrize(
    "parameters",
    [_moxon_2_4(), _vertical_2_4(), _yagi_5_8()],
    ids=["moxon_2_4", "vertical_2_4", "yagi_5_8"],
)
def test_high_frequency_designs_get_relative_bounds(parameters: object) -> None:
    availability = optimizer_availability(parameters)  # type: ignore[arg-type]

    assert availability.available is True
    assert availability.descriptor is not None
    descriptor = availability.descriptor
    for variable in descriptor.variables:
        value = descriptor.initial_values[variable.name]
        assert variable.minimum <= value <= variable.maximum, variable.name
        assert variable.maximum > variable.minimum, variable.name
        assert variable.step <= variable.maximum - variable.minimum, variable.name


def test_a_genuine_conductor_floor_still_reports_out_of_bounds() -> None:
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=0.001, radius_m=0.001),
            YagiElement(position_m=0.05, length_m=0.001, radius_m=0.001),
        ),
        height_m=10.0,
    )

    availability = optimizer_availability(parameters)

    assert availability.available is False
    assert availability.reason_key == "optimize.unavailable.bounds.outside"
    assert availability.reason_values["family"] == "yagi"
    assert availability.reason_values["variable"] in {"length_0", "length_1"}


def test_valid_hf_moxon_remains_available() -> None:
    availability = optimizer_availability(_cebik_moxon_20m())

    assert availability.available is True
    assert availability.descriptor is not None


def test_locked_variable_may_be_outside_bounds_until_unlocked() -> None:
    descriptor = AntennaOptimizerDescriptor(
        key="test_bounds_locked",
        variables=(
            OptimizationVariable(
                "width_m",
                "field.length",
                "optimize.group.geometry",
                0.0,
                1.0,
            ),
            OptimizationVariable(
                "height_m",
                "field.height",
                "optimize.group.geometry",
                0.1,
                0.2,
            ),
        ),
        initial_values={"width_m": 0.5, "height_m": 0.05},
        build_parameters=lambda values: DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        validate=lambda values: (),
        objectives=frozenset({FamilyOptimizationObjective.TARGET_IMPEDANCE}),
    )

    assert descriptor.variables[1].locked_by_default is True
    assert descriptor.bound_issue() is None

    issue = descriptor.bound_issue({"width_m", "height_m"})

    assert issue is not None
    assert issue.variable == "height_m"
    assert issue.kind is BoundIssueKind.OUTSIDE


def test_descriptor_rejects_a_non_finite_initial_value() -> None:
    variable = OptimizationVariable(
        "width_m",
        "field.length",
        "optimize.group.geometry",
        0.0,
        1.0,
    )

    with pytest.raises(OptimizerBoundsError) as info:
        _simple_descriptor(variable, float("nan"))

    assert info.value.reason_key == "optimize.unavailable.bounds.non_finite"
    assert info.value.reason_values["variable"] == "width_m"


def test_descriptor_rejects_a_degenerate_span() -> None:
    variable = OptimizationVariable(
        "width_m",
        "field.length",
        "optimize.group.geometry",
        0.0,
        1e-7,
    )

    with pytest.raises(OptimizerBoundsError) as info:
        _simple_descriptor(variable, 5e-8)

    assert info.value.reason_key == "optimize.unavailable.bounds.degenerate_span"


def test_descriptor_rejects_an_unrepresentable_integer_or_choice_value() -> None:
    integer = OptimizationVariable(
        "count",
        "vertical.radial_count",
        "optimize.group.loads",
        1.0,
        10.0,
        kind=VariableKind.INTEGER,
        unit="count",
    )
    with pytest.raises(OptimizerBoundsError) as integer_info:
        _simple_descriptor(integer, 2.5)
    assert integer_info.value.reason_key == "optimize.unavailable.bounds.unrepresentable"

    choice = OptimizationVariable(
        "ratio",
        "field.transformer_ratio",
        "optimize.group.feed",
        1.0,
        49.0,
        kind=VariableKind.CHOICE,
        unit="ratio",
        choices=(1.0, 4.0, 9.0, 49.0),
    )
    with pytest.raises(OptimizerBoundsError) as choice_info:
        _simple_descriptor(choice, 2.0)
    assert choice_info.value.reason_key == "optimize.unavailable.bounds.unrepresentable"
