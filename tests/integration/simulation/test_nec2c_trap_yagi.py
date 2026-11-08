# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real NEC2C run with a trapped Yagi."""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters
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


def test_trap_yagi_completes_a_two_band_sweep() -> None:
    parameters = trap_yagi_parameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        element_count=3,
        driven_length_m=20.0,
        reflector_spacing_m=4.0,
        director_spacing_m=3.0,
        trap_inset_m=3.0,
        trap_frequency_hz=14_100_000.0,
        ground=GroundModel.free_space(),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(
            parameters.frequency_hz,
            parameters.high_band_frequency_hz,
            5,
        ),
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
    assert len(result.frequencies) == 5
    for point in result.frequencies:
        assert math.isfinite(point.impedance_ohm.real)
        assert math.isfinite(point.impedance_ohm.imag)
        assert point.currents
    assert result.raw_input.count("EX 0 ") == 1
    assert result.raw_input.count("LD 1 ") == 6
