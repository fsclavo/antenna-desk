# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""The cliff/second-medium profile changes patterns but not impedance."""

from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path

import pytest

from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.environment.site_ground import EdgeShape, SiteGroundProfile
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


def test_cliff_profile_changes_far_field_but_not_impedance(
    solver: Nec2cSolver,
) -> None:
    model = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.0,
        wire_radius_m=0.002,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    ).to_antenna(name="10 m monopole")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=19,
            phi_start_deg=0.0,
            phi_stop_deg=0.0,
            phi_count=1,
        ),
    )
    site = SiteGroundProfile(
        second_medium_relative_permittivity=81.0,
        second_medium_conductivity_s_per_m=5.0,
        edge_distance_m=0.0,
        edge_shape=EdgeShape.CIRCULAR,
        edge_height_m=0.0,
        label="Water at the antenna",
    )

    flat = solver.run(model, spec)
    cliff = solver.run(model, replace(spec, site_ground=site))

    flat_frequency = flat.frequencies[0]
    cliff_frequency = cliff.frequencies[0]
    assert cliff_frequency.impedance_ohm == pytest.approx(
        flat_frequency.impedance_ohm,
        rel=0.0,
        abs=1e-6,
    )
    assert cliff_frequency.swr == pytest.approx(flat_frequency.swr, rel=0.0, abs=1e-9)

    flat_gain = {point.theta_deg: point.gain_total_db for point in flat_frequency.far_field}
    cliff_gain = {point.theta_deg: point.gain_total_db for point in cliff_frequency.far_field}
    differences = [
        abs(cliff_gain[theta] - flat_gain[theta])
        for theta in flat_gain.keys() & cliff_gain.keys()
        if cliff_gain[theta] is not None and flat_gain[theta] is not None
    ]
    assert differences
    assert max(differences) > 0.1
