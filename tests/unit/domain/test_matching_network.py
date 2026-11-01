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


def test_designs_an_l_network_for_a_high_impedance_load() -> None:
    from antennadesk.domain.antennas.matching_network import design_l_network

    network = design_l_network(complex(100.0, 0.0), 10_000_000.0)

    assert network is not None
    assert network.input_impedance(complex(100.0, 0.0), 10_000_000.0) == pytest.approx(
        complex(50.0, 0.0), abs=1e-6
    )


def test_designs_an_l_network_for_a_low_impedance_complex_load() -> None:
    from antennadesk.domain.antennas.matching_network import design_l_network

    load = complex(25.0, 10.0)
    network = design_l_network(load, 14_100_000.0)

    assert network is not None
    assert network.input_impedance(load, 14_100_000.0) == pytest.approx(
        complex(50.0, 0.0), abs=1e-6
    )


def test_auto_design_returns_none_for_an_already_matched_load() -> None:
    from antennadesk.domain.antennas.matching_network import design_l_network

    assert design_l_network(complex(50.0, 0.0), 14_100_000.0) is None


def test_pi_network_with_only_a_series_element_is_a_series_reactance() -> None:
    from antennadesk.domain.antennas.matching_network import PiNetwork

    network = PiNetwork(series_inductance_h=1e-6)
    frequency = 10_000_000.0
    load = complex(50.0, 0.0)
    expected = load + complex(0.0, 2.0 * math.pi * frequency * 1e-6)

    assert network.input_impedance(load, frequency) == pytest.approx(expected)


def test_t_network_with_only_a_shunt_element_is_a_shunt_reactance() -> None:
    from antennadesk.domain.antennas.matching_network import TNetwork

    network = TNetwork(shunt_capacitance_f=100e-12)
    frequency = 10_000_000.0
    load = complex(50.0, 0.0)
    expected = 1.0 / (complex(0.0, 2.0 * math.pi * frequency * 100e-12) + 1.0 / load)

    assert network.input_impedance(load, frequency) == pytest.approx(expected)


def test_pi_and_t_networks_reject_empty_configurations() -> None:
    from antennadesk.domain.antennas.matching_network import PiNetwork, TNetwork

    with pytest.raises(ValueError, match="non-zero"):
        PiNetwork()
    with pytest.raises(ValueError, match="non-zero"):
        TNetwork()


def test_component_q_adds_series_loss_to_a_pi_branch() -> None:
    from antennadesk.domain.antennas.matching_network import PiNetwork

    frequency = 10_000_000.0
    inductance = 1e-6
    q_factor = 100.0
    network = PiNetwork(series_inductance_h=inductance, q_factor=q_factor)
    omega = 2.0 * math.pi * frequency
    expected = complex(50.0, 0.0) + complex(omega * inductance / q_factor, omega * inductance)

    assert network.input_impedance(complex(50.0, 0.0), frequency) == pytest.approx(expected)


def test_q_factor_must_be_positive_when_present() -> None:
    with pytest.raises(ValueError, match="q_factor"):
        LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12, q_factor=0.0)
