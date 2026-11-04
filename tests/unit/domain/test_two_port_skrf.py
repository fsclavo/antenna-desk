# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Cross-check the two-port math against scikit-rf.

scikit-rf is a dev-only, BSD-3 independent implementation of transmission-line
physics and network algebra.  These tests build the same circuit with both
libraries and compare the input impedance.  They do not replace a physical
reference: they catch implementation and convention errors that a self-check
cannot.
"""

from __future__ import annotations

import math

import pytest
import skrf as rf

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.antennas.matching_network import LNetwork, PiNetwork, TNetwork
from antennadesk.domain.antennas.two_port import Abcd, transducer_gain_db

Z0 = 50.0
FREQUENCY_HZ = 14_100_000.0
SPEED_OF_LIGHT_M_PER_S = 299_792_458.0


def _media(
    *,
    velocity_factor: float = 1.0,
    loss_db_per_100m: float = 0.0,
) -> rf.media.DefinedGammaZ0:
    frequency = rf.Frequency(
        FREQUENCY_HZ / 1e6,
        FREQUENCY_HZ / 1e6,
        1,
        unit="MHz",
    )
    attenuation = loss_db_per_100m * math.log(10.0) / 2000.0
    phase = 2.0 * math.pi * FREQUENCY_HZ / (SPEED_OF_LIGHT_M_PER_S * velocity_factor)
    return rf.media.DefinedGammaZ0(
        frequency,
        z0=Z0,
        gamma=complex(attenuation, phase),
    )


def _load(media: rf.media.DefinedGammaZ0, impedance_ohm: complex):
    return media.load((impedance_ohm - Z0) / (impedance_ohm + Z0))


def _input_impedance(network, load) -> complex:
    return complex((network**load).z[0, 0, 0])


@pytest.mark.parametrize(
    ("length_m", "velocity_factor", "loss_db_per_100m", "load_ohm"),
    [
        (10.0, 1.0, 0.0, complex(75.0, -20.0)),
        (30.0, 0.66, 1.5, complex(75.0, -20.0)),
        (100.0, 0.8, 3.0, complex(40.0, 15.0)),
        (50.0, 1.0, 2.0, complex(Z0, 0.0)),
    ],
)
def test_feed_line_matches_scikit_rf(
    length_m: float,
    velocity_factor: float,
    loss_db_per_100m: float,
    load_ohm: complex,
) -> None:
    line = FeedLine(
        characteristic_impedance_ohm=Z0,
        length_m=length_m,
        velocity_factor=velocity_factor,
        matched_loss_db_per_100m=loss_db_per_100m,
    )
    media = _media(
        velocity_factor=velocity_factor,
        loss_db_per_100m=loss_db_per_100m,
    )
    expected = _input_impedance(
        media.line(d=length_m, unit="m"),
        _load(media, load_ohm),
    )

    assert line.input_impedance(load_ohm, FREQUENCY_HZ) == pytest.approx(
        expected,
        rel=1e-9,
        abs=1e-9,
    )


@pytest.mark.parametrize("shunt_at_input", [False, True])
def test_l_network_matches_scikit_rf(shunt_at_input: bool) -> None:
    load_ohm = complex(75.0, -20.0)
    network = LNetwork(
        series_inductance_h=1e-6,
        shunt_capacitance_f=100e-12,
        shunt_at_input=shunt_at_input,
    )
    media = _media()
    series = media.inductor(1e-6)
    shunt = media.shunt_capacitor(100e-12)
    expected = (
        _input_impedance(shunt**series, _load(media, load_ohm))
        if shunt_at_input
        else _input_impedance(series**shunt, _load(media, load_ohm))
    )

    assert network.input_impedance(load_ohm, FREQUENCY_HZ) == pytest.approx(
        expected,
        rel=1e-9,
        abs=1e-9,
    )


def test_pi_network_matches_scikit_rf() -> None:
    load_ohm = complex(75.0, -20.0)
    network = PiNetwork(
        input_shunt_capacitance_f=50e-12,
        series_inductance_h=1e-6,
        output_shunt_capacitance_f=80e-12,
    )
    media = _media()
    expected = _input_impedance(
        media.shunt_capacitor(50e-12) ** media.inductor(1e-6) ** media.shunt_capacitor(80e-12),
        _load(media, load_ohm),
    )

    assert network.input_impedance(load_ohm, FREQUENCY_HZ) == pytest.approx(
        expected,
        rel=1e-9,
        abs=1e-9,
    )


def test_t_network_matches_scikit_rf() -> None:
    load_ohm = complex(75.0, -20.0)
    network = TNetwork(
        input_series_inductance_h=0.5e-6,
        shunt_capacitance_f=100e-12,
        output_series_inductance_h=0.7e-6,
    )
    media = _media()
    expected = _input_impedance(
        media.inductor(0.5e-6) ** media.shunt_capacitor(100e-12) ** media.inductor(0.7e-6),
        _load(media, load_ohm),
    )

    assert network.input_impedance(load_ohm, FREQUENCY_HZ) == pytest.approx(
        expected,
        rel=1e-9,
        abs=1e-9,
    )


def test_feed_line_and_matching_network_cascade_matches_scikit_rf() -> None:
    load_ohm = complex(75.0, -20.0)
    line = FeedLine(
        characteristic_impedance_ohm=Z0,
        length_m=30.0,
        velocity_factor=0.66,
        matched_loss_db_per_100m=1.5,
    )
    network = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    media = _media(velocity_factor=0.66, loss_db_per_100m=1.5)
    expected = _input_impedance(
        media.line(d=30.0, unit="m") ** media.inductor(1e-6) ** media.shunt_capacitor(100e-12),
        _load(media, load_ohm),
    )

    cascade = line.abcd(FREQUENCY_HZ) @ network.abcd(FREQUENCY_HZ)

    assert cascade.input_impedance(load_ohm) == pytest.approx(expected, rel=1e-9, abs=1e-9)


def test_transducer_gain_matches_the_scikit_rf_s_parameters() -> None:
    load_ohm = complex(75.0, -20.0)
    line = FeedLine(
        characteristic_impedance_ohm=Z0,
        length_m=30.0,
        velocity_factor=0.66,
        matched_loss_db_per_100m=1.5,
    )
    network = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    media = _media(velocity_factor=0.66, loss_db_per_100m=1.5)
    two_port = (
        media.line(d=30.0, unit="m") ** media.inductor(1e-6) ** media.shunt_capacitor(100e-12)
    )

    s = two_port.s[0]
    gamma_load = (load_ohm - Z0) / (load_ohm + Z0)
    # Matched source (gamma_s = 0), so the transducer gain reduces to this.
    gain = abs(s[1, 0]) ** 2 * (1.0 - abs(gamma_load) ** 2) / abs(1.0 - s[1, 1] * gamma_load) ** 2

    cascade = line.abcd(FREQUENCY_HZ) @ network.abcd(FREQUENCY_HZ)

    assert transducer_gain_db(cascade, Z0, load_ohm) == pytest.approx(
        10.0 * math.log10(gain),
        abs=1e-9,
    )


def test_abcd_cascade_order_matches_scikit_rf() -> None:
    media = _media()
    load_ohm = complex(60.0, 25.0)
    series = Abcd.series(complex(0.0, 2.0 * math.pi * FREQUENCY_HZ * 1e-6))
    shunt = Abcd.shunt(complex(0.0, 2.0 * math.pi * FREQUENCY_HZ * 100e-12))

    expected = _input_impedance(
        media.inductor(1e-6) ** media.shunt_capacitor(100e-12),
        _load(media, load_ohm),
    )

    assert (series @ shunt).input_impedance(load_ohm) == pytest.approx(
        expected,
        rel=1e-9,
        abs=1e-9,
    )
