# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.matching_network import (
    LNetwork,
    PiNetwork,
    TNetwork,
    TransformerNetwork,
    input_shunt_l_network_swr_floor,
)


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


@pytest.mark.parametrize(
    "load",
    [
        complex(100.0, 0.0),
        complex(25.0, 0.0),
        complex(200.0, -50.0),
        complex(10.0, 20.0),
        complex(300.0, 80.0),
        complex(50.0, 0.0),
        complex(75.0, -30.0),
        complex(1000.0, -500.0),
    ],
)
@pytest.mark.parametrize("loaded_q", [None, 3.0, 10.0])
def test_designs_a_pi_network_for_complex_loads(
    load: complex,
    loaded_q: float | None,
) -> None:
    from antennadesk.domain.antennas.matching_network import design_pi_network

    frequency = 14_100_000.0
    network = design_pi_network(load, frequency, loaded_q=loaded_q)

    if loaded_q == 3.0 and load == complex(1000.0, -500.0):
        assert network is None
        return
    assert isinstance(network, PiNetwork)
    assert network.input_impedance(load, frequency) == pytest.approx(
        complex(50.0, 0.0),
        abs=1e-6,
    )


@pytest.mark.parametrize(
    "load",
    [
        complex(100.0, 0.0),
        complex(25.0, 0.0),
        complex(200.0, -50.0),
        complex(10.0, 20.0),
        complex(300.0, 80.0),
        complex(50.0, 0.0),
        complex(75.0, -30.0),
        complex(1000.0, -500.0),
    ],
)
@pytest.mark.parametrize("loaded_q", [None, 3.0, 10.0])
def test_designs_a_t_network_for_complex_loads(
    load: complex,
    loaded_q: float | None,
) -> None:
    from antennadesk.domain.antennas.matching_network import design_t_network

    frequency = 14_100_000.0
    network = design_t_network(load, frequency, loaded_q=loaded_q)

    if loaded_q == 3.0 and load == complex(1000.0, -500.0):
        assert network is None
        return
    assert isinstance(network, TNetwork)
    assert network.input_impedance(load, frequency) == pytest.approx(
        complex(50.0, 0.0),
        abs=1e-6,
    )


def test_pi_and_t_loaded_q_below_the_minimum_returns_none() -> None:
    from antennadesk.domain.antennas.matching_network import (
        design_pi_network,
        design_t_network,
    )

    load = complex(300.0, 80.0)
    assert design_pi_network(load, 14_100_000.0, loaded_q=2.0) is None
    assert design_t_network(load, 14_100_000.0, loaded_q=2.0) is None
    assert design_pi_network(load, 14_100_000.0, loaded_q=10.0) is not None
    assert design_t_network(load, 14_100_000.0, loaded_q=10.0) is not None


def test_pi_and_t_loaded_q_changes_the_component_values() -> None:
    from antennadesk.domain.antennas.matching_network import (
        design_pi_network,
        design_t_network,
    )

    load = complex(100.0, -20.0)
    pi_low = design_pi_network(load, 14_100_000.0, loaded_q=2.0)
    pi_high = design_pi_network(load, 14_100_000.0, loaded_q=8.0)
    t_low = design_t_network(load, 14_100_000.0, loaded_q=2.0)
    t_high = design_t_network(load, 14_100_000.0, loaded_q=8.0)

    assert pi_low is not None
    assert pi_high is not None
    assert t_low is not None
    assert t_high is not None
    assert pi_low.series_inductance_h != pytest.approx(pi_high.series_inductance_h)
    assert t_low.shunt_capacitance_f != pytest.approx(t_high.shunt_capacitance_f)


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


def test_abcd_input_impedance_matches_each_topology() -> None:
    from antennadesk.domain.antennas.matching_network import PiNetwork, TNetwork

    frequency = 14_100_000.0
    load = complex(80.0, -15.0)
    networks = (
        LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=50e-12, q_factor=100.0),
        LNetwork(
            series_capacitance_f=40e-12,
            shunt_inductance_h=1.5e-6,
            shunt_at_input=True,
            q_factor=120.0,
        ),
        PiNetwork(
            input_shunt_capacitance_f=30e-12,
            series_inductance_h=0.8e-6,
            output_shunt_capacitance_f=60e-12,
            q_factor=80.0,
        ),
        TNetwork(
            input_series_inductance_h=0.5e-6,
            shunt_capacitance_f=40e-12,
            output_series_inductance_h=0.7e-6,
            q_factor=90.0,
        ),
    )

    for network in networks:
        assert network.abcd(frequency).input_impedance(load) == pytest.approx(
            network.input_impedance(load, frequency)
        )


def test_matched_lossless_l_network_has_no_insertion_loss() -> None:
    from antennadesk.domain.antennas.matching_network import design_l_network
    from antennadesk.domain.antennas.two_port import transducer_gain_db

    load = complex(100.0, 0.0)
    network = design_l_network(load, 14_100_000.0)
    assert network is not None

    assert transducer_gain_db(network.abcd(14_100_000.0), 50.0, load) == pytest.approx(
        0.0, abs=1e-6
    )


def test_input_shunt_l_reports_the_floor_for_a_high_resistance_load() -> None:
    network = PiNetwork(
        input_shunt_capacitance_f=100e-12,
        series_inductance_h=198e-9,
    )

    assert input_shunt_l_network_swr_floor(
        network,
        complex(150.0, 0.0),
        50.0,
    ) == pytest.approx(3.0)
    assert (
        input_shunt_l_network_swr_floor(
            network,
            complex(30.0, 0.0),
            50.0,
        )
        is None
    )


def test_input_shunt_floor_requires_the_input_shunt_topology() -> None:
    network = LNetwork(
        series_inductance_h=1e-6,
        shunt_capacitance_f=100e-12,
        shunt_at_input=True,
    )
    assert input_shunt_l_network_swr_floor(
        network,
        complex(100.0, 10.0),
        50.0,
    ) == pytest.approx(2.0)

    output_shunt = LNetwork(
        series_inductance_h=1e-6,
        shunt_capacitance_f=100e-12,
        shunt_at_input=False,
    )
    assert (
        input_shunt_l_network_swr_floor(
            output_shunt,
            complex(100.0, 10.0),
            50.0,
        )
        is None
    )

    full_pi = PiNetwork(
        input_shunt_capacitance_f=100e-12,
        series_inductance_h=198e-9,
        output_shunt_capacitance_f=50e-12,
    )
    assert (
        input_shunt_l_network_swr_floor(
            full_pi,
            complex(150.0, 0.0),
            50.0,
        )
        is None
    )


def test_transformer_network_combines_shunt_c_and_l_with_series_leakage() -> None:
    network = TransformerNetwork(
        series_inductance_h=198e-9,
        input_shunt_capacitance_f=232e-12,
        input_shunt_inductance_h=25.8e-6,
    )
    frequency = 7_100_000.0
    load = complex(80.0, 37.0)
    omega = 2.0 * math.pi * frequency
    shunt = complex(0.0, omega * 232e-12) + complex(0.0, -1.0 / (omega * 25.8e-6))
    series = complex(0.0, omega * 198e-9)
    expected = 1.0 / (shunt + 1.0 / (series + load))

    assert network.input_impedance(load, frequency) == pytest.approx(expected)
    assert network.abcd(frequency).input_impedance(load) == pytest.approx(expected)
