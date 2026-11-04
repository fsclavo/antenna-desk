# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Adapter mechanics: capabilities, execution, cancellation, errors, and link post-processing."""

from __future__ import annotations

import math
import os
from dataclasses import replace
from pathlib import Path

import pytest
from nec2c_support import (
    manual_example1_model,
    manual_example1_spec,
)

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
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.environment.environment import Environment
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationStatus
from antennadesk.domain.simulation.segmentation import (
    SegmentationPolicy,
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


def test_version_and_capabilities(solver: Nec2cSolver) -> None:
    metadata = solver.version()
    assert metadata.name == "nec2c"
    assert metadata.version == "1.3.3"

    capabilities = solver.capabilities()
    assert capabilities.supports_frequency_sweep is True
    assert capabilities.supports_currents is True
    assert capabilities.supports_far_field is True
    assert capabilities.supports_finite_ground is True


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
        manual_example1_model(),
        manual_example1_spec(),
        cancel_token=token,
    )

    assert result.status is SimulationStatus.CANCELLED
    assert any(diagnostic.code == "solver.cancelled" for diagnostic in result.diagnostics)


def test_missing_executable_returns_error() -> None:
    solver = Nec2cSolver(Path("/nonexistent/nec2c"))
    result = solver.run(manual_example1_model(), manual_example1_spec())

    assert result.status is SimulationStatus.ERROR
    assert any(diagnostic.code == "solver.not_available" for diagnostic in result.diagnostics)


def test_timeout_returns_error(solver: Nec2cSolver) -> None:
    model = manual_example1_model()
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
            model=manual_example1_model(),
            spec=manual_example1_spec(),
        )
    )

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].impedance_ohm.real == pytest.approx(82.6979, abs=0.05)


def test_l_network_transforms_impedance_before_the_feed_line(solver: Nec2cSolver) -> None:
    base = manual_example1_spec()
    reference = solver.run(manual_example1_model(), base)
    antenna_impedance = reference.frequencies[0].impedance_ohm
    network = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    line = FeedLine(characteristic_impedance_ohm=50.0, length_m=5.0, velocity_factor=1.0)
    expected = line.input_impedance(
        network.input_impedance(antenna_impedance, 299_800_000.0),
        299_800_000.0,
    )

    result = solver.run(
        manual_example1_model(),
        replace(base, matching_network=network, feed_line=line),
    )

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].impedance_ohm == pytest.approx(expected, abs=1e-6)
    assert any(diagnostic.code == "matching_network.applied" for diagnostic in result.diagnostics)
    assert any(diagnostic.code == "feed_line.applied" for diagnostic in result.diagnostics)


def test_feed_transformer_scales_impedance_before_the_feed_line(
    solver: Nec2cSolver,
) -> None:
    base = manual_example1_spec()
    reference = solver.run(manual_example1_model(), base)
    antenna_impedance = reference.frequencies[0].impedance_ohm

    result = solver.run(
        manual_example1_model(),
        replace(base, feed_transformer_ratio=4.0),
    )

    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].impedance_ohm == pytest.approx(
        antenna_impedance / 4.0,
        abs=1e-6,
    )
    assert any(diagnostic.code == "transformer.applied" for diagnostic in result.diagnostics)


def test_feed_line_transforms_impedance_at_the_transmitter(solver: Nec2cSolver) -> None:
    base = manual_example1_spec()
    reference = solver.run(manual_example1_model(), base)
    antenna_impedance = reference.frequencies[0].impedance_ohm
    line = FeedLine(
        characteristic_impedance_ohm=50.0,
        length_m=10.0,
        velocity_factor=1.0,
    )

    result = solver.run(
        manual_example1_model(),
        replace(base, feed_line=line),
    )

    expected = line.input_impedance(antenna_impedance, 299_800_000.0)
    assert result.status is SimulationStatus.COMPLETED
    assert result.frequencies[0].impedance_ohm == pytest.approx(expected, abs=1e-6)
    assert any(diagnostic.code == "feed_line.applied" for diagnostic in result.diagnostics)


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


def test_output_limit_has_a_specific_diagnostic() -> None:
    assert NEC2C is not None
    limited = Nec2cSolver(Path(NEC2C), max_output_bytes=1)

    result = limited.run(manual_example1_model(), manual_example1_spec())

    assert result.status is SimulationStatus.ERROR
    assert any(diagnostic.code == "solver.output_too_large" for diagnostic in result.diagnostics)
