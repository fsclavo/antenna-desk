# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""NEC2C comparison of the default and extended thin-wire kernels."""

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
from antennadesk.domain.antennas.moxon import MoxonParameters
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


def _moxon(frequency_hz: float, radius_m: float) -> AntennaModel:
    scale = 14_170_000.0 / frequency_hz
    return MoxonParameters(
        frequency_hz=frequency_hz,
        width_m=25.00 * 0.3048 * scale,
        depth_m=9.57 * 0.3048 * scale,
        reflector_tip_m=4.85 * 0.3048 * scale,
        driven_tip_m=4.00 * 0.3048 * scale,
        height_m=1.0,
        wire_radius_m=radius_m,
    ).to_antenna(name="Moxon quality")


def _yagi(frequency_hz: float, radius_m: float) -> AntennaModel:
    wavelength = wavelength_m(frequency_hz)
    return YagiParameters(
        frequency_hz=frequency_hz,
        elements=tuple(
            YagiElement(
                position_m=spacing * wavelength,
                length_m=length * wavelength,
                radius_m=radius_m,
            )
            for length, spacing in dl6wu_elements(5)
        ),
        height_m=1.0,
        driven_index=1,
    ).to_antenna(name="Yagi quality")


def _run(
    solver: Nec2cSolver,
    model: AntennaModel,
    frequency_hz: float,
    *,
    extended: bool,
):
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        extended_thin_wire_kernel=extended,
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )
    return RunSimulation(solver).execute(RunSimulationCommand(model=model, spec=spec))


@pytest.mark.parametrize(
    ("model_builder", "frequency_hz", "radius_m"),
    [
        (_moxon, 1_500_000_000.0, 0.0007),
        (_moxon, 2_400_000_000.0, 0.0005),
        (_yagi, 2_400_000_000.0, 0.001),
        (_yagi, 5_800_000_000.0, 0.001),
    ],
    ids=["moxon-1.5GHz", "moxon-2.4GHz", "yagi-2.4GHz", "yagi-5.8GHz"],
)
def test_default_and_extended_kernels_complete_and_report_impedance(
    solver: Nec2cSolver,
    model_builder,
    frequency_hz: float,
    radius_m: float,
) -> None:
    model = model_builder(frequency_hz, radius_m)

    standard = _run(solver, model, frequency_hz, extended=False)
    extended = _run(solver, model, frequency_hz, extended=True)

    assert standard.frequencies
    assert extended.frequencies
    z_standard = standard.frequencies[0].impedance_ohm
    z_extended = extended.frequencies[0].impedance_ohm
    assert math.isfinite(z_standard.real)
    assert math.isfinite(z_standard.imag)
    assert math.isfinite(z_extended.real)
    assert math.isfinite(z_extended.imag)

    standard_codes = {diagnostic.code for diagnostic in standard.diagnostics}
    extended_codes = {diagnostic.code for diagnostic in extended.diagnostics}
    assert "segmentation.radius_ratio_low" in standard_codes
    assert "segmentation.radius_ratio_low" not in extended_codes

    # Observed with the bundled NEC2C on 2026-11-18 (standard -> extended):
    # moxon-1.5GHz 101.06+59.16j -> 97.70+58.44j (|delta| 3.44 ohm)
    # moxon-2.4GHz 106.49+60.43j -> 101.92+59.72j (|delta| 4.62 ohm)
    # yagi-2.4GHz   45.84+42.04j -> 37.28+35.04j (|delta| 11.06 ohm)
    # yagi-5.8GHz    0.13+10.57j -> 0.79-4.09j  (|delta| 14.68 ohm)
    # The comparison records a deterministic change; it makes no accuracy claim.
    delta = abs(z_extended - z_standard)
    assert math.isfinite(delta)
    assert delta > 0.0
