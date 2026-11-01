# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.matching_network import LNetwork


def test_inactive_network_returns_the_load() -> None:
    network = LNetwork()
    assert network.is_active is False
    assert network.input_impedance(complex(75.0, 10.0), 7_100_000.0) == complex(75.0, 10.0)


def test_series_inductance_and_shunt_capacitance_transform_the_load() -> None:
    network = LNetwork(
        series_inductance_h=1e-6,
        shunt_capacitance_f=100e-12,
    )
    frequency = 10_000_000.0
    load = complex(100.0, -20.0)
    omega = 2.0 * math.pi * frequency
    series = complex(0.0, omega * 1e-6)
    shunt = complex(0.0, omega * 100e-12)
    expected = series + 1.0 / (shunt + 1.0 / load)

    assert network.is_active is True
    assert network.input_impedance(load, frequency) == pytest.approx(expected)


def test_shunt_at_input_uses_the_other_orientation() -> None:
    network = LNetwork(
        series_capacitance_f=50e-12,
        shunt_inductance_h=2e-6,
        shunt_at_input=True,
    )
    frequency = 14_100_000.0
    load = complex(50.0, 0.0)
    omega = 2.0 * math.pi * frequency
    series = 1.0 / complex(0.0, omega * 50e-12)
    shunt = 1.0 / complex(0.0, omega * 2e-6)
    expected = 1.0 / (shunt + 1.0 / (series + load))

    assert network.input_impedance(load, frequency) == pytest.approx(expected)


def test_network_requires_one_series_and_one_shunt_element() -> None:
    with pytest.raises(ValueError, match="series and a shunt"):
        LNetwork(series_inductance_h=1e-6)


def test_network_rejects_series_l_and_c_together() -> None:
    with pytest.raises(ValueError, match="series branch"):
        LNetwork(
            series_inductance_h=1e-6,
            series_capacitance_f=100e-12,
            shunt_capacitance_f=100e-12,
        )
