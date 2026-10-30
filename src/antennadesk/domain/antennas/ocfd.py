# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Off-center-fed dipole generated as an editable custom-wire design."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

RADIATOR_ID = "radiator"


@dataclass(frozen=True, slots=True)
class OCFDParameters:
    """A single horizontal wire fed away from its center."""

    frequency_hz: float
    total_length_m: float
    feed_ratio: float = 1.0 / 3.0
    height_m: float = 10.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.total_length_m, name="total_length_m")
        ensure_positive(self.height_m, name="height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if not 0.0 < self.feed_ratio < 1.0:
            raise ValueError("feed_ratio must be between 0 and 1")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def feed_offset_m(self) -> float:
        return self.total_length_m * self.feed_ratio

    def to_custom_parameters(self) -> CustomAntennaParameters:
        half_length = self.total_length_m / 2.0
        angle = units.degrees_to_radians(self.azimuth_deg)
        offset_x = half_length * math.cos(angle)
        offset_y = half_length * math.sin(angle)
        wire = Wire(
            id=RADIATOR_ID,
            start=Point3D(x_m=-offset_x, y_m=-offset_y, z_m=self.height_m),
            end=Point3D(x_m=offset_x, y_m=offset_y, z_m=self.height_m),
            radius_m=self.wire_radius_m,
            material=self.material,
        )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=(wire,),
            feed=FeedPoint(RADIATOR_ID, self.feed_offset_m),
            ground=self.ground,
            generator_id="ocfd",
            generator_name="OCFD",
        )

    @classmethod
    def from_custom_parameters(
        cls,
        parameters: CustomAntennaParameters,
    ) -> OCFDParameters:
        if len(parameters.wires) != 1:
            raise ValueError("an OCFD must contain exactly one wire")
        wire = parameters.wires[0]
        if not math.isclose(wire.start.z_m, wire.end.z_m, abs_tol=1e-6):
            raise ValueError("the OCFD wire must be horizontal")
        if wire.length_m <= 0.0:
            raise ValueError("the OCFD wire must have positive length")
        feed_ratio = parameters.feed.offset_m / wire.length_m
        if not 0.0 < feed_ratio < 1.0:
            raise ValueError("the OCFD feed must be inside the wire")
        dx = wire.end.x_m - wire.start.x_m
        dy = wire.end.y_m - wire.start.y_m
        return cls(
            frequency_hz=parameters.frequency_hz,
            total_length_m=wire.length_m,
            feed_ratio=feed_ratio,
            height_m=wire.start.z_m,
            azimuth_deg=math.degrees(math.atan2(dy, dx)),
            wire_radius_m=wire.radius_m,
            material=wire.material,
            ground=parameters.ground,
        )
