# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import os
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
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.environment.environment import Environment
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationStatus
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
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
