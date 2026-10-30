# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from uuid import uuid4

import pytest

from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.projects.project import DesignVariant


def _custom() -> CustomAntennaParameters:
    wire = Wire(
        id="wire-1",
        start=Point3D(-5.0, 0.0, 8.0),
        end=Point3D(5.0, 0.0, 8.0),
        radius_m=0.001,
        material=COPPER,
    )
    return CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(wire,),
        feed=FeedPoint("wire-1", 5.0),
    )


def test_custom_parameters_generate_a_canonical_model() -> None:
    parameters = _custom()
    model = parameters.to_antenna(name="Custom")

    assert model.name == "Custom"
    assert model.design_frequency_hz == pytest.approx(7_100_000.0)
    assert len(model.wires) == 1
    assert model.feed.wire_id == "wire-1"


def test_custom_parameters_validate_wire_and_feed_rules() -> None:
    wire = Wire(
        id="wire-1",
        start=Point3D(-5.0, 0.0, 8.0),
        end=Point3D(5.0, 0.0, 8.0),
        radius_m=0.001,
        material=COPPER,
    )
    with pytest.raises(ValueError, match="unknown wire"):
        CustomAntennaParameters(
            frequency_hz=7_100_000.0,
            wires=(wire,),
            feed=FeedPoint("missing", 1.0),
        ).to_antenna()


def test_custom_parameters_work_in_a_design_variant() -> None:
    parameters = _custom()
    design = DesignVariant(
        id=uuid4(),
        name="Custom",
        antenna_type="custom",
        parameters=parameters,
        antenna=parameters.to_antenna(name="Custom"),
    )

    assert design.antenna_type == "custom"
    assert design.antenna.wires[0].length_m == pytest.approx(10.0)


def _wire(wire_id: str, start: tuple[float, float, float], end: tuple[float, float, float]) -> Wire:
    return Wire(
        id=wire_id,
        start=Point3D(*start),
        end=Point3D(*end),
        radius_m=0.001,
        material=COPPER,
    )


def _with_wires(*wires: Wire) -> CustomAntennaParameters:
    return CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=wires,
        feed=FeedPoint(wires[0].id, wires[0].length_m / 2.0),
    )


def test_custom_geometry_detects_overlapping_wires() -> None:
    from antennadesk.domain.antennas.custom import geometry_warnings

    warnings = geometry_warnings(
        _with_wires(
            _wire("a", (0.0, 0.0, 8.0), (10.0, 0.0, 8.0)),
            _wire("b", (5.0, 0.0, 8.0), (15.0, 0.0, 8.0)),
        )
    )

    assert any(diagnostic.code == "custom.wires.overlap" for diagnostic in warnings)


def test_custom_geometry_detects_crossing_wires() -> None:
    from antennadesk.domain.antennas.custom import geometry_warnings

    warnings = geometry_warnings(
        _with_wires(
            _wire("a", (-5.0, 0.0, 8.0), (5.0, 0.0, 8.0)),
            _wire("b", (0.0, -5.0, 8.0), (0.0, 5.0, 8.0)),
        )
    )

    assert any(diagnostic.code == "custom.wires.cross" for diagnostic in warnings)


def test_custom_geometry_allows_separate_parallel_wires() -> None:
    from antennadesk.domain.antennas.custom import geometry_warnings

    warnings = geometry_warnings(
        _with_wires(
            _wire("a", (-5.0, 0.0, 8.0), (5.0, 0.0, 8.0)),
            _wire("b", (-5.0, 1.0, 8.0), (5.0, 1.0, 8.0)),
        )
    )

    assert warnings == ()
