# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real NEC2C antenna Y-matrix and N-port feed-network cross-check."""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from antennadesk.application.feed_network_y import extract_antenna_y_matrix
from antennadesk.domain.antennas.feed_network import (
    NPortNetwork,
    TransmissionLineBranch,
    n_way_wilkinson,
    solve_feed_network,
    two_way_wilkinson,
)
from antennadesk.domain.antennas.matching_network import design_l_network
from antennadesk.domain.antennas.stacked_yagi import (
    StackedYagiFeed,
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.common.reflection import calculate_swr
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.solver import Nec2cSolver

NEC2C = os.environ.get("NEC2C")
pytestmark = [
    pytest.mark.solver,
    pytest.mark.science,
    pytest.mark.skipif(
        not NEC2C or not Path(NEC2C).is_file(),
        reason="NEC2C must point to a nec2c executable",
    ),
]

FREQUENCY_HZ = 14_100_000.0


def _stack() -> StackedYagiParameters:
    return StackedYagiParameters(
        yagi=YagiParameters(
            frequency_hz=FREQUENCY_HZ,
            elements=(
                YagiElement(position_m=0.0, length_m=10.2, radius_m=0.001),
                YagiElement(position_m=2.1, length_m=9.8, radius_m=0.001),
            ),
            height_m=10.0,
        ),
        count=2,
        spacing_m=10.6,
        phase_step_deg=180.0,
    )


def _spec(*, co_simulate: bool) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(FREQUENCY_HZ),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=FarFieldRequest(enabled=False),
        co_simulate_feed_network=co_simulate,
        include_conductor_losses=False,
    )


def _network_stack() -> StackedYagiParameters:
    base = _stack()
    return StackedYagiParameters(
        yagi=base.yagi,
        count=base.count,
        spacing_m=base.spacing_m,
        phase_step_deg=base.phase_step_deg,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.NETWORK,
            reference_length_m=2.0,
            line_increment_m=2.65,
            velocity_factor=0.8,
            characteristic_impedance_ohm=75.0,
        ),
    )


def test_y_matrix_matches_the_nec_co_simulated_line_network() -> None:
    solver = Nec2cSolver(Path(os.environ["NEC2C"]))
    antenna_y = extract_antenna_y_matrix(
        solver,
        _stack().to_antenna(),
        _spec(co_simulate=False),
    )

    assert antenna_y.ports == (
        ("level-1-element-2", 4.9),
        ("level-2-element-2", 4.9),
    )
    assert antenna_y.matrix[0][1] == pytest.approx(antenna_y.matrix[1][0])
    assert antenna_y.matrix[0][1].real > 0.0

    feed = NPortNetwork(
        port_names=("input", "level-1", "level-2"),
        branches=(
            TransmissionLineBranch(0, 1, 75.0, 2.0, 0.8),
            TransmissionLineBranch(0, 2, 75.0, 4.65, 0.8),
        ),
    )
    solution = solve_feed_network(
        feed,
        antenna_y.matrix,
        frequency_hz=FREQUENCY_HZ,
    )
    network_result = solver.run(
        _network_stack().to_antenna(),
        _spec(co_simulate=True),
    )

    assert network_result.status.value == "completed"
    point = network_result.frequencies[0]
    assert solution.input_impedance_ohm == pytest.approx(
        point.impedance_ohm,
        abs=0.01,
    )
    level_powers = {
        source.wire_id: max(0.0, source.power_w)
        for source in point.source_results
        if source.wire_id.startswith("level-")
    }
    assert len(level_powers) == 2
    network_ratio = level_powers["level-2-element-2"] / level_powers["level-1-element-2"]
    solver_ratio = solution.antenna_port_powers_w[1] / solution.antenna_port_powers_w[0]
    assert solver_ratio == pytest.approx(network_ratio, rel=1e-3)


def test_wilkinson_feed_network_with_the_real_antenna_y_matrix() -> None:
    solver = Nec2cSolver(Path(os.environ["NEC2C"]))
    antenna_y = extract_antenna_y_matrix(
        solver,
        _stack().to_antenna(),
        _spec(co_simulate=False),
    )
    solution = solve_feed_network(
        two_way_wilkinson(frequency_hz=FREQUENCY_HZ),
        antenna_y.matrix,
        frequency_hz=FREQUENCY_HZ,
        source_current_a=1.0,
    )

    assert math.isfinite(solution.input_impedance_ohm.real)
    assert math.isfinite(solution.input_impedance_ohm.imag)
    assert solution.input_power_w > 0.0
    assert solution.network_loss_w >= 0.0
    assert solution.input_power_w == pytest.approx(
        sum(solution.antenna_port_powers_w) + solution.network_loss_w,
        rel=1e-12,
    )


def test_per_level_matching_improves_the_real_antenna_input_match() -> None:
    solver = Nec2cSolver(Path(os.environ["NEC2C"]))
    antenna_y = extract_antenna_y_matrix(
        solver,
        _stack().to_antenna(),
        _spec(co_simulate=False),
    )
    port_impedance = 1.0 / antenna_y.matrix[0][0]
    matching = design_l_network(
        port_impedance,
        FREQUENCY_HZ,
        source_impedance_ohm=50.0,
    )
    assert matching is not None

    base = n_way_wilkinson(
        frequency_hz=FREQUENCY_HZ,
        port_count=2,
        feed_line_lengths_m=(2.0, 2.0),
    )
    matched = n_way_wilkinson(
        frequency_hz=FREQUENCY_HZ,
        port_count=2,
        feed_line_lengths_m=(2.0, 2.0),
        level_matching_network=matching,
    )
    base_solution = solve_feed_network(
        base,
        antenna_y.matrix,
        frequency_hz=FREQUENCY_HZ,
    )
    matched_solution = solve_feed_network(
        matched,
        antenna_y.matrix,
        frequency_hz=FREQUENCY_HZ,
    )

    base_swr = calculate_swr(base_solution.input_impedance_ohm, 50.0)
    matched_swr = calculate_swr(matched_solution.input_impedance_ohm, 50.0)
    assert matched_swr < base_swr
    assert matched_swr < 1.2
    assert matched_solution.antenna_port_powers_w[0] == pytest.approx(
        matched_solution.antenna_port_powers_w[1],
        rel=1e-6,
    )
    assert matched_solution.input_power_w == pytest.approx(
        sum(matched_solution.antenna_port_powers_w) + matched_solution.network_loss_w,
        rel=1e-9,
    )
    assert matched_solution.antenna_port_voltages_v != base_solution.antenna_port_voltages_v
