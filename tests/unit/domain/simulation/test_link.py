# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace

import pytest

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.antennas.matching_network import (
    MatchingNetworkPosition,
    design_l_network,
)
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.link import link_budget
from antennadesk.domain.simulation.spec import SimulationSpec

FREQUENCY_HZ = 14_100_000.0


def _spec(**overrides: object) -> SimulationSpec:
    values: dict[str, object] = {
        "frequency_plan": FrequencyPlan.single(FREQUENCY_HZ),
    }
    values.update(overrides)
    return SimulationSpec(**values)


def test_matched_antenna_has_no_link_loss() -> None:
    budget = link_budget(
        antenna_impedance_ohm=complex(50.0, 0.0),
        frequency_hz=FREQUENCY_HZ,
        spec=_spec(),
    )

    assert budget.input_impedance_ohm == pytest.approx(complex(50.0, 0.0))
    assert budget.transducer_gain_db == pytest.approx(0.0)
    assert budget.mismatch_loss_db == pytest.approx(0.0)
    assert budget.feed_line_loss_db == pytest.approx(0.0)
    assert budget.network_loss_db == pytest.approx(0.0)


def test_mismatched_antenna_reports_the_reflection_loss() -> None:
    budget = link_budget(
        antenna_impedance_ohm=complex(100.0, 0.0),
        frequency_hz=FREQUENCY_HZ,
        spec=_spec(),
    )

    assert budget.transducer_gain_db == pytest.approx(-0.5115, abs=0.001)
    assert budget.mismatch_loss_db == pytest.approx(0.5115, abs=0.001)


def test_ideal_transformer_matches_the_transformed_load() -> None:
    budget = link_budget(
        antenna_impedance_ohm=complex(200.0, 0.0),
        frequency_hz=FREQUENCY_HZ,
        spec=_spec(feed_transformer_ratio=4.0),
    )

    assert budget.input_impedance_ohm == pytest.approx(complex(50.0, 0.0))
    assert budget.transducer_gain_db == pytest.approx(0.0)
    assert budget.mismatch_loss_db == pytest.approx(0.0)


def test_balun_loss_is_frequency_dependent_and_reduces_realized_gain() -> None:
    from antennadesk.domain.antennas.balun import BalunLoss

    balun = BalunLoss(
        reference_frequency_hz=14_100_000.0,
        reference_loss_db=0.5,
        exponent=0.5,
    )
    at_reference = link_budget(
        antenna_impedance_ohm=complex(50.0, 0.0),
        frequency_hz=14_100_000.0,
        spec=_spec(balun_loss=balun),
    )
    at_double = link_budget(
        antenna_impedance_ohm=complex(50.0, 0.0),
        frequency_hz=28_200_000.0,
        spec=_spec(balun_loss=balun),
    )

    assert at_reference.balun_loss_db == pytest.approx(0.5)
    assert at_reference.transducer_gain_db == pytest.approx(-0.5)
    assert at_double.balun_loss_db == pytest.approx(0.5 * 2**0.5)
    assert at_double.transducer_gain_db == pytest.approx(-0.5 * 2**0.5)


def test_matched_feed_line_reports_its_matched_loss() -> None:
    line = FeedLine(
        characteristic_impedance_ohm=50.0,
        length_m=100.0,
        velocity_factor=1.0,
        matched_loss_db_per_100m=1.0,
    )
    budget = link_budget(
        antenna_impedance_ohm=complex(50.0, 0.0),
        frequency_hz=FREQUENCY_HZ,
        spec=_spec(feed_line=line),
    )

    assert budget.input_impedance_ohm == pytest.approx(complex(50.0, 0.0), abs=1e-6)
    assert budget.transducer_gain_db == pytest.approx(-1.0, abs=1e-6)
    assert budget.feed_line_loss_db == pytest.approx(1.0)


def test_lossless_matching_network_has_no_insertion_loss() -> None:
    load = complex(100.0, 0.0)
    network = design_l_network(load, FREQUENCY_HZ)
    assert network is not None
    budget = link_budget(
        antenna_impedance_ohm=load,
        frequency_hz=FREQUENCY_HZ,
        spec=_spec(matching_network=network),
    )

    assert budget.transducer_gain_db == pytest.approx(0.0, abs=1e-6)
    assert budget.network_loss_db == pytest.approx(0.0, abs=1e-6)


def test_a_shack_tuner_makes_the_line_carry_the_mismatch() -> None:
    load = complex(500.0, 0.0)
    network = design_l_network(load, FREQUENCY_HZ)
    assert network is not None
    line = FeedLine(
        characteristic_impedance_ohm=50.0,
        length_m=30.0,
        velocity_factor=0.66,
        matched_loss_db_per_100m=2.0,
    )
    feedpoint = link_budget(
        antenna_impedance_ohm=load,
        frequency_hz=FREQUENCY_HZ,
        spec=_spec(
            feed_line=line,
            matching_network=network,
            matching_network_position=MatchingNetworkPosition.FEEDPOINT,
        ),
    )
    shack = link_budget(
        antenna_impedance_ohm=load,
        frequency_hz=FREQUENCY_HZ,
        spec=_spec(
            feed_line=line,
            matching_network=network,
            matching_network_position=MatchingNetworkPosition.SHACK,
        ),
    )

    assert shack.feed_line_loss_db > feedpoint.feed_line_loss_db
    assert shack.transducer_gain_db < feedpoint.transducer_gain_db


def test_lossy_matching_network_adds_insertion_loss() -> None:
    load = complex(100.0, 0.0)
    network = design_l_network(load, FREQUENCY_HZ)
    assert network is not None
    network = replace(network, q_factor=50.0)
    budget = link_budget(
        antenna_impedance_ohm=load,
        frequency_hz=FREQUENCY_HZ,
        spec=_spec(matching_network=network),
    )

    assert budget.network_loss_db > 0.0
    assert budget.transducer_gain_db < 0.0
