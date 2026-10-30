# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""End-fed wire antenna."""

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

ANTENNA_TYPE_ENDFED = "endfed"
RADIATOR_ID = "radiator"


@dataclass(frozen=True, slots=True)
class EndFedParameters:
    """A single wire fed at one end, optionally sloping to a different height."""

    frequency_hz: float
    length_m: float
    feed_height_m: float = 10.0
    end_height_m: float = 10.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.length_m, name="length_m")
        ensure_non_negative(self.feed_height_m, name="feed_height_m")
        ensure_non_negative(self.end_height_m, name="end_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    def to_antenna(self, *, name: str = "End-fed wire") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        wire = Wire(
            id=RADIATOR_ID,
            start=Point3D(x_m=0.0, y_m=0.0, z_m=self.feed_height_m),
            end=Point3D(
                x_m=self.length_m * math.cos(angle),
                y_m=self.length_m * math.sin(angle),
                z_m=self.end_height_m,
            ),
            radius_m=self.wire_radius_m,
            material=self.material,
        )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=(wire,),
            feed=FeedPoint(RADIATOR_ID, 0.0),
            ground=self.ground,
            generator_id="endfed",
            generator_name="End-fed",
        )
