# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric vertical radiator with an optional radial ground plane."""

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

RADIATOR_ID = "radiator"
MAX_RADIALS = 128


@dataclass(frozen=True, slots=True)
class VerticalParameters:
    """A vertical radiator with optional elevated or ground-level radials.

    ``base_height_m`` is both the lower end of the radiator and the radial
    plane.  Set it slightly above ground for elevated radials.
    """

    frequency_hz: float
    height_m: float
    base_height_m: float = 0.0
    radial_count: int = 0
    radial_length_m: float = 0.0
    radial_angle_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.height_m, name="height_m")
        ensure_non_negative(self.base_height_m, name="base_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if not 0 <= self.radial_count <= MAX_RADIALS:
            raise ValueError(f"radial_count must be between 0 and {MAX_RADIALS}")
        if self.radial_count > 0:
            ensure_positive(self.radial_length_m, name="radial_length_m")
        else:
            ensure_non_negative(self.radial_length_m, name="radial_length_m")
        object.__setattr__(
            self,
            "radial_angle_deg",
            units.normalize_azimuth_degrees(self.radial_angle_deg),
        )

    @property
    def top_height_m(self) -> float:
        return self.base_height_m + self.height_m

    def to_custom_parameters(self) -> CustomAntennaParameters:
        base = Point3D(x_m=0.0, y_m=0.0, z_m=self.base_height_m)
        wires: list[Wire] = [
            Wire(
                id=RADIATOR_ID,
                start=base,
                end=Point3D(x_m=0.0, y_m=0.0, z_m=self.top_height_m),
                radius_m=self.wire_radius_m,
                material=self.material,
            )
        ]
        if self.radial_count > 0:
            step = 360.0 / self.radial_count
            for index in range(self.radial_count):
                angle = math.radians(self.radial_angle_deg + index * step)
                wires.append(
                    Wire(
                        id=f"radial-{index + 1}",
                        start=base,
                        end=Point3D(
                            x_m=self.radial_length_m * math.cos(angle),
                            y_m=self.radial_length_m * math.sin(angle),
                            z_m=self.base_height_m,
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
            generator_id="vertical",
            generator_name="Vertical",
        )
