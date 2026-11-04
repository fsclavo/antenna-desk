# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Analytical oracles for canonical antennas.

FDTD or FEM would be the ideal different-method oracle, but no engine is
available in this environment. These tests use published closed forms instead:
they are independent of the moment method and catch formulation or
normalization errors in the small-antenna and half-wave limits.

Sources: Constantine A. Balanis, *Antenna Theory: Analysis and Design*,
4th edition, Chapters 4 (dipoles) and 5 (loops).
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.environment.ground import GroundModel
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

FREQUENCY_HZ = 14_100_000.0
WAVELENGTH_M = 299_792_458.0 / FREQUENCY_HZ


def _run(model, *, segments: int, far_field: bool = True):
    assert NEC2C is not None
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(FREQUENCY_HZ),
        segmentation=SegmentationPolicy(segments_per_wire=segments),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=far_field,
            theta_count=37,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=73,
        ),
    )
    return Nec2cSolver(Path(NEC2C)).run(model, spec)


def _dipole(length_m: float):
    return DipoleParameters(
        frequency_hz=FREQUENCY_HZ,
        total_length_m=length_m,
        height_m=0.0,
        wire_radius_m=0.001,
        ground=GroundModel.free_space(),
    ).to_antenna()


def test_short_dipole_radiation_resistance_matches_the_analytical_formula() -> None:
    length_m = 0.05 * WAVELENGTH_M
    result = _run(_dipole(length_m), segments=21, far_field=False)

    impedance = result.frequencies[0].impedance_ohm
    expected = 20.0 * math.pi**2 * (length_m / WAVELENGTH_M) ** 2

    assert impedance.real == pytest.approx(expected, rel=0.03)


def test_short_dipole_directivity_matches_the_analytical_value() -> None:
    result = _run(_dipole(0.05 * WAVELENGTH_M), segments=21)

    assert result.max_total_gain_db == pytest.approx(10.0 * math.log10(1.5), abs=0.05)


def test_small_loop_radiation_resistance_matches_the_analytical_formula() -> None:
    # A 16-sided polygon at C = 0.1 lambda. The uniform-current formula is an
    # approximation at this size; the observed difference is about 12%.
    sides = 16
    circumference_m = 0.1 * WAVELENGTH_M
    area_m2 = circumference_m**2 / (4.0 * sides * math.tan(math.pi / sides))
    expected = 31_171.0 * (area_m2 / WAVELENGTH_M**2) ** 2
    model = LoopParameters(
        frequency_hz=FREQUENCY_HZ,
        circumference_m=circumference_m,
        height_m=0.0,
        sides=sides,
        wire_radius_m=0.001,
        ground=GroundModel.free_space(),
    ).to_antenna()

    result = _run(model, segments=10, far_field=False)

    assert result.frequencies[0].impedance_ohm.real == pytest.approx(expected, rel=0.15)


def test_half_wave_dipole_directivity_matches_the_analytical_value() -> None:
    result = _run(_dipole(0.5 * WAVELENGTH_M), segments=31)

    assert result.max_total_gain_db == pytest.approx(10.0 * math.log10(1.643), abs=0.1)
