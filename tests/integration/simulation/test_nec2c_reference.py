# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Published numerical references: NEC-2 User's Guide examples, NBS, Cebik, and ARRL values."""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest
from nec2c_support import (
    manual_example1_model,
    manual_example1_spec,
    multi_wire_spec,
    vertical_model,
    vertical_spec,
)

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.moxon import moxon_20m_wire
from antennadesk.domain.antennas.polarization import Polarization
from antennadesk.domain.antennas.yagi import nbs_five_element
from antennadesk.domain.design import DesignIntent, LoopShape, estimate_intent
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationStatus
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


def test_manual_example1_impedance_and_pattern(solver: Nec2cSolver) -> None:
    result = solver.run(manual_example1_model(), manual_example1_spec())

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 1
    frequency = result.frequencies[0]
    assert frequency.frequency_hz == pytest.approx(299_800_000.0)
    assert frequency.impedance_ohm.real == pytest.approx(82.6979, abs=0.05)
    assert frequency.impedance_ohm.imag == pytest.approx(46.3060, abs=0.05)
    assert frequency.swr == pytest.approx(2.351965, abs=0.01)
    assert len(frequency.currents) == 7
    assert len(frequency.far_field) == 19
    assert frequency.power_budget is not None
    assert result.max_total_gain_db == pytest.approx(2.15, abs=0.2)
    assert "GW 1 7" in result.raw_input
    assert "ANTENNA INPUT PARAMETERS" in result.raw_output
    assert result.diagnostics == ()


def test_perfect_ground(solver: Nec2cSolver) -> None:
    result = solver.run(
        vertical_model(GroundModel.perfect()),
        vertical_spec(),
    )

    assert result.status is SimulationStatus.COMPLETED
    frequency = result.frequencies[0]
    assert frequency.impedance_ohm.real == pytest.approx(106.437, abs=0.05)
    assert frequency.impedance_ohm.imag == pytest.approx(9.90578, abs=0.05)
    assert result.diagnostics == ()


def test_finite_ground(solver: Nec2cSolver) -> None:
    ground = GroundModel.finite(
        relative_permittivity=6.0,
        conductivity_s_per_m=0.001,
    )
    result = solver.run(vertical_model(ground), vertical_spec())

    assert result.status is SimulationStatus.COMPLETED
    frequency = result.frequencies[0]
    assert frequency.impedance_ohm.real == pytest.approx(111.117, abs=0.05)
    assert frequency.impedance_ohm.imag == pytest.approx(11.0075, abs=0.05)


def test_vertical_dipole_template_matches_manual_example3(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.dipole import DipoleOrientation

    parameters = DipoleParameters(
        frequency_hz=30_000_000.0,
        total_length_m=5.0,
        height_m=2.0,
        orientation=DipoleOrientation.VERTICAL,
        wire_radius_m=0.3,
        ground=GroundModel.perfect(),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(30_000_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=9),
        extended_thin_wire_kernel=True,
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )

    result = solver.run(parameters.to_antenna(), spec)

    assert result.status is SimulationStatus.COMPLETED
    frequency = result.frequencies[0]
    assert frequency.impedance_ohm.real == pytest.approx(106.437, abs=0.05)
    assert frequency.impedance_ohm.imag == pytest.approx(9.90578, abs=0.05)


def test_folded_dipole_multi_wire_simulation(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )
    result = solver.run(
        parameters.to_antenna(name="Folded dipole"),
        multi_wire_spec(7_100_000.0, 300.0),
    )

    assert result.status is SimulationStatus.COMPLETED
    frequency = result.frequencies[0]
    assert math.isfinite(frequency.impedance_ohm.real)
    assert math.isfinite(frequency.impedance_ohm.imag)
    assert frequency.impedance_ohm.real > 0.0
    assert len(frequency.currents) == 44
    assert not any(d.severity.value == "error" for d in result.diagnostics)


def test_loop_multi_wire_simulation(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
    )
    result = solver.run(
        parameters.to_antenna(name="Loop"),
        multi_wire_spec(7_100_000.0, 100.0),
    )

    assert result.status is SimulationStatus.COMPLETED
    frequency = result.frequencies[0]
    assert math.isfinite(frequency.impedance_ohm.real)
    assert math.isfinite(frequency.impedance_ohm.imag)
    assert frequency.impedance_ohm.real > 0.0
    assert len(frequency.currents) == 44
    assert not any(d.severity.value == "error" for d in result.diagnostics)


def test_nbs_five_element_yagi_gain_reference(solver: Nec2cSolver) -> None:
    yagi = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=0.0,
        ground=GroundModel.free_space(),
    )
    model = yagi.to_custom_parameters().to_antenna(name="NBS 5-element Yagi")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(50_100_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=180.0,
            theta_count=37,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=73,
        ),
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.max_total_gain_db == pytest.approx(11.35, abs=0.5)
    assert len(result.frequencies[0].currents) == 5 * 21


