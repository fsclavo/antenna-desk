# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real NEC2C run with a two-level stacked Yagi."""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from antennadesk.domain.antennas.stacked_yagi import (
    StackedYagiFeed,
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationStatus
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


def test_stacked_yagi_reports_both_ports_and_a_combined_pattern() -> None:
    parameters = StackedYagiParameters(
        yagi=YagiParameters(
            frequency_hz=14_100_000.0,
            elements=(
                YagiElement(position_m=0.0, length_m=10.2, radius_m=0.001),
                YagiElement(position_m=2.1, length_m=9.8, radius_m=0.001),
            ),
            height_m=10.0,
            ground=GroundModel.perfect(),
        ),
        count=2,
        spacing_m=10.6,
        phase_step_deg=180.0,
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=FarFieldRequest(
            enabled=True,
            theta_count=9,
            phi_count=17,
        ),
    )

    result = Nec2cSolver(Path(os.environ["NEC2C"])).run(
        parameters.to_antenna(),
        spec,
    )

    assert result.status is SimulationStatus.COMPLETED
    point = result.frequencies[0]
    assert math.isfinite(point.impedance_ohm.real)
    assert math.isfinite(point.impedance_ohm.imag)
    assert len(point.source_results) == 2
    assert all(math.isfinite(source.power_w) for source in point.source_results)
    assert point.far_field
    assert result.raw_input.count("EX 0 ") == 2


def test_stacked_yagi_network_mode_co_simulates_every_tl_port() -> None:
    parameters = StackedYagiParameters(
        yagi=YagiParameters(
            frequency_hz=14_100_000.0,
            elements=(
                YagiElement(position_m=0.0, length_m=10.2, radius_m=0.001),
                YagiElement(position_m=2.1, length_m=9.8, radius_m=0.001),
            ),
            height_m=10.0,
            ground=GroundModel.perfect(),
        ),
        count=3,
        spacing_m=10.6,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.NETWORK,
            reference_length_m=2.0,
            line_increment_m=2.65,
            velocity_factor=0.8,
            characteristic_impedance_ohm=75.0,
            splitter_loss_db=0.4,
        ),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=FarFieldRequest(
            enabled=True,
            theta_count=9,
            phi_count=17,
        ),
        feed_network_loss_db=parameters.feed.splitter_loss_db,
        co_simulate_feed_network=True,
    )

    result = Nec2cSolver(Path(os.environ["NEC2C"])).run(
        parameters.to_antenna(),
        spec,
    )

    assert result.status is SimulationStatus.COMPLETED
    point = result.frequencies[0]
    assert math.isfinite(point.impedance_ohm.real)
    assert len(point.source_results) == 4
    level_prefixes = {
        source.wire_id.split("-")[1]
        for source in point.source_results
        if source.wire_id.startswith("level-")
    }
    assert level_prefixes == {"1", "2", "3"}
    assert point.source_results[0].wire_id == "splitter-node"
    assert all(math.isfinite(source.power_w) for source in point.source_results)
    assert point.far_field
    assert result.raw_input.count("TL ") == 3
