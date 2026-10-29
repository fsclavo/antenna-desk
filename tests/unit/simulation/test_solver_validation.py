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
