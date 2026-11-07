# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""End-fed inverted-L antenna with a vertical section and a horizontal top."""

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

ANTENNA_TYPE_INVERTED_L = "inverted_l"
VERTICAL_ID = "vertical"
HORIZONTAL_ID = "horizontal"


@dataclass(frozen=True, slots=True)
class InvertedLParameters:
    """A bent end-fed wire with a vertical radiator and horizontal top.

    ``vertical_height_m`` is the height of the vertical section above the
    feedpoint, ``horizontal_length_m`` is the top horizontal run, and
    ``base_height_m`` is the feedpoint height above ground. The horizontal
    section is rotated by ``azimuth_deg`` around the vertical axis.
    """

    frequency_hz: float
    vertical_height_m: float
    horizontal_length_m: float
    base_height_m: float = 0.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.vertical_height_m, name="vertical_height_m")
        ensure_positive(self.horizontal_length_m, name="horizontal_length_m")
        ensure_non_negative(self.base_height_m, name="base_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def top_height_m(self) -> float:
        return self.base_height_m + self.vertical_height_m

    @property
    def total_length_m(self) -> float:
        return self.vertical_height_m + self.horizontal_length_m

    @classmethod
    def from_custom_parameters(
        cls,
        parameters: CustomAntennaParameters,
    ) -> InvertedLParameters:
        if len(parameters.wires) != 2:
            raise ValueError("an inverted L must contain exactly two wires")
        vertical = next(
            (wire for wire in parameters.wires if wire.id == parameters.feed.wire_id),
            None,
        )
        if vertical is None:
            raise ValueError("inverted-L feed wire is missing")
        if not math.isclose(parameters.feed.offset_m, 0.0, abs_tol=1e-9):
            raise ValueError("the inverted-L feed must be at the base of the vertical")
        if (
            math.hypot(
                vertical.end.x_m - vertical.start.x_m,
                vertical.end.y_m - vertical.start.y_m,
            )
            > 1e-6
        ):
            raise ValueError("the fed inverted-L wire must be vertical")
        base_z = min(vertical.start.z_m, vertical.end.z_m)
        top_z = max(vertical.start.z_m, vertical.end.z_m)
        vertical_height = top_z - base_z
        if vertical_height <= 0.0:
            raise ValueError("the inverted-L vertical section must have positive height")
        if not math.isclose(vertical.start.z_m, base_z, abs_tol=1e-6):
            raise ValueError("the inverted-L feed must be at the base of the vertical")
        horizontal = next(
            (wire for wire in parameters.wires if wire.id != vertical.id),
            None,
        )
        if horizontal is None:
            raise ValueError("inverted-L horizontal wire is missing")
        corner = next(
            iter({vertical.start, vertical.end} & {horizontal.start, horizontal.end}),
            None,
        )
        if corner is None:
            raise ValueError("inverted-L wires must share the top corner")
        far = horizontal.end if corner == horizontal.start else horizontal.start
        if not math.isclose(corner.z_m, top_z, abs_tol=1e-6) or not math.isclose(
            far.z_m,
            top_z,
            abs_tol=1e-6,
        ):
            raise ValueError("the inverted-L horizontal wire must be at the top of the vertical")
        if horizontal.length_m <= 0.0:
            raise ValueError("the inverted-L horizontal wire must have positive length")
        azimuth = math.degrees(math.atan2(far.y_m - corner.y_m, far.x_m - corner.x_m))
        return cls(
            frequency_hz=parameters.frequency_hz,
            vertical_height_m=vertical_height,
            horizontal_length_m=horizontal.length_m,
            base_height_m=base_z,
            azimuth_deg=azimuth,
            wire_radius_m=(vertical.radius_m + horizontal.radius_m) / 2.0,
            material=vertical.material,
            ground=parameters.ground,
        )

    def to_antenna(self, *, name: str = "Inverted L") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        base = Point3D(x_m=0.0, y_m=0.0, z_m=self.base_height_m)
        corner = Point3D(x_m=0.0, y_m=0.0, z_m=self.top_height_m)
        end = Point3D(
            x_m=self.horizontal_length_m * cos_angle,
            y_m=self.horizontal_length_m * sin_angle,
            z_m=self.top_height_m,
        )
        wires = (
            Wire(
                id=VERTICAL_ID,
                start=base,
                end=corner,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id=HORIZONTAL_ID,
                start=corner,
                end=end,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
        )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=wires,
            feed=FeedPoint(VERTICAL_ID, 0.0),
            ground=self.ground,
            generator_id="inverted_l",
            generator_name="Inverted L",
        )
