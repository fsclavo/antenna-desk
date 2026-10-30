# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric inverted-V dipole generated as an editable custom-wire design."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

LEG_ONE_ID = "leg-1"
LEG_TWO_ID = "leg-2"


@dataclass(frozen=True, slots=True)
class InvertedVParameters:
    """A two-leg inverted-V with an apex feed.

    ``leg_length_m`` is the length of each sloping wire.  ``included_angle_deg``
    is the angle between the two legs at the apex; 180 degrees is a flat
    horizontal dipole and smaller angles lower the ends.
    """

    frequency_hz: float
    leg_length_m: float
    apex_height_m: float
    included_angle_deg: float = 120.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.leg_length_m, name="leg_length_m")
        ensure_non_negative(self.apex_height_m, name="apex_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if not 0.0 < self.included_angle_deg < 180.0:
            raise ValueError("included_angle_deg must be between 0 and 180")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )
        if self.end_height_m < 0.0:
            raise ValueError("the inverted-V ends would be below ground")

    @property
    def half_angle_rad(self) -> float:
        return math.radians(self.included_angle_deg) / 2.0

    @property
    def horizontal_span_m(self) -> float:
        return self.leg_length_m * math.sin(self.half_angle_rad)

    @property
    def vertical_drop_m(self) -> float:
        return self.leg_length_m * math.cos(self.half_angle_rad)

    @property
    def end_height_m(self) -> float:
        return self.apex_height_m - self.vertical_drop_m

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        apex = Point3D(x_m=0.0, y_m=0.0, z_m=self.apex_height_m)
        half_span = self.horizontal_span_m
        end_z = self.end_height_m

        def endpoint(local_x: float) -> Point3D:
            return Point3D(
                x_m=local_x * cos_angle,
                y_m=local_x * sin_angle,
                z_m=end_z,
            )

        leg_one = Wire(
            id=LEG_ONE_ID,
            start=apex,
            end=endpoint(-half_span),
            radius_m=self.wire_radius_m,
            material=self.material,
        )
        leg_two = Wire(
            id=LEG_TWO_ID,
            start=apex,
            end=endpoint(half_span),
            radius_m=self.wire_radius_m,
            material=self.material,
        )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=(leg_one, leg_two),
            feed=FeedPoint(wire_id=LEG_ONE_ID, offset_m=0.0),
            ground=self.ground,
        )
