# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Segmentation convergence for a half-wave dipole.

The NEC-2 User's Guide (Burke and Poggio), Part III, Section II, recommends
segments no longer than 0.1 lambda in general and 0.05 lambda in critical
regions, and warns that segments shorter than 1e-3 lambda lose accuracy
(<https://www.nec2.org/part_3/secii.html>).

This is a convergence study, not an independent numerical reference: the
expected values come from the same engine at a finer segmentation.  It
validates that the default policy is numerically stable, not that the physics
is absolutely correct.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.environment.ground import GroundModel
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

FREQUENCY_HZ = 4_800_000.0
LENGTH_M = 30.48
REFERENCE_SEGMENTS = 61


def _impedance(segments: int, *, ground: GroundModel, height_m: float) -> complex:
    assert NEC2C is not None
    parameters = DipoleParameters(
        frequency_hz=FREQUENCY_HZ,
        total_length_m=LENGTH_M,
        height_m=height_m,
        wire_radius_m=0.001,
        ground=ground,
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(FREQUENCY_HZ),
        segmentation=SegmentationPolicy(segments_per_wire=segments),
    )
    result = Nec2cSolver(Path(NEC2C)).run(parameters.to_antenna(), spec)
    return result.frequencies[0].impedance_ohm


def test_free_space_dipole_impedance_converges() -> None:
    values = {
        segments: _impedance(segments, ground=GroundModel.free_space(), height_m=0.0)
        for segments in (7, 11, 21, 31, 41, REFERENCE_SEGMENTS, 81)
    }
    reference = values[REFERENCE_SEGMENTS]

    # At 31 segments the segment is 0.016 lambda, well inside the 0.05 lambda
    # guideline.  The tolerances are the observed stability at that density.
    for segments in (31, 41, REFERENCE_SEGMENTS):
        assert values[segments].real == pytest.approx(reference.real, abs=0.1)
        assert values[segments].imag == pytest.approx(reference.imag, abs=0.25)

    assert abs(values[21] - reference) / abs(reference) <= 0.01

    # Refining past the reference must not move the result further away.
    assert abs(values[81].real - reference.real) <= abs(values[31].real - reference.real)
    assert abs(values[81].imag - reference.imag) <= abs(values[31].imag - reference.imag)


def test_dipole_over_finite_ground_impedance_converges() -> None:
    ground = GroundModel.finite(relative_permittivity=13.0, conductivity_s_per_m=0.005)
    values = {
        segments: _impedance(segments, ground=ground, height_m=8.0)
        for segments in (21, 31, 41, REFERENCE_SEGMENTS, 81)
    }
    reference = values[REFERENCE_SEGMENTS]

    # Finite ground converges more slowly than free space, so the tolerance is
    # wider.  It still rules out a segmentation-dependent oscillation.
    for segments in (31, 41, REFERENCE_SEGMENTS):
        assert values[segments].real == pytest.approx(reference.real, abs=0.15)
        assert values[segments].imag == pytest.approx(reference.imag, abs=0.3)

    assert abs(values[21] - reference) / abs(reference) <= 0.01

    assert abs(values[81].real - reference.real) <= abs(values[31].real - reference.real)
    assert abs(values[81].imag - reference.imag) <= abs(values[31].imag - reference.imag)
