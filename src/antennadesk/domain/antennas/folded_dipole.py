# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric horizontal folded dipole."""

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

ANTENNA_TYPE_FOLDED_DIPOLE = "folded_dipole"
DRIVEN_WIRE_ID = "folded-1"


@dataclass(frozen=True, slots=True)
class FoldedDipoleParameters:
    """Parameters for a horizontal two-wire folded dipole.

    ``total_length_m`` is the length of each parallel conductor,
    ``spacing_m`` is the center-to-center spacing between them, and
    ``height_m`` is the wire height above ground.  The feed is at the center
    of the driven conductor.
    """

    frequency_hz: float
    total_length_m: float
    height_m: float
    spacing_m: float = 0.1
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.total_length_m, name="total_length_m")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_positive(self.spacing_m, name="spacing_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def total_conductor_length_m(self) -> float:
        return 2.0 * self.total_length_m + 2.0 * self.spacing_m

    def to_antenna(self, *, name: str = "Folded dipole") -> AntennaModel:
        half_length = self.total_length_m / 2.0
        half_spacing = self.spacing_m / 2.0
        angle = units.degrees_to_radians(self.azimuth_deg)
        direction_x = math.cos(angle)
        direction_y = math.sin(angle)
        perpendicular_x = -direction_y
        perpendicular_y = direction_x

        def point(u: float, v: float) -> Point3D:
            return Point3D(
                x_m=u * direction_x + v * perpendicular_x,
                y_m=u * direction_y + v * perpendicular_y,
                z_m=self.height_m,
            )

        start_driven = point(-half_length, half_spacing)
        end_driven = point(half_length, half_spacing)
        start_other = point(-half_length, -half_spacing)
        end_other = point(half_length, -half_spacing)

        wires = (
            Wire(
                id=DRIVEN_WIRE_ID,
                start=start_driven,
                end=end_driven,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="folded-2",
                start=start_other,
                end=end_other,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="end-start",
                start=start_driven,
                end=start_other,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="end-end",
                start=end_driven,
                end=end_other,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
        )
        return AntennaModel(
            name=name,
            design_frequency_hz=self.frequency_hz,
            wires=wires,
            feed=FeedPoint(wire_id=DRIVEN_WIRE_ID, offset_m=half_length),
            environment=Environment(ground=self.ground),
        )
