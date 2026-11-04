# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Cross-check the nec2c adapter against nec2++ through PyNEC.

PyNEC wraps nec2++, an independent C++ rewrite of NEC-2.  Both engines use the
same thin-wire EFIE formulation, so this catches implementation and adapter
errors, not formulation errors.  It does not replace the published references.

PyNEC lives in the optional ``cross-engine`` dependency group:

    uv sync --group cross-engine
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.discretization import build_segment_layout
from antennadesk.simulation.nec2.solver import Nec2cSolver

PyNEC = pytest.importorskip("PyNEC")

NEC2C = os.environ.get("NEC2C")
pytestmark = [
    pytest.mark.solver,
    pytest.mark.science,
    pytest.mark.cross_engine,
    pytest.mark.skipif(
        not NEC2C or not Path(NEC2C).is_file(),
        reason="NEC2C must point to a nec2c executable",
    ),
]

FREQUENCY_HZ = 7_100_000.0
WAVELENGTH_M = 299_792_458.0 / FREQUENCY_HZ


def _spec() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(FREQUENCY_HZ),
        segmentation=SegmentationPolicy(target_segment_length_wavelengths=0.05),
        far_field=FarFieldRequest(
            enabled=True,
            theta_count=19,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=37,
        ),
    )


def _dipole() -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=FREQUENCY_HZ,
        total_length_m=20.0,
        height_m=0.0,
        wire_radius_m=0.001,
        ground=GroundModel.free_space(),
    )


def _folded_dipole() -> FoldedDipoleParameters:
    return FoldedDipoleParameters(
        frequency_hz=FREQUENCY_HZ,
        total_length_m=20.0,
        height_m=0.0,
        spacing_m=0.1,
        wire_radius_m=0.001,
        ground=GroundModel.free_space(),
    )


def _quad_loop() -> LoopParameters:
    return LoopParameters(
        frequency_hz=FREQUENCY_HZ,
        circumference_m=WAVELENGTH_M * 1.05,
        height_m=0.0,
        sides=4,
        wire_radius_m=0.001,
        ground=GroundModel.free_space(),
    )


def _run_pynec(model, spec: SimulationSpec) -> tuple[complex, float]:
    layout = build_segment_layout(model, spec)
    context = PyNEC.nec_context()
    geometry = context.get_geometry()
    for segmentation in layout.wires:
        wire = segmentation.wire
        geometry.wire(
            segmentation.tag,
            segmentation.segments,
            wire.start.x_m,
            wire.start.y_m,
            wire.start.z_m,
            wire.end.x_m,
            wire.end.y_m,
            wire.end.z_m,
            wire.radius_m,
            1.0,
            1.0,
        )
    context.geometry_complete(0)
    if spec.include_conductor_losses:
        for segmentation in layout.wires:
            context.ld_card(
                5,
                segmentation.tag,
                0,
                0,
                segmentation.wire.material.conductivity_s_per_m,
                0.0,
                0.0,
            )
    context.fr_card(0, 1, spec.frequency_plan.stop_hz / 1e6, 0.0)
    context.ex_card(
        0,
        layout.feed_tag,
        layout.feed_local_segment,
        0,
        0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )
    far_field = spec.far_field
    context.rp_card(
        0,
        far_field.theta_count,
        far_field.phi_count,
        1000,
        0,
        0,
        0,
        far_field.theta_start_deg,
        far_field.phi_start_deg,
        far_field.theta_step_deg,
        far_field.phi_step_deg,
        1.0,
        1.0,
    )
    context.xq_card(0)
    return (
        complex(context.get_impedance_real(0), context.get_impedance_imag(0)),
        context.get_gain_max(0),
    )


@pytest.mark.parametrize(
    "factory",
    [_dipole, _folded_dipole, _quad_loop],
    ids=["dipole", "folded_dipole", "quad_loop"],
)
def test_nec2c_matches_necpp(factory) -> None:
    assert NEC2C is not None
    model = factory().to_antenna()
    spec = _spec()

    reference = Nec2cSolver(Path(NEC2C)).run(model, spec)
    reference_impedance = reference.frequencies[0].impedance_ohm
    other_impedance, other_gain_db = _run_pynec(model, spec)

    assert other_impedance.real == pytest.approx(reference_impedance.real, abs=0.1)
    assert other_impedance.imag == pytest.approx(reference_impedance.imag, abs=0.1)
    assert other_gain_db == pytest.approx(reference.max_total_gain_db, abs=0.05)
