# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shape constraints for the Yagi optimizer descriptor."""

from __future__ import annotations

from dataclasses import replace

import pytest

from antennadesk.domain.antennas.yagi import (
    YagiElement,
    YagiMatchType,
    YagiParameters,
    nbs_five_element,
)
from antennadesk.domain.common.units import wavelength_m
from antennadesk.domain.design.yagi_reference import dl6wu_elements
from antennadesk.domain.optimization.families.yagi import yagi_descriptor

FREQUENCY_HZ = 14_100_000.0


def _dl6wu_yagi(
    count: int = 5,
    *,
    frequency_hz: float = FREQUENCY_HZ,
    radius_m: float = 0.001,
) -> YagiParameters:
    wavelength = wavelength_m(frequency_hz)
    return YagiParameters(
        frequency_hz=frequency_hz,
        elements=tuple(
            YagiElement(
                position_m=spacing * wavelength,
                length_m=length * wavelength,
                radius_m=radius_m,
            )
            for length, spacing in dl6wu_elements(count)
        ),
        height_m=12.0,
        driven_index=1,
    )


def _scaled_dl6wu_radius(frequency_hz: float) -> float:
    # The reference table uses a 4 mm element diameter at 432 MHz. Scale it
    # with frequency, with a 0.2 mm radius floor for thin-wire modelling.
    return max(0.0002, 0.002 * 432_000_000.0 / frequency_hz)


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


@pytest.mark.parametrize("frequency_hz", [1_500_000_000.0, 2_400_000_000.0, 5_800_000_000.0])
@pytest.mark.parametrize("count", [5, 10, 15, 20, 32])
def test_dl6wu_high_frequency_start_is_in_bounds(
    count: int,
    frequency_hz: float,
) -> None:
    radius = _scaled_dl6wu_radius(frequency_hz)
    parameters = _dl6wu_yagi(count, frequency_hz=frequency_hz, radius_m=radius)
    descriptor = yagi_descriptor(parameters)

    assert descriptor.validate(descriptor.initial_values) == ()
    for variable in descriptor.variables:
        value = descriptor.initial_values[variable.name]
        assert variable.minimum <= value <= variable.maximum, variable.name
        span = variable.maximum - variable.minimum
        assert variable.step <= span, variable.name
        if variable.name.startswith("length_"):
            assert variable.minimum == pytest.approx(value * 0.88)
            assert variable.maximum == pytest.approx(value * 1.12)
            assert variable.step == pytest.approx(span / 100.0)

    rebuilt = descriptor.build_parameters(descriptor.initial_values)
    assert len(rebuilt.elements) == count
    for original, changed in zip(parameters.elements, rebuilt.elements, strict=True):
        assert changed.length_m == pytest.approx(original.length_m, rel=1e-12)
        assert changed.position_m == pytest.approx(original.position_m, abs=1e-12)


def test_folded_and_hairpin_yagi_variables_are_relative_at_5_8_ghz() -> None:
    frequency_hz = 5_800_000_000.0
    radius = _scaled_dl6wu_radius(frequency_hz)
    base = _dl6wu_yagi(5, frequency_hz=frequency_hz, radius_m=radius)

    folded = yagi_descriptor(
        replace(
            base,
            driven_folded=True,
            driven_fold_spacing_m=4.0 * radius,
            transformer_ratio=4.0,
        )
    )
    assert folded.validate(folded.initial_values) == ()
    fold_variable = next(
        variable for variable in folded.variables if variable.name == "driven_fold_spacing_m"
    )
    assert fold_variable.minimum == pytest.approx(4.0 * radius)

    hairpin = yagi_descriptor(
        replace(
            base,
            match_type=YagiMatchType.BETA_HAIRPIN,
            match_length_m=8.0 * radius,
            match_spacing_m=4.0 * radius,
        )
    )
    assert hairpin.validate(hairpin.initial_values) == ()
    match_length = next(
        variable for variable in hairpin.variables if variable.name == "match_length_m"
    )
    match_spacing = next(
        variable for variable in hairpin.variables if variable.name == "match_spacing_m"
    )
    assert match_length.minimum == pytest.approx(8.0 * radius)
    assert match_spacing.minimum == pytest.approx(4.0 * radius)


def test_global_shape_scaling_is_feasible() -> None:
    descriptor = yagi_descriptor(_dl6wu_yagi())
    values = dict(descriptor.initial_values)
    for name in tuple(values):
        if name.startswith("length_"):
            values[name] *= 1.03
        elif name.startswith("gap_"):
            values[name] *= 1.05

    assert descriptor.validate(values) == ()
