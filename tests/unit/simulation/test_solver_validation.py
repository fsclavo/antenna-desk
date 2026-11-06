# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import ConductorMaterial
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.common.validation import Severity
from antennadesk.domain.environment.environment import Environment
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.solver import Nec2cSolver


def _model(material: ConductorMaterial | None = None) -> AntennaModel:
    if material is None:
        return DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ).to_antenna()
    wire = Wire(
        id="radiator",
        start=Point3D(-10.0, 0.0, 8.0),
        end=Point3D(10.0, 0.0, 8.0),
        radius_m=0.001,
        material=material,
    )
    return AntennaModel(
        name="custom",
        design_frequency_hz=7_100_000.0,
        wires=(wire,),
        feed=FeedPoint("radiator", 10.0),
    )


def _spec(
    *,
    include_conductor_losses: bool = True,
    ground: GroundModel | None = None,
) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        include_conductor_losses=include_conductor_losses,
        far_field=FarFieldRequest(enabled=ground is not None),
    )


def _solver() -> Nec2cSolver:
    return Nec2cSolver(Path("unused"))


def test_permeability_warning() -> None:
    material = ConductorMaterial(
        name="iron",
        conductivity_s_per_m=1.0e7,
        relative_permeability=100.0,
    )
    diagnostics = _solver().validate(_model(material), _spec())

    assert any(diagnostic.code == "solver.permeability_unsupported" for diagnostic in diagnostics)


def test_permeability_warning_is_suppressed_without_conductor_losses() -> None:
    material = ConductorMaterial(
        name="iron",
        conductivity_s_per_m=1.0e7,
        relative_permeability=100.0,
    )
    diagnostics = _solver().validate(
        _model(material),
        _spec(include_conductor_losses=False),
    )

    assert not any(
        diagnostic.code == "solver.permeability_unsupported" for diagnostic in diagnostics
    )


def _ground_level_model(*, ground: GroundModel, z_m: float = 0.0) -> AntennaModel:
    model = _model()
    return AntennaModel(
        name=model.name,
        design_frequency_hz=model.design_frequency_hz,
        wires=(
            Wire(
                id="radiator",
                start=Point3D(-10.0, 0.0, z_m),
                end=Point3D(10.0, 0.0, z_m),
                radius_m=0.001,
                material=model.wires[0].material,
            ),
        ),
        feed=model.feed,
        environment=Environment(ground=ground),
    )


def test_ground_level_wire_reports_the_nec_clearance() -> None:
    ground = GroundModel.perfect()
    diagnostics = _solver().validate(
        _ground_level_model(ground=ground),
        _spec(include_conductor_losses=False, ground=ground),
    )

    assert any(diagnostic.code == "geometry.ground_clearance" for diagnostic in diagnostics)
    assert not any(diagnostic.code == "geometry.below_ground" for diagnostic in diagnostics)
    assert not any(diagnostic.code == "geometry.ground_mounted_wires" for diagnostic in diagnostics)


def test_finite_ground_level_wire_warns_about_the_approximation() -> None:
    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    diagnostics = _solver().validate(
        _ground_level_model(ground=ground),
        _spec(include_conductor_losses=False, ground=ground),
    )

    warning = next(
        diagnostic
        for diagnostic in diagnostics
        if diagnostic.code == "geometry.ground_mounted_wires"
    )
    assert warning.severity is Severity.WARNING
    assert "ground-mounted" in warning.message


def test_wire_above_the_clearance_does_not_warn_about_ground_mounted_wires() -> None:
    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    diagnostics = _solver().validate(
        _ground_level_model(ground=ground, z_m=0.02),
        _spec(include_conductor_losses=False, ground=ground),
    )

    assert not any(diagnostic.code == "geometry.ground_mounted_wires" for diagnostic in diagnostics)


def test_below_ground_wire_is_an_error() -> None:
    model = _model()
    grounded = AntennaModel(
        name=model.name,
        design_frequency_hz=model.design_frequency_hz,
        wires=(
            Wire(
                id="radiator",
                start=Point3D(-10.0, 0.0, -0.1),
                end=Point3D(10.0, 0.0, -0.1),
                radius_m=0.001,
                material=model.wires[0].material,
            ),
        ),
        feed=model.feed,
        environment=Environment(ground=GroundModel.perfect()),
    )
    diagnostics = _solver().validate(
        grounded,
        _spec(include_conductor_losses=False, ground=GroundModel.perfect()),
    )

    assert any(diagnostic.code == "geometry.below_ground" for diagnostic in diagnostics)


def test_far_field_below_ground_warning() -> None:
    model = _model()
    grounded = AntennaModel(
        name=model.name,
        design_frequency_hz=model.design_frequency_hz,
        wires=model.wires,
        feed=model.feed,
        environment=Environment(ground=GroundModel.perfect()),
    )
    diagnostics = _solver().validate(
        grounded,
        _spec(include_conductor_losses=False, ground=GroundModel.perfect()),
    )

    assert any(diagnostic.code == "far_field.below_ground" for diagnostic in diagnostics)
