# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real NEC2C run with a quad beam."""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
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


def test_quad_beam_completes_a_pattern_run() -> None:
    parameters = quad_beam_parameters(
        frequency_hz=14_100_000.0,
        element_count=3,
        loop_side_m=5.0,
        reflector_spacing_m=4.0,
        director_spacing_m=3.0,
        height_m=2.5,
        ground=GroundModel.perfect(),
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
    assert len(result.frequencies) == 1
    point = result.frequencies[0]
    assert math.isfinite(point.impedance_ohm.real)
    assert math.isfinite(point.impedance_ohm.imag)
    assert point.currents
    assert point.far_field
    assert result.raw_input.count("EX 0 ") == 1
