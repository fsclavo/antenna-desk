# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Invalid passive results are reported instead of being marked complete."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationStatus
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


def test_negative_input_resistance_is_reported(solver: Nec2cSolver) -> None:
    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=9.0,
        base_height_m=0.25,
        radial_count=14,
        radial_length_m=12.863,
        wire_radius_m=0.001,
        material=COPPER,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
        loading_coil_enabled=True,
        loading_coil_inductance_h=10e-6,
        top_hat_enabled=True,
        top_hat_radius_m=0.5,
        top_hat_wire_count=4,
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        far_field=FarFieldRequest(
            theta_count=3,
            theta_stop_deg=90.0,
            phi_count=3,
            phi_stop_deg=360.0,
        ),
        pattern_frequencies_hz=(7_100_000.0,),
        timeout_s=60.0,
    )

    result = solver.run(parameters.to_antenna(), spec)

    assert result.status is SimulationStatus.ERROR
    assert result.frequencies[0].impedance_ohm.real < 0.0
    diagnostic = next(
        item for item in result.diagnostics if item.code == "normalization.negative_resistance"
    )
    assert diagnostic.severity.value == "error"
