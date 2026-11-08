# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shape constraints for the Yagi optimizer descriptor."""

from __future__ import annotations

from antennadesk.domain.antennas.yagi import (
    YagiElement,
    YagiParameters,
    nbs_five_element,
)
from antennadesk.domain.common.units import wavelength_m
from antennadesk.domain.design.yagi_reference import dl6wu_elements
from antennadesk.domain.optimization.families.yagi import yagi_descriptor

FREQUENCY_HZ = 14_100_000.0


def _dl6wu_yagi(count: int = 5) -> YagiParameters:
    wavelength = wavelength_m(FREQUENCY_HZ)
    return YagiParameters(
        frequency_hz=FREQUENCY_HZ,
        elements=tuple(
            YagiElement(
                position_m=spacing * wavelength,
                length_m=length * wavelength,
                radius_m=0.001,
            )
            for length, spacing in dl6wu_elements(count)
        ),
        height_m=12.0,
        driven_index=1,
    )


def test_dl6wu_starting_taper_is_feasible() -> None:
    descriptor = yagi_descriptor(_dl6wu_yagi())

    assert descriptor.validate(descriptor.initial_values) == ()
    built = descriptor.build_parameters(descriptor.initial_values)
    assert isinstance(built, YagiParameters)
    assert len(built.elements) == 5


def test_director_length_inversion_is_rejected() -> None:
    descriptor = yagi_descriptor(_dl6wu_yagi())
    values = dict(descriptor.initial_values)
    values["length_3"] = values["length_2"] * 1.02

    violations = descriptor.validate(values)

    assert any(
        violation.message_key == "optimize.constraint.director_length_taper"
        for violation in violations
    )


def test_director_length_jump_is_rejected() -> None:
    descriptor = yagi_descriptor(_dl6wu_yagi())
    values = dict(descriptor.initial_values)
    values["length_3"] = values["length_2"] * 0.90

    violations = descriptor.validate(values)

    assert any(
        violation.message_key == "optimize.constraint.director_length_taper"
        for violation in violations
    )


def test_first_director_longer_than_driven_is_rejected() -> None:
    descriptor = yagi_descriptor(_dl6wu_yagi())
    values = dict(descriptor.initial_values)
    values["length_2"] = values["length_1"] * 1.02

    violations = descriptor.validate(values)

    assert any(
        violation.message_key == "optimize.constraint.director_length_taper"
        for violation in violations
    )


def test_director_gap_inversion_is_rejected() -> None:
    descriptor = yagi_descriptor(_dl6wu_yagi())
    values = dict(descriptor.initial_values)
    values["gap_3"] = values["gap_2"] * 0.5

    violations = descriptor.validate(values)

    assert any(
        violation.message_key == "optimize.constraint.director_gap_taper"
        for violation in violations
    )


def test_nbs_non_monotonic_start_is_preserved_but_not_amplified() -> None:
    parameters = nbs_five_element(frequency_hz=FREQUENCY_HZ, height_m=12.0)
    descriptor = yagi_descriptor(parameters)

    assert descriptor.validate(descriptor.initial_values) == ()

    values = dict(descriptor.initial_values)
    values["length_4"] = values["length_3"] * 1.10

    violations = descriptor.validate(values)

    assert any(
        violation.message_key == "optimize.constraint.director_length_taper"
        for violation in violations
    )


def test_nbs_uniform_gap_trend_is_preserved() -> None:
    parameters = nbs_five_element(frequency_hz=FREQUENCY_HZ, height_m=12.0)
    descriptor = yagi_descriptor(parameters)
    values = dict(descriptor.initial_values)
    values["gap_3"] = values["gap_2"] * 1.20

    violations = descriptor.validate(values)

    assert any(
        violation.message_key == "optimize.constraint.director_gap_taper"
        for violation in violations
    )


def test_dl6wu_first_director_gap_trend_is_preserved() -> None:
    descriptor = yagi_descriptor(_dl6wu_yagi())
    values = dict(descriptor.initial_values)
    values["gap_2"] = values["gap_1"] * 1.20

    violations = descriptor.validate(values)

    assert any(
        violation.message_key == "optimize.constraint.director_gap_taper"
        for violation in violations
    )


def test_global_shape_scaling_is_feasible() -> None:
    descriptor = yagi_descriptor(_dl6wu_yagi())
    values = dict(descriptor.initial_values)
    for name in tuple(values):
        if name.startswith("length_"):
            values[name] *= 1.03
        elif name.startswith("gap_"):
            values[name] *= 1.05

    assert descriptor.validate(values) == ()
