# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""N-port feed-network solver tests."""

from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.feed_network import (
    NPortNetwork,
    TransmissionLineBranch,
    TwoPortBranch,
    n_way_wilkinson,
    solve_feed_network,
    two_way_wilkinson,
)
from antennadesk.domain.antennas.matching_network import (
    design_l_network,
    design_pi_network,
    design_t_network,
)

FREQUENCY_HZ = 14_100_000.0
SPEED_OF_LIGHT = 299_792_458.0


def _wilkinson_s() -> list[list[complex]]:
    network = two_way_wilkinson(frequency_hz=FREQUENCY_HZ)
    return network.s_matrix(FREQUENCY_HZ)


def test_two_way_wilkinson_s_matrix_is_ideal() -> None:
    s = _wilkinson_s()

    assert s[0][0] == pytest.approx(0.0, abs=1e-12)
    assert s[1][1] == pytest.approx(0.0, abs=1e-12)
    assert s[2][2] == pytest.approx(0.0, abs=1e-12)
    assert s[1][2] == pytest.approx(0.0, abs=1e-12)
    assert s[2][1] == pytest.approx(0.0, abs=1e-12)
    assert abs(s[1][0]) == pytest.approx(1.0 / math.sqrt(2.0))
    assert abs(s[2][0]) == pytest.approx(1.0 / math.sqrt(2.0))
    assert s[1][0] == pytest.approx(-1j / math.sqrt(2.0))
    assert s[2][0] == pytest.approx(-1j / math.sqrt(2.0))
    assert s[1][0] == pytest.approx(s[2][0])
    assert s[0][1] == pytest.approx(s[1][0])
    assert s[0][2] == pytest.approx(s[2][0])


def test_two_way_wilkinson_matches_scikit_rf() -> None:
    skrf = pytest.importorskip("skrf")
    from skrf.circuit import Circuit

    frequency = skrf.Frequency.from_f([FREQUENCY_HZ], unit="Hz")
    media = skrf.media.DefinedGammaZ0(
        frequency,
        z0=50.0,
        gamma=1j * math.tau * FREQUENCY_HZ / SPEED_OF_LIGHT,
    )
    length = SPEED_OF_LIGHT / FREQUENCY_HZ / 4.0
    line_1 = media.line(d=length, unit="m", z0=70.71067811865476)
    line_1.name = "line-1"
    line_2 = media.line(d=length, unit="m", z0=70.71067811865476)
    line_2.name = "line-2"
    port_0 = Circuit.Port(frequency, "input")
    port_1 = Circuit.Port(frequency, "output-1")
    port_2 = Circuit.Port(frequency, "output-2")
    isolation = Circuit.SeriesImpedance(frequency, 100.0, "isolation")
    circuit = Circuit(
        [
            [(port_0, 0), (line_1, 0), (line_2, 0)],
            [(line_1, 1), (port_1, 0), (isolation, 0)],
            [(line_2, 1), (port_2, 0), (isolation, 1)],
        ]
    )
    reference = circuit.s_external[0]
    ours = _wilkinson_s()

    for row in range(3):
        for column in range(3):
            assert ours[row][column] == pytest.approx(
                reference[row, column],
                abs=1e-9,
            )


def test_single_line_into_a_matched_load_is_matched() -> None:
    quarter = SPEED_OF_LIGHT / FREQUENCY_HZ / 4.0
    network = NPortNetwork(
        port_names=("input", "output"),
        branches=(
            TransmissionLineBranch(
                node_a=0,
                node_b=1,
                characteristic_impedance_ohm=50.0,
                length_m=quarter,
            ),
        ),
    )

    solution = solve_feed_network(
        network,
        [[1.0 / 50.0 + 0.0j]],
        frequency_hz=FREQUENCY_HZ,
    )

    assert solution.input_impedance_ohm == pytest.approx(50.0 + 0.0j, abs=1e-9)
    assert solution.antenna_port_powers_w[0] == pytest.approx(
        solution.input_power_w,
        rel=1e-12,
    )


def test_quarter_wave_transformer_impedance() -> None:
    quarter = SPEED_OF_LIGHT / FREQUENCY_HZ / 4.0
    network = NPortNetwork(
        port_names=("input", "output"),
        branches=(
            TransmissionLineBranch(
                node_a=0,
                node_b=1,
                characteristic_impedance_ohm=70.71067811865476,
                length_m=quarter,
            ),
        ),
    )

    solution = solve_feed_network(
        network,
        [[1.0 / 50.0 + 0.0j]],
        frequency_hz=FREQUENCY_HZ,
    )

    assert solution.input_impedance_ohm == pytest.approx(100.0 + 0.0j, abs=1e-9)


