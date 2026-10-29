# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from antennadesk.domain.antennas.wire import Wire


def test_point_distance() -> None:
    first = Point3D(0.0, 0.0, 0.0)
    second = Point3D(3.0, 4.0, 0.0)
    assert first.distance_to(second) == pytest.approx(5.0)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_point_rejects_non_finite_coordinates(value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        Point3D(value, 0.0, 0.0)


def test_wire_length() -> None:
    wire = Wire(
        id="radiator",
        start=Point3D(-10.0, 0.0, 8.0),
        end=Point3D(10.0, 0.0, 8.0),
        radius_m=0.001,
        material=COPPER,
    )
    assert wire.length_m == pytest.approx(20.0)


def test_zero_length_wire_is_rejected() -> None:
    point = Point3D(0.0, 0.0, 8.0)
    with pytest.raises(ValueError, match="non-zero length"):
        Wire(
            id="radiator",
            start=point,
            end=point,
            radius_m=0.001,
            material=COPPER,
        )


def test_wire_rejects_invalid_radius() -> None:
    with pytest.raises(ValueError, match="positive"):
        Wire(
            id="radiator",
            start=Point3D(0.0, 0.0, 8.0),
            end=Point3D(10.0, 0.0, 8.0),
            radius_m=0.0,
            material=COPPER,
        )


def test_wire_rejects_empty_id() -> None:
    with pytest.raises(ValueError, match="id"):
        Wire(
            id=" ",
            start=Point3D(0.0, 0.0, 8.0),
            end=Point3D(10.0, 0.0, 8.0),
            radius_m=0.001,
            material=COPPER,
        )


def test_material_presets() -> None:
    assert COPPER.conductivity_s_per_m > ALUMINUM.conductivity_s_per_m
    assert COPPER.relative_permeability == pytest.approx(1.0)


def test_material_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="conductivity"):
        ConductorMaterial(name="test", conductivity_s_per_m=0.0)
    with pytest.raises(ValueError, match="relative_permeability"):
        ConductorMaterial(
            name="test",
            conductivity_s_per_m=1.0,
            relative_permeability=0.0,
        )
