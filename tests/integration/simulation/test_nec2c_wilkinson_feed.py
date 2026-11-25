# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real NEC2C Wilkinson feed-network integration."""

from __future__ import annotations

import math
import os
from dataclasses import replace
from pathlib import Path

import pytest

from antennadesk.application.feed_network_y import extract_antenna_y_matrix
from antennadesk.application.simulation_specs import build_typed_family_simulation_spec
from antennadesk.application.wilkinson_feed import WilkinsonFeedSolver
from antennadesk.domain.antennas.feed_network import n_way_wilkinson, solve_feed_network
from antennadesk.domain.antennas.matching_network import design_l_network
from antennadesk.domain.antennas.stacked_yagi import (
    StackedYagiFeed,
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
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


def _parameters(count: int = 2) -> StackedYagiParameters:
    return StackedYagiParameters(
        yagi=YagiParameters(
            frequency_hz=FREQUENCY_HZ,
            elements=(
                YagiElement(position_m=0.0, length_m=10.2, radius_m=0.001),
                YagiElement(position_m=2.1, length_m=9.8, radius_m=0.001),
            ),
            height_m=10.0,
        ),
        count=count,
        spacing_m=10.6,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.WILKINSON,
            reference_length_m=2.0,
            line_increment_m=0.0,
            velocity_factor=0.8,
            characteristic_impedance_ohm=50.0,
            splitter_loss_db=0.2,
            line_loss_db_per_100m=1.5,
            splitter_design_frequency_hz=FREQUENCY_HZ,
        ),
    )


def test_wilkinson_wrapper_reconstructs_a_two_level_pattern() -> None:
    parameters = _parameters()
    spec = replace(
        build_typed_family_simulation_spec(parameters),
        frequency_plan=FrequencyPlan.single(FREQUENCY_HZ),
        far_field=FarFieldRequest(enabled=True, theta_count=9, phi_count=17),
    )
    base = Nec2cSolver(Path(os.environ["NEC2C"]))
    result = WilkinsonFeedSolver(base).run(parameters.to_antenna(), spec)

    assert result.status.value == "completed"
    assert len(result.frequencies) == 1
    point = result.frequencies[0]
    assert math.isfinite(point.impedance_ohm.real)
    assert math.isfinite(point.impedance_ohm.imag)
    assert math.isfinite(point.swr)
    assert point.far_field
    assert point.power_budget is None
    assert point.realized_gain_db is not None
    assert point.directivity_db is not None
    assert point.mismatch_loss_db is not None
    assert point.feed_line_loss_db is not None
    assert point.network_loss_db is not None
    assert len(point.source_results) == 2
    delivered = sum(source.power_w for source in point.source_results)
    assert delivered > 0.0
    assert delivered <= point.input_power_w + 1e-9
    diagnostics = {diagnostic.code for diagnostic in result.diagnostics}
    assert "wilkinson.pattern_reconstruction" in diagnostics
    assert "wilkinson.ideal_components" in diagnostics

    feed_spec = spec.feed_network
    assert feed_spec is not None
    antenna_spec = replace(
        spec,
        frequency_plan=FrequencyPlan.single(FREQUENCY_HZ),
        feed_network=None,
        co_simulate_feed_network=False,
    )
    antenna_y = extract_antenna_y_matrix(
        base,
        parameters.to_antenna(),
        antenna_spec,
    )
    network = n_way_wilkinson(
        frequency_hz=feed_spec.design_frequency_hz,
        port_count=feed_spec.port_count,
        feed_line_lengths_m=feed_spec.feed_line_lengths_m,
        system_impedance_ohm=feed_spec.feed_line_impedance_ohm,
        velocity_factor=feed_spec.velocity_factor,
    )
    solution = solve_feed_network(
        network,
        antenna_y.matrix,
        frequency_hz=FREQUENCY_HZ,
    )
    assert point.impedance_ohm == pytest.approx(solution.input_impedance_ohm, abs=1e-9)


def test_wilkinson_wrapper_handles_three_ports_and_a_sweep() -> None:
    parameters = _parameters(count=3)
    spec = replace(
        build_typed_family_simulation_spec(parameters),
        frequency_plan=FrequencyPlan.sweep(13.9e6, 14.3e6, 3),
        far_field=FarFieldRequest(enabled=True, theta_count=7, phi_count=13),
    )
    result = WilkinsonFeedSolver(Nec2cSolver(Path(os.environ["NEC2C"]))).run(
        parameters.to_antenna(),
        spec,
    )

    assert result.status.value == "completed"
    assert len(result.frequencies) == 3
    for point in result.frequencies:
        assert point.far_field
        assert len(point.source_results) == 3
        assert math.isfinite(point.impedance_ohm.real)
        assert point.realized_gain_db is not None
        delivered = sum(source.power_w for source in point.source_results)
        assert delivered > 0.0
        assert delivered <= point.input_power_w + 1e-9


def test_wilkinson_wrapper_with_level_matching_improves_the_input_swr() -> None:
    base_parameters = _parameters()
    base_spec = replace(
        build_typed_family_simulation_spec(base_parameters),
        frequency_plan=FrequencyPlan.single(FREQUENCY_HZ),
        far_field=FarFieldRequest(enabled=True, theta_count=9, phi_count=17),
    )
    base_solver = Nec2cSolver(Path(os.environ["NEC2C"]))
    antenna_spec = replace(
        base_spec,
        feed_network=None,
        co_simulate_feed_network=False,
    )
    antenna_y = extract_antenna_y_matrix(
        base_solver,
        base_parameters.to_antenna(),
        antenna_spec,
    )
    matching = design_l_network(
        1.0 / antenna_y.matrix[0][0],
        FREQUENCY_HZ,
        source_impedance_ohm=50.0,
    )
    assert matching is not None
    matched_parameters = replace(
        base_parameters,
        feed=replace(
            base_parameters.feed,
            level_matching_network=matching,
        ),
    )
    matched_spec = replace(
        build_typed_family_simulation_spec(matched_parameters),
        frequency_plan=FrequencyPlan.single(FREQUENCY_HZ),
        far_field=FarFieldRequest(enabled=True, theta_count=9, phi_count=17),
    )
    wrapper = WilkinsonFeedSolver(base_solver)

    base_result = wrapper.run(base_parameters.to_antenna(), base_spec)
    matched_result = wrapper.run(matched_parameters.to_antenna(), matched_spec)

    assert base_result.frequencies
    assert matched_result.frequencies
    base_point = base_result.frequencies[0]
    matched_point = matched_result.frequencies[0]
    assert matched_point.swr < base_point.swr
    assert matched_point.swr < 1.2
    assert matched_point.far_field
    assert len(matched_point.source_results) == 2
    assert matched_point.realized_gain_db is not None
