# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Half-wave vertical with a base matching ring (Ringo-style)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_RINGO = "ringo"
RADIATOR_ID = "radiator"
MIN_RING_SIDES = 3
MAX_RING_SIDES = 128


@dataclass(frozen=True, slots=True)
class RingoParameters:
    """A vertical radiator with a horizontal matching ring at its base."""

    frequency_hz: float
    radiator_height_m: float
    ring_diameter_m: float
    ring_height_m: float = 0.25
    ring_sides: int = 16
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.radiator_height_m, name="radiator_height_m")
        ensure_positive(self.ring_diameter_m, name="ring_diameter_m")
        ensure_positive(self.ring_height_m, name="ring_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if not MIN_RING_SIDES <= self.ring_sides <= MAX_RING_SIDES:
            raise ValueError(f"ring_sides must be between {MIN_RING_SIDES} and {MAX_RING_SIDES}")

    def to_antenna(self, *, name: str = "Ringo") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        radius = self.ring_diameter_m / 2.0
        base = Point3D(x_m=0.0, y_m=0.0, z_m=self.ring_height_m)
        wires = [
            Wire(
                id=RADIATOR_ID,
                start=base,
                end=Point3D(
                    x_m=0.0,
                    y_m=0.0,
                    z_m=self.ring_height_m + self.radiator_height_m,
                ),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="ring-connector",
                start=base,
                end=Point3D(x_m=radius, y_m=0.0, z_m=self.ring_height_m),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
        ]
        for index in range(self.ring_sides):
            angle_a = 2.0 * math.pi * index / self.ring_sides
            angle_b = 2.0 * math.pi * (index + 1) / self.ring_sides
            wires.append(
                Wire(
                    id=f"ring-{index + 1}",
                    start=Point3D(
                        x_m=radius * math.cos(angle_a),
                        y_m=radius * math.sin(angle_a),
                        z_m=self.ring_height_m,
                    ),
                    end=Point3D(
                        x_m=radius * math.cos(angle_b),
                        y_m=radius * math.sin(angle_b),
                        z_m=self.ring_height_m,
                    ),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(RADIATOR_ID, 0.0),
            ground=self.ground,
            generator_id="ringo",
            generator_name="Ringo",
        )
