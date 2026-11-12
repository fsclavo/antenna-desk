# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.antennas.two_port import (
    Abcd,
    dissipative_loss_db,
    reflection_loss_db,
    transducer_gain_db,
)


def test_dissipative_loss_matches_the_matched_line_and_grows_with_swr() -> None:
    line = FeedLine(
        characteristic_impedance_ohm=50.0,
        length_m=100.0,
        velocity_factor=1.0,
        matched_loss_db_per_100m=1.0,
    )
    frequency = 7_100_000.0

    matched = dissipative_loss_db(line.abcd(frequency), 50.0, complex(50.0, 0.0))
    mismatched = dissipative_loss_db(line.abcd(frequency), 50.0, complex(200.0, 0.0))

    assert matched == pytest.approx(1.0, abs=1e-6)
    assert mismatched > matched


def test_lossless_line_has_no_dissipative_loss_with_a_mismatched_load() -> None:
    line = FeedLine(
        characteristic_impedance_ohm=50.0,
        length_m=100.0,
        velocity_factor=1.0,
        matched_loss_db_per_100m=0.0,
    )

    loss = dissipative_loss_db(line.abcd(7_100_000.0), 50.0, complex(200.0, 0.0))

    assert loss == pytest.approx(0.0, abs=1e-9)


def test_series_and_shunt_impedances_match_circuit_theory() -> None:
    load = complex(50.0, 10.0)
    series = Abcd.series(complex(25.0, -5.0))
    shunt = Abcd.shunt(complex(0.0, 0.02))

    assert series.input_impedance(load) == pytest.approx(load + complex(25.0, -5.0))
    expected_shunt = 1.0 / (complex(0.0, 0.02) + 1.0 / load)
    assert shunt.input_impedance(load) == pytest.approx(expected_shunt)


def test_cascade_multiplies_in_input_to_output_order() -> None:
    load = complex(100.0, 20.0)
    series = Abcd.series(complex(10.0, 0.0))
    shunt = Abcd.shunt(complex(0.0, 0.01))

    cascade = series @ shunt

    assert cascade.input_impedance(load) == pytest.approx(
        series.input_impedance(shunt.input_impedance(load))
    )


def test_direct_connection_gain_is_the_mismatch_gain() -> None:
    load = complex(100.0, 0.0)
    direct = Abcd()

    assert transducer_gain_db(direct, 50.0, load) == pytest.approx(-0.5115, abs=0.001)
    assert reflection_loss_db(load, 50.0) == pytest.approx(0.5115, abs=0.001)


def test_matched_connection_has_zero_loss() -> None:
    assert transducer_gain_db(Abcd(), 50.0, complex(50.0, 0.0)) == pytest.approx(0.0)
    assert reflection_loss_db(complex(50.0, 0.0), 50.0) == pytest.approx(0.0)


def test_open_or_active_load_has_no_realizable_gain() -> None:
    assert transducer_gain_db(Abcd(), 50.0, complex(0.0, 0.0)) == -math.inf
    assert transducer_gain_db(Abcd(), 50.0, complex(-50.0, 0.0)) == -math.inf
