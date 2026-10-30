# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent properties from the ARRL Antenna Book, 24th edition.

The free-space gain value is from Figure 2.16 (Chapter 2, printed page
2.12): a 100-foot dipole at 4.8 MHz has 2.14 dBi gain.  The folded-dipole
rule is from the same chapter/page: for equal conductors it has the same
gain and pattern as a single-wire dipole, and its feed-point resistance is
four times higher.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.solver import Nec2cSolver

NEC2C = os.environ.get("NEC2C")
pytestmark = pytest.mark.skipif(
    not NEC2C or not Path(NEC2C).is_file(),
    reason="NEC2C must point to a nec2c executable",
)


def _solver() -> Nec2cSolver:
    assert NEC2C is not None
    return Nec2cSolver(Path(NEC2C))


def _spec() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(4_800_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=31),
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=180.0,
            theta_count=19,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=37,
        ),
    )


def _spec_for_loop() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(3_750_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=31),
        far_field=FarFieldRequest(enabled=False),
    )


def test_arrl_free_space_100_foot_dipole_gain() -> None:
    parameters = DipoleParameters(
        frequency_hz=4_800_000.0,
        total_length_m=30.48,
        height_m=0.0,
        wire_radius_m=0.001,
        ground=GroundModel.free_space(),
    )
    result = _solver().run(parameters.to_antenna(), _spec())

    frequency = result.frequencies[0]
    assert frequency.impedance_ohm.real == pytest.approx(73.5, abs=2.0)
    assert result.max_total_gain_db == pytest.approx(2.14, abs=0.15)


def test_arrl_folded_dipole_keeps_gain_and_quadruples_resistance() -> None:
    single = DipoleParameters(
        frequency_hz=4_800_000.0,
        total_length_m=30.48,
        height_m=0.0,
        wire_radius_m=0.001,
        ground=GroundModel.free_space(),
    )
    folded = FoldedDipoleParameters(
        frequency_hz=4_800_000.0,
        total_length_m=30.48,
        height_m=0.0,
        spacing_m=0.1,
        wire_radius_m=0.001,
        ground=GroundModel.free_space(),
    )
    single_result = _solver().run(single.to_antenna(), _spec())
    folded_result = _solver().run(folded.to_antenna(), _spec())

    single_resistance = single_result.frequencies[0].impedance_ohm.real
    folded_resistance = folded_result.frequencies[0].impedance_ohm.real
    assert folded_resistance / single_resistance == pytest.approx(4.0, abs=0.5)
    assert folded_result.max_total_gain_db == pytest.approx(
        single_result.max_total_gain_db,
        abs=0.2,
    )


def test_arrl_free_space_quad_loop_resistance() -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    wavelength = 299_792_458.0 / 3_750_000.0
    parameters = LoopParameters(
        frequency_hz=3_750_000.0,
        circumference_m=wavelength * 1.05,
        height_m=0.0,
        sides=4,
        wire_radius_m=0.001,
        ground=GroundModel.free_space(),
    )
    result = _solver().run(parameters.to_antenna(), _spec_for_loop())

    assert result.frequencies[0].impedance_ohm.real == pytest.approx(120.0, abs=15.0)
