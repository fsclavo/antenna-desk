# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Component calculator formulas and limits."""

from __future__ import annotations

import pytest

from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.design.component_calculators import (
    capacitance_for_resonance_f,
    capacitive_reactance_ohm,
    impedance_ratio_for_turns_ratio,
    inductance_for_resonance_f,
    inductive_reactance_ohm,
    lc_resonance_hz,
    round_wire_resistance_per_m,
    skin_depth_m,
    solenoid_inductance_h,
    solenoid_turns_for_inductance,
    turns_ratio_for_impedance_ratio,
)


def test_solenoid_inductance_and_turns_invert() -> None:
    inductance = solenoid_inductance_h(
        turns=10,
        diameter_m=0.05,
        length_m=0.05,
    )
    turns = solenoid_turns_for_inductance(
        inductance_h=inductance,
        diameter_m=0.05,
        length_m=0.05,
    )

    assert inductance > 0.0
    assert turns == pytest.approx(10.0)


def test_solenoid_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="turns"):
        solenoid_inductance_h(turns=0, diameter_m=0.05, length_m=0.05)
    with pytest.raises(ValueError, match="diameter"):
        solenoid_inductance_h(turns=10, diameter_m=0.0, length_m=0.05)
    with pytest.raises(ValueError, match="inductance"):
        solenoid_turns_for_inductance(
            inductance_h=0.0,
            diameter_m=0.05,
            length_m=0.05,
        )


def test_lc_resonance_and_solutions_round_trip() -> None:
    inductance = 10e-6
    capacitance = 100e-12
    frequency = lc_resonance_hz(
        inductance_h=inductance,
        capacitance_f=capacitance,
    )

    assert frequency == pytest.approx(5_032_921.0, rel=1e-6)
    assert capacitance_for_resonance_f(
        inductance_h=inductance,
        frequency_hz=frequency,
    ) == pytest.approx(capacitance)
    assert inductance_for_resonance_f(
        capacitance_f=capacitance,
        frequency_hz=frequency,
    ) == pytest.approx(inductance)


def test_reactances_and_balun_ratios() -> None:
    assert inductive_reactance_ohm(
        inductance_h=10e-6,
        frequency_hz=7_100_000.0,
    ) == pytest.approx(446.1, rel=1e-3)
    assert capacitive_reactance_ohm(
        capacitance_f=100e-12,
        frequency_hz=7_100_000.0,
    ) == pytest.approx(224.16, rel=1e-3)
    assert impedance_ratio_for_turns_ratio(7.0) == pytest.approx(49.0)
    assert turns_ratio_for_impedance_ratio(49.0) == pytest.approx(7.0)


def test_skin_depth_and_wire_resistance() -> None:
    depth = skin_depth_m(frequency_hz=7_100_000.0, material=COPPER)
    dc, rf, same_depth = round_wire_resistance_per_m(
        frequency_hz=7_100_000.0,
        diameter_m=0.001,
        material=COPPER,
    )

    assert 1e-5 < depth < 5e-5
    assert same_depth == pytest.approx(depth)
    assert dc > 0.0
    assert rf > dc


def test_invalid_frequency_is_rejected() -> None:
    with pytest.raises(ValueError, match="frequency"):
        capacitance_for_resonance_f(
            inductance_h=10e-6,
            frequency_hz=0.0,
        )
    with pytest.raises(ValueError, match="frequency"):
        skin_depth_m(frequency_hz=0.0, material=COPPER)
