# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""NEC2C completion checks for the high-frequency matrix priority cases."""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from antennadesk.application.use_cases.run_simulation import (
    RunSimulation,
    RunSimulationCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import discone_parameters
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.common.units import wavelength_m
from antennadesk.domain.design.yagi_reference import dl6wu_elements
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_model,
)
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.discretization import resolve_model_quality
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


def _moxon(frequency_hz: float) -> AntennaModel:
    scale = 14_170_000.0 / frequency_hz
    depth = 9.57 * 0.3048 * scale
    reflector_tip = 4.85 * 0.3048 * scale
    driven_tip = 4.00 * 0.3048 * scale
    gap = depth - reflector_tip - driven_tip
    return MoxonParameters(
        frequency_hz=frequency_hz,
        width_m=25.00 * 0.3048 * scale,
        depth_m=depth,
        reflector_tip_m=reflector_tip,
        driven_tip_m=driven_tip,
        height_m=1.0,
        wire_radius_m=gap / 5.0,
    ).to_antenna(name="Moxon HF matrix")


def _yagi(frequency_hz: float, element_count: int = 5) -> AntennaModel:
    wavelength = wavelength_m(frequency_hz)
    radius = min(0.0003, 0.002 * 432_000_000.0 / frequency_hz)
    return YagiParameters(
        frequency_hz=frequency_hz,
        elements=tuple(
            YagiElement(
                position_m=spacing * wavelength,
                length_m=length * wavelength,
                radius_m=radius,
            )
            for length, spacing in dl6wu_elements(element_count)
        ),
        height_m=1.0,
        driven_index=1,
    ).to_antenna(name="Yagi HF matrix")


def _quad(frequency_hz: float) -> AntennaModel:
    return quad_beam_parameters(
        frequency_hz=frequency_hz,
        element_count=3,
        height_m=0.5,
        wire_radius_m=0.0003,
    ).to_antenna(name="Quad HF matrix")


def _discone(frequency_hz: float) -> AntennaModel:
    return discone_parameters(
        frequency_hz=frequency_hz,
        base_height_m=0.5,
        disc_gap_m=0.001,
        wire_radius_m=0.00025,
    ).to_antenna(name="Discone HF matrix")


def _biquad(frequency_hz: float) -> AntennaModel:
    return biquad_parameters(
        BiquadKind.SINGLE,
        frequency_hz=frequency_hz,
        base_height_m=0.25,
        wire_radius_m=0.0003,
    ).to_antenna(name="Biquad HF matrix")


def _dipole(frequency_hz: float) -> AntennaModel:
    return DipoleParameters(
        frequency_hz=frequency_hz,
        total_length_m=0.468 * wavelength_m(frequency_hz),
        height_m=1.0,
        wire_radius_m=0.0006,
    ).to_antenna(name="Dipole HF matrix")


def _vertical(frequency_hz: float) -> AntennaModel:
    return VerticalParameters(
        frequency_hz=frequency_hz,
        height_m=0.25 * wavelength_m(frequency_hz),
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=0.25 * wavelength_m(frequency_hz),
        wire_radius_m=0.0004,
    ).to_antenna(name="Vertical HF matrix")


@pytest.mark.parametrize(
    ("builder", "frequency_hz"),
    [
        (_moxon, 2_400_000_000.0),
        (_yagi, 2_400_000_000.0),
        (_yagi, 5_800_000_000.0),
        (_quad, 2_400_000_000.0),
        (_discone, 1_296_000_000.0),
        (_biquad, 2_400_000_000.0),
        (_dipole, 144_000_000.0),
        (_vertical, 435_000_000.0),
    ],
    ids=[
        "moxon-2.4GHz",
        "yagi-2.4GHz",
        "yagi-5.8GHz",
        "quad-2.4GHz",
        "discone-1.296GHz",
        "biquad-2.4GHz",
        "dipole-144MHz",
        "vertical-435MHz",
    ],
)
def test_high_frequency_matrix_design_completes_in_nec2c(
    solver: Nec2cSolver,
    builder,
    frequency_hz: float,
) -> None:
    model = builder(frequency_hz)
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )

    quality = resolve_model_quality(model, spec, supports_extended_kernel=True)
    assert quality.blocking_codes == ()

    result = RunSimulation(solver).execute(RunSimulationCommand(model=model, spec=quality.spec))

    assert result.frequencies
    impedance = result.frequencies[0].impedance_ohm
    assert math.isfinite(impedance.real)
    assert math.isfinite(impedance.imag)
    assert impedance.real > 0.0
