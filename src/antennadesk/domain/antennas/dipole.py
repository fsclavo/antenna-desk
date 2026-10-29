"""Parametric horizontal half-wave dipole."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.environment import Environment
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

RADIATOR_WIRE_ID = "radiator"
ANTENNA_TYPE_WIRE_DIPOLE = "wire_dipole"


@dataclass(frozen=True, slots=True)
class DipoleParameters:
    """User-facing parameters for a horizontal center-fed dipole.

    ``total_length_m`` is the physical wire length, ``height_m`` is the wire
    height above ground, and ``azimuth_deg`` is the horizontal direction of the
    wire (0 degrees along +X, 90 degrees along +Y).  The feed point is at the
    center of the wire.
    """

    frequency_hz: float
    total_length_m: float
    height_m: float
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.total_length_m, name="total_length_m")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def wavelength_m(self) -> float:
        return units.wavelength_m(self.frequency_hz)

    @property
    def half_length_m(self) -> float:
        return self.total_length_m / 2.0

    def to_antenna(self, *, name: str = "Dipole") -> AntennaModel:
        half_length = self.half_length_m
        angle = units.degrees_to_radians(self.azimuth_deg)
        offset_x = half_length * math.cos(angle)
        offset_y = half_length * math.sin(angle)

        wire = Wire(
            id=RADIATOR_WIRE_ID,
            start=Point3D(x_m=-offset_x, y_m=-offset_y, z_m=self.height_m),
            end=Point3D(x_m=offset_x, y_m=offset_y, z_m=self.height_m),
            radius_m=self.wire_radius_m,
            material=self.material,
        )
        feed = FeedPoint(wire_id=RADIATOR_WIRE_ID, offset_m=half_length)
        environment = Environment(ground=self.ground)

        return AntennaModel(
            name=name,
            design_frequency_hz=self.frequency_hz,
            wires=(wire,),
            feed=feed,
            environment=environment,
        )

    def with_length(self, total_length_m: float) -> DipoleParameters:
        return replace(self, total_length_m=total_length_m)
