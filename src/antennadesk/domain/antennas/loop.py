# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric vertical regular-polygon loop."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.environment import Environment
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_LOOP = "loop"
MIN_SIDES = 3
MAX_SIDES = 128


@dataclass(frozen=True, slots=True)
class LoopParameters:
    """Parameters for a vertical regular-polygon loop.

    ``circumference_m`` is the total conductor length, ``sides`` is the number
    of straight sides (4 is a square, 16 approximates a circle), and
    ``height_m`` is the bottom of the loop above ground.  The loop lies in a
    vertical plane and is rotated by ``azimuth_deg`` around the vertical axis.
    The feed is at the midpoint of the first side.
    """

    frequency_hz: float
    circumference_m: float
    height_m: float
    sides: int = 16
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.circumference_m, name="circumference_m")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if not MIN_SIDES <= self.sides <= MAX_SIDES:
            raise ValueError(f"sides must be between {MIN_SIDES} and {MAX_SIDES}")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def side_length_m(self) -> float:
        return self.circumference_m / self.sides

    @property
    def diameter_m(self) -> float:
        return self.circumference_m / (self.sides * math.sin(math.pi / self.sides))

    @property
    def top_height_m(self) -> float:
        return self.height_m + self.diameter_m

    def to_antenna(self, *, name: str = "Loop") -> AntennaModel:
        side_length = self.side_length_m
        radius = self.diameter_m / 2.0
        base_angle = units.degrees_to_radians(self.azimuth_deg)
        step = 2.0 * math.pi / self.sides
        direction_x = math.cos(base_angle)
        direction_y = math.sin(base_angle)
        center_z = self.height_m + radius

        def point(theta: float) -> Point3D:
            horizontal = radius * math.cos(theta)
            return Point3D(
                x_m=horizontal * direction_x,
                y_m=horizontal * direction_y,
                z_m=center_z + radius * math.sin(theta),
            )

        wires: list[Wire] = []
        for index in range(self.sides):
            start_angle = index * step
            end_angle = (index + 1) * step
            wires.append(
                Wire(
                    id=f"loop-{index}",
                    start=point(start_angle),
                    end=point(end_angle),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )

        return AntennaModel(
            name=name,
            design_frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(wire_id="loop-0", offset_m=side_length / 2.0),
            environment=Environment(ground=self.ground),
        )
