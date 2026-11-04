# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math
import os
from dataclasses import replace
from pathlib import Path

import pytest

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.application.use_cases.run_simulation import (
    RunSimulation,
    RunSimulationCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.matching_network import LNetwork
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.moxon import moxon_20m_wire
from antennadesk.domain.antennas.polarization import Polarization
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.antennas.yagi import nbs_five_element
from antennadesk.domain.design import DesignIntent, LoopShape, estimate_intent
from antennadesk.domain.environment.environment import Environment
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
pytestmark = pytest.mark.skipif(
    not NEC2C or not Path(NEC2C).is_file(),
    reason="NEC2C must point to a nec2c executable",
)


@pytest.fixture
def solver() -> Nec2cSolver:
    assert NEC2C is not None
    return Nec2cSolver(Path(NEC2C))


def _manual_example1_model() -> AntennaModel:
    return DipoleParameters(
        frequency_hz=299_800_000.0,
        total_length_m=0.5,
        height_m=0.0,
        wire_radius_m=0.001,
    ).to_antenna(name="NEC-2 manual example 1")


def _manual_example1_spec() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(299_800_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=7),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=180.0,
            theta_count=19,
            phi_count=1,
        ),
    )


def _vertical_model(ground: GroundModel) -> AntennaModel:
    wire = Wire(
        id="radiator",
        start=Point3D(0.0, 0.0, 2.0),
        end=Point3D(0.0, 0.0, 7.0),
        radius_m=0.3,
        material=COPPER,
    )
    return AntennaModel(
        name="NEC-2 manual example 3",
        design_frequency_hz=30_000_000.0,
        wires=(wire,),
        feed=FeedPoint("radiator", 2.5),
        environment=Environment(ground=ground),
    )


def _vertical_spec() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(30_000_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=9),
        extended_thin_wire_kernel=True,
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )


def test_version_and_capabilities(solver: Nec2cSolver) -> None:
    metadata = solver.version()
    assert metadata.name == "nec2c"
    assert metadata.version == "1.3.3"

    capabilities = solver.capabilities()
    assert capabilities.supports_frequency_sweep is True
    assert capabilities.supports_currents is True
    assert capabilities.supports_far_field is True
    assert capabilities.supports_finite_ground is True


def test_manual_example1_impedance_and_pattern(solver: Nec2cSolver) -> None:
    result = solver.run(_manual_example1_model(), _manual_example1_spec())

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
        _vertical_model(GroundModel.perfect()),
        _vertical_spec(),
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
    result = solver.run(_vertical_model(ground), _vertical_spec())

    assert result.status is SimulationStatus.COMPLETED
    frequency = result.frequencies[0]
    assert frequency.impedance_ohm.real == pytest.approx(111.117, abs=0.05)
    assert frequency.impedance_ohm.imag == pytest.approx(11.0075, abs=0.05)


def test_frequency_sweep(solver: Nec2cSolver) -> None:
    model = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        wire_radius_m=0.001,
    ).to_antenna(name="40 m dipole")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_300_000.0, 21),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=10,
            phi_count=1,
        ),
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 21
    assert result.frequencies[0].frequency_hz == pytest.approx(6_900_000.0)
    assert result.frequencies[-1].frequency_hz == pytest.approx(7_300_000.0)
    assert all(frequency.currents for frequency in result.frequencies)
    assert all(frequency.far_field for frequency in result.frequencies)


def test_cancelled_before_run(solver: Nec2cSolver) -> None:
    token = EventCancelToken()
    token.cancel()

    result = solver.run(
        _manual_example1_model(),
        _manual_example1_spec(),
        cancel_token=token,
    )

    assert result.status is SimulationStatus.CANCELLED
    assert any(diagnostic.code == "solver.cancelled" for diagnostic in result.diagnostics)


def test_missing_executable_returns_error() -> None:
    solver = Nec2cSolver(Path("/nonexistent/nec2c"))
    result = solver.run(_manual_example1_model(), _manual_example1_spec())

    assert result.status is SimulationStatus.ERROR
    assert any(diagnostic.code == "solver.not_available" for diagnostic in result.diagnostics)


def test_timeout_returns_error(solver: Nec2cSolver) -> None:
    model = _manual_example1_model()
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(1_000_000.0, 100_000_000.0, 10_000),
        segmentation=SegmentationPolicy(segments_per_wire=51),
        far_field=FarFieldRequest(enabled=False),
        timeout_s=0.001,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.ERROR
    assert any(diagnostic.code == "solver.timeout" for diagnostic in result.diagnostics)


