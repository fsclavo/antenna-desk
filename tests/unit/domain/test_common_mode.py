# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.common_mode import CommonModeChoke


def test_disabled_choke_is_inactive_and_needs_no_source() -> None:
    choke = CommonModeChoke()

    assert not choke.is_active
    assert choke.impedance_ohm == complex(0.0, 0.0)
    assert choke.series_inductance_h == 0.0
    assert choke.series_capacitance_f == 0.0


def test_enabled_choke_requires_a_non_zero_impedance_and_source() -> None:
    with pytest.raises(ValueError, match="non-zero"):
        CommonModeChoke(enabled=True, source="VNA")
    with pytest.raises(ValueError, match="source"):
        CommonModeChoke(enabled=True, resistance_ohm=100.0)


def test_choke_realizes_the_measured_reactance_as_l_or_c() -> None:
    frequency_hz = 14_000_000.0
    inductive = CommonModeChoke(
        enabled=True,
        measurement_frequency_hz=frequency_hz,
        resistance_ohm=80.0,
        reactance_ohm=400.0,
        source="VNA",
    )
    capacitive = CommonModeChoke(
        enabled=True,
        measurement_frequency_hz=frequency_hz,
        resistance_ohm=80.0,
        reactance_ohm=-400.0,
        source="VNA",
    )

    assert inductive.series_inductance_h == pytest.approx(400.0 / (2.0 * math.pi * frequency_hz))
    assert inductive.series_capacitance_f == 0.0
    assert capacitive.series_capacitance_f == pytest.approx(
        1.0 / (2.0 * math.pi * frequency_hz * 400.0)
    )
    assert capacitive.series_inductance_h == 0.0


def test_choke_flags_a_predominantly_reactive_measurement() -> None:
    resistive = CommonModeChoke(
        enabled=True,
        resistance_ohm=500.0,
        reactance_ohm=100.0,
        source="VNA",
    )
    reactive = CommonModeChoke(
        enabled=True,
        resistance_ohm=50.0,
        reactance_ohm=500.0,
        source="VNA",
    )

    assert not resistive.is_predominantly_reactive
    assert reactive.is_predominantly_reactive
