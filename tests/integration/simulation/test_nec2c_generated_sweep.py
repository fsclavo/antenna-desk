# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""NEC2C smoke check for the generated 100-point single-design sweep."""

from __future__ import annotations

import math
import os
import time
from pathlib import Path

import pytest

from antennadesk.application.use_cases.run_simulation import (
    RunSimulation,
    RunSimulationCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
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


def test_generated_100_point_sweep_completes_in_nec2c(
    solver: Nec2cSolver,
) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6_700_000.0, 7_500_000.0, 100),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )

    started = time.monotonic()
    result = RunSimulation(solver).execute(
        RunSimulationCommand(model=parameters.to_antenna(), spec=spec)
    )
    elapsed_s = time.monotonic() - started
    # Observed 2026-11-19: about 0.02 s for 100 points with this 21-segment
    # dipole on the development machine. This is a smoke bound, not a target.

    assert len(result.frequencies) == 100
    assert result.duration_s < 180.0
    assert elapsed_s < 180.0
    impedance = result.frequencies[50].impedance_ohm
    assert math.isfinite(impedance.real)
    assert math.isfinite(impedance.imag)
    assert impedance.real > 0.0