def test_wilkinson_with_matched_loads_has_no_extra_loss() -> None:
    network = two_way_wilkinson(frequency_hz=FREQUENCY_HZ)
    load = [[1.0 / 50.0 + 0.0j, 0.0j], [0.0j, 1.0 / 50.0 + 0.0j]]

    solution = solve_feed_network(
        network,
        load,
        frequency_hz=FREQUENCY_HZ,
        source_current_a=1.0,
    )

    assert solution.input_impedance_ohm == pytest.approx(50.0 + 0.0j, abs=1e-9)
    assert solution.input_power_w == pytest.approx(25.0, rel=1e-12)
    assert solution.antenna_port_powers_w[0] == pytest.approx(12.5, rel=1e-12)
    assert solution.antenna_port_powers_w[1] == pytest.approx(12.5, rel=1e-12)
    assert solution.network_loss_w == pytest.approx(0.0, abs=1e-9)


def test_wilkinson_power_balance_with_mismatched_loads() -> None:
    network = two_way_wilkinson(frequency_hz=FREQUENCY_HZ)
    load = [[1.0 / 50.0 + 0.0j, 0.0j], [0.0j, 1.0 / 100.0 + 0.0j]]

    solution = solve_feed_network(
        network,
        load,
        frequency_hz=FREQUENCY_HZ,
        source_current_a=1.0,
    )

    delivered = sum(solution.antenna_port_powers_w)
    assert solution.network_loss_w > 0.0
    assert solution.input_power_w == pytest.approx(
        delivered + solution.network_loss_w,
        rel=1e-12,
    )


@pytest.mark.parametrize("port_count", [2, 3, 4])
def test_n_way_wilkinson_is_matched_and_splits_equally(port_count: int) -> None:
    quarter = SPEED_OF_LIGHT / FREQUENCY_HZ / 4.0
    network = n_way_wilkinson(
        frequency_hz=FREQUENCY_HZ,
        port_count=port_count,
        feed_line_lengths_m=(quarter,) * port_count,
    )
    s = network.s_matrix(FREQUENCY_HZ)

    assert s[0][0] == pytest.approx(0.0, abs=1e-5)
    for output in range(1, port_count + 1):
        assert s[output][output] == pytest.approx(0.0, abs=1e-5)
        assert abs(s[output][0]) == pytest.approx(1.0 / math.sqrt(port_count), abs=1e-5)
        for other in range(1, port_count + 1):
            if other != output:
                assert s[output][other] == pytest.approx(0.0, abs=1e-5)

    load = [[0.0j for _ in range(port_count)] for _ in range(port_count)]
    for index in range(port_count):
        load[index][index] = 1.0 / 50.0 + 0.0j
    solution = solve_feed_network(
        network,
        load,
        frequency_hz=FREQUENCY_HZ,
        source_current_a=1.0,
    )

    assert solution.input_impedance_ohm == pytest.approx(50.0 + 0.0j, abs=0.01)
    for power in solution.antenna_port_powers_w:
        assert power == pytest.approx(solution.input_power_w / port_count, rel=1e-5)
    assert solution.network_loss_w == pytest.approx(0.0, abs=1e-4)


@pytest.mark.parametrize(
    "network_factory",
    [
        lambda: design_l_network(100.0 + 0.0j, FREQUENCY_HZ, source_impedance_ohm=50.0),
        lambda: design_pi_network(
            100.0 + 0.0j,
            FREQUENCY_HZ,
            source_impedance_ohm=50.0,
            loaded_q=3.0,
        ),
        lambda: design_t_network(
            100.0 + 0.0j,
            FREQUENCY_HZ,
            source_impedance_ohm=50.0,
            loaded_q=3.0,
        ),
    ],
)
def test_level_matching_branch_transforms_a_100_ohm_load(network_factory) -> None:
    matching = network_factory()
    assert matching is not None
    quarter = SPEED_OF_LIGHT / FREQUENCY_HZ / 4.0
    feed = NPortNetwork(
        port_names=("input", "output"),
        branches=(
            TransmissionLineBranch(0, 2, 50.0, quarter),
            TwoPortBranch(2, 1, matching),
        ),
        internal_node_count=1,
    )

    solution = solve_feed_network(
        feed,
        [[1.0 / 100.0 + 0.0j]],
        frequency_hz=FREQUENCY_HZ,
    )

    assert solution.input_impedance_ohm == pytest.approx(50.0 + 0.0j, abs=1e-6)
    assert solution.antenna_port_powers_w[0] == pytest.approx(
        solution.input_power_w,
        rel=1e-6,
    )