def test_run_simulation_use_case(solver: Nec2cSolver) -> None:
    result = RunSimulation(solver).execute(
        RunSimulationCommand(
            model=_manual_example1_model(),
            spec=_manual_example1_spec(),
        )
    )

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].impedance_ohm.real == pytest.approx(82.6979, abs=0.05)


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


def _multi_wire_spec(frequency_hz: float, reference_ohm: float) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=SegmentationPolicy(segments_per_wire=11),
        reference_impedance_ohm=reference_ohm,
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )


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
        _multi_wire_spec(7_100_000.0, 300.0),
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
        _multi_wire_spec(7_100_000.0, 100.0),
    )

    assert result.status is SimulationStatus.COMPLETED
    frequency = result.frequencies[0]
    assert math.isfinite(frequency.impedance_ohm.real)
    assert math.isfinite(frequency.impedance_ohm.imag)
    assert frequency.impedance_ohm.real > 0.0
    assert len(frequency.currents) == 44
    assert not any(d.severity.value == "error" for d in result.diagnostics)


def test_l_network_transforms_impedance_before_the_feed_line(solver: Nec2cSolver) -> None:
    base = _manual_example1_spec()
    reference = solver.run(_manual_example1_model(), base)
    antenna_impedance = reference.frequencies[0].impedance_ohm
    network = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    line = FeedLine(characteristic_impedance_ohm=50.0, length_m=5.0, velocity_factor=1.0)
    expected = line.input_impedance(
        network.input_impedance(antenna_impedance, 299_800_000.0),
        299_800_000.0,
    )

    result = solver.run(
        _manual_example1_model(),
        replace(base, matching_network=network, feed_line=line),
    )

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].impedance_ohm == pytest.approx(expected, abs=1e-6)
    assert any(diagnostic.code == "matching_network.applied" for diagnostic in result.diagnostics)
    assert any(diagnostic.code == "feed_line.applied" for diagnostic in result.diagnostics)


def test_feed_transformer_scales_impedance_before_the_feed_line(
    solver: Nec2cSolver,
) -> None:
    base = _manual_example1_spec()
    reference = solver.run(_manual_example1_model(), base)
    antenna_impedance = reference.frequencies[0].impedance_ohm

    result = solver.run(
        _manual_example1_model(),
        replace(base, feed_transformer_ratio=4.0),
    )

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].impedance_ohm == pytest.approx(
        antenna_impedance / 4.0,
        abs=1e-6,
    )
    assert any(diagnostic.code == "transformer.applied" for diagnostic in result.diagnostics)


def test_feed_line_transforms_impedance_at_the_transmitter(solver: Nec2cSolver) -> None:
    base = _manual_example1_spec()
    reference = solver.run(_manual_example1_model(), base)
    antenna_impedance = reference.frequencies[0].impedance_ohm
    line = FeedLine(
        characteristic_impedance_ohm=50.0,
        length_m=10.0,
        velocity_factor=1.0,
    )

    result = solver.run(
        _manual_example1_model(),
        replace(base, feed_line=line),
    )

    expected = line.input_impedance(antenna_impedance, 299_800_000.0)
    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].impedance_ohm == pytest.approx(expected, abs=1e-6)
    assert any(diagnostic.code == "feed_line.applied" for diagnostic in result.diagnostics)


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