def test_vertical_yagi_is_the_free_space_horizontal_yagi_rotated(
    solver: Nec2cSolver,
) -> None:
    horizontal = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=8.0,
        ground=GroundModel.free_space(),
    )
    vertical = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=8.0,
        polarization=Polarization.VERTICAL,
        ground=GroundModel.free_space(),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(50_100_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=180.0,
            theta_count=37,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=73,
        ),
    )

    horizontal_result = solver.run(horizontal.to_antenna(name="Horizontal Yagi"), spec)
    vertical_result = solver.run(vertical.to_antenna(name="Vertical Yagi"), spec)

    assert horizontal_result.status is SimulationStatus.COMPLETED
    assert vertical_result.status is SimulationStatus.COMPLETED
    assert vertical_result.frequencies[0].impedance_ohm == pytest.approx(
        horizontal_result.frequencies[0].impedance_ohm,
        abs=0.5,
    )
    assert vertical_result.max_total_gain_db == pytest.approx(
        horizontal_result.max_total_gain_db,
        abs=0.1,
    )


def test_vertical_moxon_is_the_free_space_horizontal_moxon_rotated(
    solver: Nec2cSolver,
) -> None:
    horizontal = moxon_20m_wire(height_m=10.0, ground=GroundModel.free_space())
    vertical = moxon_20m_wire(
        height_m=10.0,
        polarization=Polarization.VERTICAL,
        ground=GroundModel.free_space(),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(14_170_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=180.0,
            theta_count=37,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=73,
        ),
    )

    horizontal_result = solver.run(horizontal.to_antenna(name="Horizontal Moxon"), spec)
    vertical_result = solver.run(vertical.to_antenna(name="Vertical Moxon"), spec)

    assert horizontal_result.status is SimulationStatus.COMPLETED
    assert vertical_result.status is SimulationStatus.COMPLETED
    assert vertical_result.frequencies[0].impedance_ohm == pytest.approx(
        horizontal_result.frequencies[0].impedance_ohm,
        abs=0.5,
    )
    assert vertical_result.max_total_gain_db == pytest.approx(
        horizontal_result.max_total_gain_db,
        abs=0.1,
    )


def test_ocfd_published_feedpoint_trend(solver: Nec2cSolver) -> None:
    """Published sanity check for an OCFD fed 20% from one end.

    The WIA/VK2WB analysis reports roughly 276 + j140 ohms at 7.1 MHz for a
    20.9 m wire 10 m above real ground. This is a published/heuristic sanity
    check, not a strict reference: the source does not fully specify the
    EZNEC ground model. We check the reported resistance band and the
    documented trend that moving the feed toward the centre lowers R.
    """

    from antennadesk.domain.antennas.ocfd import OCFDParameters

    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        far_field=FarFieldRequest(enabled=False),
    )

    def impedance(ratio: float) -> complex:
        parameters = OCFDParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.9,
            feed_ratio=ratio,
            height_m=10.0,
            wire_radius_m=0.00075,
            ground=ground,
        )
        result = solver.run(parameters.to_antenna(name="OCFD sanity"), spec)
        assert result.status is SimulationStatus.COMPLETED
        return result.frequencies[0].impedance_ohm

    near_end = impedance(0.2)
    toward_center = impedance(0.4)

    assert 200.0 <= near_end.real <= 350.0
    assert near_end.real > toward_center.real