def test_n_way_wilkinson_with_level_matching_is_matched_and_splits_equally() -> None:
    matching = design_l_network(
        100.0 + 0.0j,
        FREQUENCY_HZ,
        source_impedance_ohm=50.0,
    )
    assert matching is not None
    network = n_way_wilkinson(
        frequency_hz=FREQUENCY_HZ,
        port_count=2,
        feed_line_lengths_m=(0.01, 0.01),
        level_matching_network=matching,
    )
    load = [[0.01 + 0.0j, 0.0j], [0.0j, 0.01 + 0.0j]]

    solution = solve_feed_network(
        network,
        load,
        frequency_hz=FREQUENCY_HZ,
        source_current_a=1.0,
    )

    assert solution.input_impedance_ohm == pytest.approx(50.0 + 0.0j, abs=0.001)
    for power in solution.antenna_port_powers_w:
        assert power == pytest.approx(solution.input_power_w / 2.0, rel=1e-4)
    assert solution.network_loss_w == pytest.approx(0.0, abs=1e-4)


def test_n_way_wilkinson_supports_a_different_network_per_level() -> None:
    matching_100 = design_l_network(
        100.0 + 0.0j,
        FREQUENCY_HZ,
        source_impedance_ohm=50.0,
    )
    matching_25 = design_l_network(
        25.0 + 0.0j,
        FREQUENCY_HZ,
        source_impedance_ohm=50.0,
    )
    assert matching_100 is not None
    assert matching_25 is not None
    network = n_way_wilkinson(
        frequency_hz=FREQUENCY_HZ,
        port_count=2,
        feed_line_lengths_m=(0.01, 0.01),
        level_matching_networks=(matching_100, matching_25),
    )

    solution = solve_feed_network(
        network,
        [[0.01 + 0.0j, 0.0j], [0.0j, 0.04 + 0.0j]],
        frequency_hz=FREQUENCY_HZ,
        source_current_a=1.0,
    )

    assert solution.input_impedance_ohm == pytest.approx(50.0 + 0.0j, abs=0.001)
    for power in solution.antenna_port_powers_w:
        assert power == pytest.approx(solution.input_power_w / 2.0, rel=1e-4)
    assert solution.network_loss_w == pytest.approx(0.0, abs=1e-4)


def test_n_way_wilkinson_rejects_ambiguous_or_incomplete_level_networks() -> None:
    matching = design_l_network(100.0 + 0.0j, FREQUENCY_HZ, source_impedance_ohm=50.0)
    assert matching is not None

    with pytest.raises(ValueError, match="not both"):
        n_way_wilkinson(
            frequency_hz=FREQUENCY_HZ,
            port_count=2,
            feed_line_lengths_m=(0.01, 0.01),
            level_matching_network=matching,
            level_matching_networks=(matching, matching),
        )
    with pytest.raises(ValueError, match="one entry per output"):
        n_way_wilkinson(
            frequency_hz=FREQUENCY_HZ,
            port_count=2,
            feed_line_lengths_m=(0.01, 0.01),
            level_matching_networks=(matching,),
        )


def test_n_way_wilkinson_supports_an_unmatched_level_between_matched_levels() -> None:
    matching = design_l_network(100.0 + 0.0j, FREQUENCY_HZ, source_impedance_ohm=50.0)
    assert matching is not None
    network = n_way_wilkinson(
        frequency_hz=FREQUENCY_HZ,
        port_count=2,
        feed_line_lengths_m=(0.01, 0.01),
        level_matching_networks=(matching, None),
    )

    solution = solve_feed_network(
        network,
        [[0.01 + 0.0j, 0.0j], [0.0j, 0.02 + 0.0j]],
        frequency_hz=FREQUENCY_HZ,
        source_current_a=1.0,
    )

    assert math.isfinite(solution.input_impedance_ohm.real)
    assert math.isfinite(solution.input_impedance_ohm.imag)
    assert len(solution.antenna_port_powers_w) == 2
    assert sum(solution.antenna_port_powers_w) <= solution.input_power_w + 1e-9