@pytest.mark.parametrize(
    ("antenna_type", "frequency_hz", "kwargs"),
    [
        ("wire_dipole", 7_100_000.0, {}),
        ("folded_dipole", 7_100_000.0, {}),
        ("loop", 7_100_000.0, {"loop_shape": LoopShape.QUAD}),
        ("vertical", 146_000_000.0, {"radial_count": 8}),
        ("inverted_v", 7_100_000.0, {"height_m": 20.0}),
        ("fan_dipole", 7_100_000.0, {"height_m": 20.0}),
        ("endfed", 7_100_000.0, {}),
        ("ocfd", 7_100_000.0, {}),
        ("j_pole", 146_000_000.0, {"folded": False}),
        ("j_pole", 146_000_000.0, {"folded": True}),
        ("ringo", 146_000_000.0, {}),
        ("yagi", 146_000_000.0, {"yagi_elements": 5}),
        ("moxon", 14_170_000.0, {}),
    ],
)
def test_every_estimator_produces_a_solvable_model(
    solver: Nec2cSolver,
    antenna_type: str,
    frequency_hz: float,
    kwargs: dict[str, object],
) -> None:
    estimate = estimate_intent(
        DesignIntent(frequency_hz=frequency_hz, antenna_type=antenna_type, **kwargs)
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
    assert result.frequencies
    assert math.isfinite(result.frequencies[0].impedance_ohm.real)
    assert math.isfinite(result.frequencies[0].impedance_ohm.imag)


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


def test_vertical_generator_produces_a_usable_sweep(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.25,
        radial_count=16,
        radial_length_m=5.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    model = parameters.to_custom_parameters().to_antenna(name="Vertical")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(7_000_000.0, 7_200_000.0, 5),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=19,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=73,
        ),
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 5
    assert all(frequency.impedance_ohm.real > 0.0 for frequency in result.frequencies)
    assert all(frequency.swr is not None for frequency in result.frequencies)
    assert result.max_total_gain_db is not None


def test_j_pole_defaults_to_a_ground_clear_base(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.j_pole import JPoleParameters

    parameters = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(145_000_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=19,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=73,
        ),
    )

    result = solver.run(parameters.to_antenna(), spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies
    assert result.max_total_gain_db is not None


def test_slim_jim_runs_with_the_feed_offset_above_the_base(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.antennas.j_pole import JPoleParameters

    parameters = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        base_height_m=0.25,
        folded=True,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(145_000_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
    )

    result = solver.run(parameters.to_antenna(), spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies
    assert result.frequencies[0].impedance_ohm.real > 0.0
    assert result.frequencies[0].swr is not None


def test_dl6wu_yagi_estimator_produces_a_runnable_model(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.design import DesignIntent, estimate_intent

    estimate = estimate_intent(
        DesignIntent(
            frequency_hz=144_000_000.0,
            antenna_type="yagi",
            height_m=10.0,
            yagi_elements=32,
        )
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(144_000_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=7),
        include_conductor_losses=False,
    )

    result = solver.run(estimate.parameters.to_antenna(), spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies
    assert result.frequencies[0].impedance_ohm.real > 0.0


def test_freshly_estimated_ground_mounted_vertical_completes(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.design import DesignIntent, VerticalForm, estimate_intent

    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    parameters = estimate_intent(
        DesignIntent(
            frequency_hz=7_100_000.0,
            antenna_type="vertical",
            vertical_form=VerticalForm.QUARTER_WAVE,
            radial_count=4,
            ground=ground,
        )
    ).parameters
    model = parameters.to_antenna(name="Estimated vertical")
    segmentation = aligned_policy_for_model(
        model,
        parameters.frequency_hz * 1.05,
        SegmentationPolicy(min_segments_per_wire=3),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
        segmentation=segmentation,
        far_field=FarFieldRequest(enabled=False),
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].impedance_ohm.real > 0.0
    assert any(diagnostic.code == "geometry.ground_clearance" for diagnostic in result.diagnostics)


def test_loaded_vertical_with_a_series_coil_solves(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=1.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=12e-6,
        loading_coil_resistance_ohm=0.5,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    model = parameters.to_antenna(name="Loaded vertical")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        include_conductor_losses=False,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 1
    assert result.frequencies[0].impedance_ohm.real > 0.0


def test_trap_dipole_with_parallel_traps_solves_both_bands(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    parameters = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=10e-6,
        height_m=12.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    model = parameters.to_antenna(name="Trap dipole")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(7_100_000.0, 14_100_000.0, 2),
        segmentation=SegmentationPolicy(min_segments_per_wire=9),
        include_conductor_losses=False,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 2
    assert all(frequency.impedance_ohm.real > 0.0 for frequency in result.frequencies)


def test_realized_gain_and_directivity_are_reported(
    solver: Nec2cSolver,
) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=10.0,
    )
    model = parameters.to_antenna(name="Realized gain dipole")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=9),
        include_conductor_losses=True,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=19,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=37,
        ),
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    frequency = result.frequencies[0]
    assert frequency.directivity_db is not None
    assert frequency.realized_gain_db is not None
    assert frequency.mismatch_loss_db is not None
    assert frequency.feed_line_loss_db == pytest.approx(0.0)
    assert frequency.network_loss_db == pytest.approx(0.0)
    assert frequency.directivity_db >= (frequency.realized_gain_db or -math.inf)
    assert frequency.power_budget is not None
    max_gain_db = max(
        point.gain_total_db for point in frequency.far_field if point.gain_total_db is not None
    )
    expected_directivity = max_gain_db - 10.0 * math.log10(
        frequency.power_budget.efficiency_percent / 100.0
    )
    assert frequency.directivity_db == pytest.approx(expected_directivity)
    assert result.max_directivity_db == pytest.approx(frequency.directivity_db)
    assert result.max_realized_gain_db == pytest.approx(frequency.realized_gain_db)


def test_transmission_line_geometry_repeats_the_load_impedance(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.antennas.transmission_line import TransmissionLine
    from antennadesk.domain.antennas.wire import Wire

    frequency_hz = 7_100_000.0
    dipole = DipoleParameters(
        frequency_hz=frequency_hz,
        total_length_m=20.0,
        height_m=10.0,
    )
    direct_model = dipole.to_antenna(name="Direct dipole")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=SegmentationPolicy(segments_per_wire=9),
        include_conductor_losses=False,
    )
    direct = solver.run(direct_model, spec)

    source = Wire(
        id="source",
        start=Point3D(0.0, 0.0, 0.0),
        end=Point3D(0.0, 0.0, 0.02),
        radius_m=0.001,
        material=COPPER,
    )
    line_model = AntennaModel(
        name="Line-fed dipole",
        design_frequency_hz=frequency_hz,
        wires=(source, *direct_model.wires),
        feed=FeedPoint("source", 0.01),
        environment=Environment(),
        transmission_lines=(
            TransmissionLine(
                id="line-1",
                start_wire_id="source",
                start_offset_m=0.01,
                end_wire_id="radiator",
                end_offset_m=10.0,
                characteristic_impedance_ohm=50.0,
                length_m=299_792_458.0 / (2.0 * frequency_hz),
                velocity_factor=1.0,
            ),
        ),
    )
    line_fed = solver.run(line_model, spec)

    assert direct.status is SimulationStatus.COMPLETED
    assert line_fed.status is SimulationStatus.COMPLETED
    assert "TL 1 5 2 5" in line_fed.raw_input
    direct_impedance = direct.frequencies[0].impedance_ohm
    line_impedance = line_fed.frequencies[0].impedance_ohm
    assert line_impedance.real == pytest.approx(direct_impedance.real, rel=0.01)
    assert line_impedance.imag == pytest.approx(direct_impedance.imag, rel=0.01)


def test_g5rv_preset_with_geometry_line_solves(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.g5rv import g5rv_parameters

    parameters = g5rv_parameters(
        frequency_hz=14_100_000.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    model = parameters.to_antenna(name="G5RV")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(7_100_000.0, 21_100_000.0, 3),
        segmentation=SegmentationPolicy(min_segments_per_wire=9),
        include_conductor_losses=False,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 3
    assert "TL " in result.raw_input
    assert all(frequency.impedance_ohm.real > 0.0 for frequency in result.frequencies)


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


def test_zepp_preset_with_geometry_matching_section_solves(solver: Nec2cSolver) -> None:
    from antennadesk.domain.antennas.zepp import zepp_parameters

    parameters = zepp_parameters()
    model = parameters.to_antenna(name="Zepp")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(7_000_000.0, 14_300_000.0, 3),
        segmentation=SegmentationPolicy(min_segments_per_wire=9),
        include_conductor_losses=False,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert "TL " in result.raw_input
    assert len(result.frequencies) == 3
    assert all(frequency.impedance_ohm.real > 0.0 for frequency in result.frequencies)


def test_output_limit_has_a_specific_diagnostic() -> None:
    assert NEC2C is not None
    limited = Nec2cSolver(Path(NEC2C), max_output_bytes=1)

    result = limited.run(_manual_example1_model(), _manual_example1_spec())

    assert result.status is SimulationStatus.ERROR
    assert any(diagnostic.code == "solver.output_too_large" for diagnostic in result.diagnostics)


def _g5rv_model_and_segmentation():
    from antennadesk.domain.antennas.g5rv import G5RV_DIPOLE_ID, g5rv_parameters

    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    parameters = g5rv_parameters(
        frequency_hz=14_100_000.0,
        ground=ground,
    )
    model = parameters.to_antenna(name="G5RV")
    stop_hz = 30_000_000.0
    base = SegmentationPolicy(min_segments_per_wire=3)
    dipole = model.wire_by_id(G5RV_DIPOLE_ID)
    count = base.segments_for(dipole, stop_hz)
    if count % 2 == 0:
        count += 1
    segmentation = aligned_policy_for_model(
        model,
        stop_hz,
        SegmentationPolicy(
            min_segments_per_wire=3,
            wire_segments=((G5RV_DIPOLE_ID, count),),
        ),
    )
    return model, segmentation, ground


def test_g5rv_default_budgeted_pattern_completes(solver: Nec2cSolver) -> None:
    from antennadesk.domain.simulation.bands import band_snapshot_frequencies
    from antennadesk.domain.simulation.budget import choose_pattern_step
    from antennadesk.ui.pattern_resolution import pattern_counts

    model, segmentation, ground = _g5rv_model_and_segmentation()
    plan = FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 41)
    snapshots = band_snapshot_frequencies(plan, preferred_frequency_hz=14_100_000.0)
    segment_count = sum(segmentation.segments_for(wire, plan.stop_hz) for wire in model.wires)
    budget = choose_pattern_step(
        frequency_count=plan.count,
        pattern_frequency_count=len(snapshots),
        segment_count=segment_count,
        candidate_steps=(1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        counts_for_step=lambda step: pattern_counts(step, ground),
    )

    assert budget.pattern_step_deg == 1.0
    spec = SimulationSpec(
        frequency_plan=plan,
        segmentation=segmentation,
        include_conductor_losses=True,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=91,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=361,
        ),
        pattern_frequencies_hz=snapshots,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 41
    assert sum(1 for frequency in result.frequencies if frequency.far_field) == 9
    assert all(frequency.currents for frequency in result.frequencies)
    assert len(result.raw_output) < 50 * 1024 * 1024


def test_g5rv_dense_sweep_uses_pattern_snapshots(solver: Nec2cSolver) -> None:
    from antennadesk.domain.simulation.bands import band_snapshot_frequencies
    from antennadesk.domain.simulation.budget import (
        DEFAULT_MAX_PROJECT_BYTES,
        choose_pattern_step,
    )
    from antennadesk.ui.pattern_resolution import pattern_counts

    model, segmentation, ground = _g5rv_model_and_segmentation()
    plan = FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 200)
    snapshots = band_snapshot_frequencies(plan, preferred_frequency_hz=14_100_000.0)
    segment_count = sum(segmentation.segments_for(wire, plan.stop_hz) for wire in model.wires)
    budget = choose_pattern_step(
        frequency_count=plan.count,
        pattern_frequency_count=len(snapshots),
        segment_count=segment_count,
        candidate_steps=(1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        counts_for_step=lambda step: pattern_counts(step, ground),
    )

    assert budget.pattern_step_deg == 1.0
    assert budget.estimated_project_bytes < DEFAULT_MAX_PROJECT_BYTES
    spec = SimulationSpec(
        frequency_plan=plan,
        segmentation=segmentation,
        include_conductor_losses=True,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=91,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=361,
        ),
        pattern_frequencies_hz=snapshots,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 200
    assert sum(1 for frequency in result.frequencies if frequency.far_field) == 9
    assert all(frequency.currents for frequency in result.frequencies)
    assert all(frequency.swr is not None for frequency in result.frequencies)
    assert len(result.raw_output) < 50 * 1024 * 1024


def _estimated_family_parameters(key: str, frequency_hz: float):
    from antennadesk.domain.antennas.t2fd import (
        T2FDParameters,
        t2fd_starting_dimensions,
    )
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    if key == "vertical":
        return estimate_intent(
            DesignIntent(
                frequency_hz=frequency_hz,
                antenna_type="vertical",
                vertical_form="quarter_wave",
                radial_count=4,
                ground=ground,
            )
        ).parameters
    if key == "loop":
        return estimate_intent(
            DesignIntent(
                frequency_hz=frequency_hz,
                antenna_type="loop",
                loop_shape=LoopShape.QUAD,
                ground=ground,
            )
        ).parameters
    if key == "fan_dipole":
        return estimate_intent(
            DesignIntent(
                frequency_hz=frequency_hz,
                antenna_type="fan_dipole",
                fan_bands_hz=(frequency_hz, frequency_hz * 2.0),
                ground=ground,
            )
        ).parameters
    if key == "endfed":
        return estimate_intent(
            DesignIntent(
                frequency_hz=frequency_hz,
                antenna_type="endfed",
                end_height_m=2.0,
                ground=ground,
            )
        ).parameters
    if key == "trap_dipole":
        return TrapDipoleParameters(
            frequency_hz=frequency_hz,
            high_band_frequency_hz=min(frequency_hz * 2.0, 60_000_000.0),
            inner_length_m=10.0,
            outer_length_m=5.0,
            trap_frequency_hz=min(frequency_hz * 2.0, 60_000_000.0),
            trap_inductance_h=10e-6,
            height_m=10.0,
            ground=ground,
        )
    if key == "t2fd":
        span_m, spacing_m = t2fd_starting_dimensions(frequency_hz)
        return T2FDParameters(
            frequency_hz=frequency_hz,
            highest_frequency_hz=max(frequency_hz * 2.0, 30_000_000.0),
            length_m=span_m,
            spacing_m=spacing_m,
            height_m=10.0,
            ground=ground,
        )
    return estimate_intent(
        DesignIntent(
            frequency_hz=frequency_hz,
            antenna_type=key,
            ground=ground,
        )
    ).parameters


@pytest.mark.parametrize(
    ("key", "frequency_hz"),
    (
        ("wire_dipole", 1_800_000.0),
        ("wire_dipole", 28_500_000.0),
        ("folded_dipole", 7_100_000.0),
        ("loop", 1_800_000.0),
        ("vertical", 7_100_000.0),
        ("inverted_v", 1_800_000.0),
        ("inverted_v", 3_500_000.0),
        ("fan_dipole", 1_800_000.0),
        ("fan_dipole", 7_100_000.0),
        ("endfed", 7_100_000.0),
        ("endfed", 28_500_000.0),
        ("ocfd", 7_100_000.0),
        ("j_pole", 50_000_000.0),
        ("ringo", 29_000_000.0),
        ("yagi", 14_100_000.0),
        ("moxon", 14_100_000.0),
        ("trap_dipole", 7_100_000.0),
        ("t2fd", 3_500_000.0),
        ("t2fd", 14_100_000.0),
    ),
)
def test_estimated_families_solve_above_ground(
    solver: Nec2cSolver,
    key: str,
    frequency_hz: float,
) -> None:
    parameters = _estimated_family_parameters(key, frequency_hz)
    model = parameters.to_antenna(name=key)
    min_z = min(point.z_m for wire in model.wires for point in (wire.start, wire.end))
    segmentation = aligned_policy_for_model(
        model,
        frequency_hz,
        SegmentationPolicy(min_segments_per_wire=3),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=segmentation,
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )

    result = solver.run(model, spec)

    assert min_z >= -1e-9, f"{key} has a wire below ground"
    assert result.status is SimulationStatus.COMPLETED
    assert math.isfinite(result.frequencies[0].impedance_ohm.real)


def test_t2fd_default_design_completes_with_a_broadband_match(
    solver: Nec2cSolver,
) -> None:
    from antennadesk.domain.antennas.t2fd import (
        T2FD_DRIVEN_WIRE_ID,
        T2FD_TERMINATED_WIRE_ID,
        T2FDParameters,
        t2fd_starting_dimensions,
    )

    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    span_m, spacing_m = t2fd_starting_dimensions(3_500_000.0)
    parameters = T2FDParameters(
        frequency_hz=3_500_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=span_m,
        spacing_m=spacing_m,
        height_m=10.0,
        termination_resistance_ohm=800.0,
        transformer_ratio=16.0,
        ground=ground,
    )
    model = parameters.to_antenna(name="T2FD")
    stop_hz = parameters.highest_frequency_hz
    base = aligned_policy_for_model(
        model,
        stop_hz,
        SegmentationPolicy(min_segments_per_wire=3),
    )
    driven_count = base.segments_for(
        model.wire_by_id(T2FD_DRIVEN_WIRE_ID),
        stop_hz,
    )
    if driven_count % 2 == 0:
        driven_count += 1
    segmentation = SegmentationPolicy(
        min_segments_per_wire=3,
        wire_segments=tuple(
            (
                wire.id,
                driven_count
                if wire.id in {T2FD_DRIVEN_WIRE_ID, T2FD_TERMINATED_WIRE_ID}
                else base.segments_for(wire, stop_hz),
            )
            for wire in model.wires
        ),
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 31),
        segmentation=segmentation,
        include_conductor_losses=True,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=10,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=37,
        ),
        feed_transformer_ratio=parameters.transformer_ratio,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 31
    assert any(diagnostic.code == "transformer.applied" for diagnostic in result.diagnostics)
    assert all(frequency.impedance_ohm.real > 0.0 for frequency in result.frequencies)
    assert all(frequency.swr is not None for frequency in result.frequencies)
    assert max(frequency.swr for frequency in result.frequencies) < 3.5
    assert all(
        frequency.realized_gain_db is not None and math.isfinite(frequency.realized_gain_db)
        for frequency in result.frequencies
    )
    assert len(result.raw_output) < 10 * 1024 * 1024