def test_moxon_20m_wire_reference(solver: Nec2cSolver) -> None:
    """Check the 20 m wire Moxon published by L. B. Cebik, W4RNL.

    Source: "The Moxon Rectangle: A Review", Table 1 (20 m wire), and the
    accompanying text: 56-58 ohm feedpoint, 5.8 dBi free-space gain, and
    greater than 32 dB front-to-back ratio.
    https://www.antentop.org/w4rnl.001/mox20.html
    """

    from antennadesk.domain.antennas.moxon import MoxonParameters

    foot = 0.3048
    parameters = MoxonParameters(
        frequency_hz=14_170_000.0,
        width_m=25.00 * foot,
        depth_m=9.57 * foot,
        reflector_tip_m=4.85 * foot,
        driven_tip_m=4.00 * foot,
        height_m=10.0,
        wire_radius_m=0.000912,
        ground=GroundModel.free_space(),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(14_170_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        far_field=FarFieldRequest(
            enabled=True,
            theta_count=37,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=73,
        ),
    )

    result = solver.run(parameters.to_antenna(name="Moxon 20 m reference"), spec)

    assert result.status is SimulationStatus.COMPLETED
    frequency = result.frequencies[0]
    assert 56.0 <= frequency.impedance_ohm.real <= 58.0
    assert abs(frequency.impedance_ohm.imag) < 5.0
    assert result.max_total_gain_db == pytest.approx(5.8, abs=0.3)
    forward = next(
        point.gain_total_db
        for point in frequency.far_field
        if abs(point.theta_deg - 90.0) < 0.1 and abs(point.phi_deg) < 0.1
    )
    rear = next(
        point.gain_total_db
        for point in frequency.far_field
        if abs(point.theta_deg - 90.0) < 0.1 and abs(point.phi_deg - 180.0) < 0.1
    )
    assert forward is not None and rear is not None
    assert forward - rear > 30.0


@pytest.mark.parametrize(
    ("frequency_hz", "reference_swr"),
    (
        (7_150_000.0, 1.15),
        (14_175_000.0, 1.47),
        (28_800_000.0, 1.56),
    ),
)
def test_zs6bkw_reference_swr(
    solver: Nec2cSolver, frequency_hz: float, reference_swr: float
) -> None:
    """Cebik/W4RNL free-space table: 1.15, 1.47, and 1.56 at 40/20/10 m."""

    from antennadesk.domain.antennas.zs6bkw import zs6bkw_parameters

    parameters = zs6bkw_parameters()
    model = parameters.to_antenna(name="ZS6BKW")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=SegmentationPolicy(min_segments_per_wire=9),
        include_conductor_losses=False,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert "TL " in result.raw_input
    assert result.frequencies[0].swr == pytest.approx(reference_swr, abs=0.3)


def test_ringo_estimate_is_near_a_match(solver: Nec2cSolver) -> None:
    estimate = estimate_intent(DesignIntent(frequency_hz=146_000_000.0, antenna_type="ringo"))
    model = estimate.parameters.to_antenna()
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(146_000_000.0),
        segmentation=aligned_policy_for_model(
            model,
            146_000_000.0,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=FarFieldRequest(enabled=False),
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].swr < 1.5


@pytest.mark.parametrize("shape", [LoopShape.LOOP, LoopShape.DELTA, LoopShape.QUAD])
def test_loop_estimate_starts_near_resonance(
    solver: Nec2cSolver,
    shape: LoopShape,
) -> None:
    frequency_hz = 7_100_000.0
    estimate = estimate_intent(
        DesignIntent(
            frequency_hz=frequency_hz,
            antenna_type="loop",
            loop_shape=shape,
            height_m=10.0,
        )
    )
    model = estimate.parameters.to_antenna()
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=aligned_policy_for_model(
            model,
            frequency_hz,
            SegmentationPolicy(min_segments_per_wire=3),
        ),
        far_field=FarFieldRequest(enabled=False),
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert abs(result.frequencies[0].impedance_ohm.imag) < 20.0
