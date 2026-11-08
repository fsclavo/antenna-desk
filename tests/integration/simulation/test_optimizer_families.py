# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Family optimizer smoke tests against the real NEC-2 engine."""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from antennadesk.application.use_cases.optimize_antenna import (
    OptimizeAntenna,
    OptimizeAntennaCommand,
)
from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import discone_parameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters
from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
from antennadesk.domain.antennas.scv import ScvKind, scv_parameters
from antennadesk.domain.antennas.transmission_line_doublet import (
    DoubletPreset,
    doublet_starting_parameters,
)
from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.antennas.zepp import zepp_starting_parameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.optimization.descriptor import FamilyOptimizationObjective
from antennadesk.domain.optimization.engine import OptimizationBudget
from antennadesk.domain.optimization.registry import optimizer_availability
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


def _samples() -> list[object]:
    return [
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
        VerticalParameters(
            frequency_hz=7_100_000.0,
            height_m=5.0,
            base_height_m=0.25,
            radial_count=4,
            radial_length_m=2.5,
            top_hat_enabled=True,
            top_hat_radius_m=0.75,
            top_hat_wire_count=4,
        ),
        InvertedVParameters(
            frequency_hz=7_100_000.0,
            leg_length_m=10.0,
            apex_height_m=12.0,
        ),
        LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
            sides=4,
        ),
        EndFedParameters(frequency_hz=7_100_000.0, length_m=20.0),
        scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0),
        biquad_parameters(BiquadKind.SINGLE),
        beverage_parameters(
            frequency_hz=7_100_000.0,
            length_m=42.0,
            ground=GroundModel.finite(
                relative_permittivity=13.0,
                conductivity_s_per_m=0.005,
            ),
        ),
        loaded_dipole_parameters(
            frequency_hz=7_100_000.0,
            total_length_m=18.0,
            link_offset_m=2.5,
        ),
        discone_parameters(
            frequency_hz=145_000_000.0,
            cone_height_m=0.5,
            cone_radius_m=0.3,
            disc_radius_m=0.5,
            wire_count=8,
        ),
        trap_yagi_parameters(
            frequency_hz=7_100_000.0,
            high_band_frequency_hz=14_100_000.0,
            element_count=3,
            driven_length_m=20.0,
            reflector_spacing_m=4.0,
            director_spacing_m=3.0,
            trap_inset_m=3.0,
        ),
        phased_vertical_parameters(
            frequency_hz=14_100_000.0,
            element_count=2,
            height_m=5.0,
            spacing_m=5.0,
            phase_step_deg=90.0,
            radial_count=4,
            radial_length_m=5.0,
        ),
        quad_beam_parameters(
            frequency_hz=14_100_000.0,
            element_count=3,
            loop_side_m=5.0,
            reflector_spacing_m=4.0,
            director_spacing_m=3.0,
        ),
        YagiParameters(
            frequency_hz=14_100_000.0,
            elements=(
                YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
                YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
            ),
            height_m=10.0,
        ),
        MoxonParameters(
            frequency_hz=14_100_000.0,
            width_m=10.0,
            depth_m=3.0,
            reflector_tip_m=1.0,
            driven_tip_m=1.0,
            height_m=10.0,
        ),
        doublet_starting_parameters(DoubletPreset.G5RV),
        zepp_starting_parameters(),
    ]


@pytest.mark.parametrize("parameters", _samples(), ids=lambda item: type(item).__name__)
def test_family_optimizer_runs_against_nec2c(
    solver: Nec2cSolver,
    parameters: object,
) -> None:
    availability = optimizer_availability(parameters)  # type: ignore[arg-type]
    assert availability.descriptor is not None
    descriptor = availability.descriptor
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(parameters.frequency_hz),  # type: ignore[attr-defined]
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )

    result = OptimizeAntenna(solver).execute(
        OptimizeAntennaCommand(
            descriptor=descriptor,
            base_spec=spec,
            objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
            budget=OptimizationBudget(4, 4, 2),
            seed=9,
        )
    )

    assert result.best_parameters is not None
    assert result.best_score is not None
    assert math.isfinite(result.best_score)
    assert result.evaluations
