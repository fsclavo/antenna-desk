# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real NEC2C run with more than one driven source."""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.feed import FeedPoint, Source
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.environment.environment import Environment
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


def test_two_sources_complete_a_pattern_run() -> None:
    frequency_hz = 14_100_000.0
    first = Wire(
        "first",
        Point3D(0.0, -5.0, 10.0),
        Point3D(10.0, -5.0, 10.0),
        0.001,
        COPPER,
    )
    second = Wire(
        "second",
        Point3D(0.0, 5.0, 10.0),
        Point3D(10.0, 5.0, 10.0),
        0.001,
        COPPER,
    )
    model = AntennaModel(
        name="two-source array",
        design_frequency_hz=frequency_hz,
        wires=(first, second),
        feed=FeedPoint("first", 5.0),
        sources=(Source("second", 5.0, amplitude=0.5, phase_deg=90.0),),
        environment=Environment(ground=GroundModel.free_space()),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=SegmentationPolicy(segments_per_wire=9),
        far_field=FarFieldRequest(
            enabled=True,
            theta_count=9,
            phi_count=17,
        ),
    )

    result = Nec2cSolver(Path(os.environ["NEC2C"])).run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 1
    point = result.frequencies[0]
    assert math.isfinite(point.impedance_ohm.real)
    assert point.currents
    assert point.far_field
    assert result.raw_input.count("EX 0 ") == 2
    assert len(point.source_results) == 2
    assert point.source_results[0].wire_id == "first"
    assert point.source_results[1].wire_id == "second"
    assert point.source_results[1].phase_deg == pytest.approx(90.0)
    assert point.source_results[1].amplitude == pytest.approx(0.5)
