# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric multi-band fan dipole."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_FAN_DIPOLE = "fan_dipole"


@dataclass(frozen=True, slots=True)
class FanElement:
    """One dipole pair in the fan, with its total length and included angle."""

    length_m: float
    included_angle_deg: float = 120.0

    def __post_init__(self) -> None:
        ensure_positive(self.length_m, name="length_m")
        if not 0.0 < self.included_angle_deg <= 180.0:
            raise ValueError("included_angle_deg must be between 0 and 180")


@dataclass(frozen=True, slots=True)
class FanDipoleParameters:
    """Multiple center-fed dipoles sharing a common apex feed."""

    frequency_hz: float
    elements: tuple[FanElement, ...]
    apex_height_m: float
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_non_negative(self.apex_height_m, name="apex_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        elements = tuple(self.elements)
        object.__setattr__(self, "elements", elements)
        if len(elements) < 1:
            raise ValueError("a fan dipole requires at least one element pair")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )
        for element in elements:
            if self.element_end_height_m(element) < 0.0:
                raise ValueError("a fan dipole element would end below ground")

    def element_end_height_m(self, element: FanElement) -> float:
        half_angle = math.radians(element.included_angle_deg) / 2.0
        return self.apex_height_m - (element.length_m / 2.0) * math.cos(half_angle)

    def to_antenna(self, *, name: str = "Fan dipole") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        apex = Point3D(x_m=0.0, y_m=0.0, z_m=self.apex_height_m)
        wires: list[Wire] = []
        for index, element in enumerate(self.elements):
            half_angle = math.radians(element.included_angle_deg) / 2.0
            half_length = element.length_m / 2.0
            horizontal = half_length * math.sin(half_angle)
            drop = half_length * math.cos(half_angle)

            def endpoint(local_x: float, drop: float = drop) -> Point3D:
                return Point3D(
                    x_m=local_x * cos_angle,
                    y_m=local_x * sin_angle,
                    z_m=self.apex_height_m - drop,
                )

            wires.append(
                Wire(
                    id=f"fan-{index + 1}-leg-1",
                    start=apex,
                    end=endpoint(-horizontal),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            wires.append(
                Wire(
                    id=f"fan-{index + 1}-leg-2",
                    start=apex,
                    end=endpoint(horizontal),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(wires[0].id, 0.0),
            ground=self.ground,
            generator_id="fan_dipole",
            generator_name="Fan dipole",
        )
