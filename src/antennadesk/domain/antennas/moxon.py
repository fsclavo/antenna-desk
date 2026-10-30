# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric Moxon rectangle."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_MOXON = "moxon"
REFLECTOR_ID = "reflector"
DRIVEN_ID = "driven"


@dataclass(frozen=True, slots=True)
class MoxonParameters:
    """A Moxon rectangle with bent reflector and driven-element tips."""

    frequency_hz: float
    width_m: float
    depth_m: float
    reflector_tip_m: float
    driven_tip_m: float
    height_m: float = 10.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.width_m, name="width_m")
        ensure_positive(self.depth_m, name="depth_m")
        ensure_positive(self.reflector_tip_m, name="reflector_tip_m")
        ensure_positive(self.driven_tip_m, name="driven_tip_m")
        ensure_positive(self.height_m, name="height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if self.reflector_tip_m + self.driven_tip_m >= self.depth_m:
            raise ValueError("Moxon tip lengths must leave a gap between elements")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def gap_m(self) -> float:
        return self.depth_m - self.reflector_tip_m - self.driven_tip_m

    def to_antenna(self, *, name: str = "Moxon") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        half_width = self.width_m / 2.0
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        def rotate(x_m: float, y_m: float) -> Point3D:
            return Point3D(
                x_m=x_m * cos_angle - y_m * sin_angle,
                y_m=x_m * sin_angle + y_m * cos_angle,
                z_m=self.height_m,
            )

        wires = (
            Wire(
                id=REFLECTOR_ID,
                start=rotate(0.0, -half_width),
                end=rotate(0.0, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="reflector-tip-1",
                start=rotate(0.0, -half_width),
                end=rotate(self.reflector_tip_m, -half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="reflector-tip-2",
                start=rotate(0.0, half_width),
                end=rotate(self.reflector_tip_m, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id=DRIVEN_ID,
                start=rotate(self.depth_m, -half_width),
                end=rotate(self.depth_m, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="driven-tip-1",
                start=rotate(self.depth_m, -half_width),
                end=rotate(self.depth_m - self.driven_tip_m, -half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="driven-tip-2",
                start=rotate(self.depth_m, half_width),
                end=rotate(self.depth_m - self.driven_tip_m, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
        )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=wires,
            feed=FeedPoint(DRIVEN_ID, half_width),
            ground=self.ground,
            generator_id="moxon",
            generator_name="Moxon",
        )
