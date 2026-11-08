# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric horizontal half-wave dipole."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from enum import StrEnum

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
SAG_WIRE_ID_PREFIX = "dipole-sag-"
SAG_SEGMENTS = 9
ANTENNA_TYPE_WIRE_DIPOLE = "wire_dipole"


class DipoleOrientation(StrEnum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass(frozen=True, slots=True)
class DipoleParameters:
    """User-facing parameters for a center-fed dipole.

    ``total_length_m`` is the physical wire length.  For a horizontal dipole,
    ``height_m`` is the wire height above ground and ``azimuth_deg`` is the
    horizontal direction of the wire (0 degrees along +X, 90 degrees along +Y).
    For a vertical dipole, ``height_m`` is the height of the lower end (base)
    above ground and ``azimuth_deg`` is not used.  The feed point is always at
    the center of the wire.
    """

    frequency_hz: float
    total_length_m: float
    height_m: float
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE
    sag_m: float = 0.0

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.total_length_m, name="total_length_m")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        ensure_non_negative(self.sag_m, name="sag_m")
        object.__setattr__(self, "orientation", DipoleOrientation(self.orientation))
        if self.sag_m > 0.0:
            if self.orientation is DipoleOrientation.VERTICAL:
                raise ValueError("sag_m is only supported for horizontal dipoles")
            if self.height_m <= 0.0 or self.sag_m >= self.height_m:
                raise ValueError("sag_m must be smaller than the horizontal height")
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
        environment = Environment(ground=self.ground)
        if self.sag_m > 0.0:
            wires, feed = self._sag_geometry()
            return AntennaModel(
                name=name,
                design_frequency_hz=self.frequency_hz,
                wires=wires,
                feed=feed,
                environment=environment,
            )
        if self.orientation is DipoleOrientation.VERTICAL:
            wire = Wire(
                id=RADIATOR_WIRE_ID,
                start=Point3D(x_m=0.0, y_m=0.0, z_m=self.height_m),
                end=Point3D(
                    x_m=0.0,
                    y_m=0.0,
                    z_m=self.height_m + self.total_length_m,
                ),
                radius_m=self.wire_radius_m,
                material=self.material,
            )
        else:
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

        return AntennaModel(
            name=name,
            design_frequency_hz=self.frequency_hz,
            wires=(wire,),
            feed=feed,
            environment=environment,
        )

    def _sag_geometry(self) -> tuple[tuple[Wire, ...], FeedPoint]:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        half = self.half_length_m
        points: list[Point3D] = []
        for index in range(SAG_SEGMENTS + 1):
            local_x = -half + self.total_length_m * index / SAG_SEGMENTS
            normalized = local_x / half
            z_m = self.height_m - self.sag_m * (1.0 - normalized * normalized)
            points.append(
                Point3D(
                    x_m=local_x * cos_angle,
                    y_m=local_x * sin_angle,
                    z_m=z_m,
                )
            )
        wires = tuple(
            Wire(
                id=f"{SAG_WIRE_ID_PREFIX}{index}",
                start=points[index],
                end=points[index + 1],
                radius_m=self.wire_radius_m,
                material=self.material,
            )
            for index in range(SAG_SEGMENTS)
        )
        center_index = SAG_SEGMENTS // 2
        return wires, FeedPoint(
            wire_id=f"{SAG_WIRE_ID_PREFIX}{center_index}",
            offset_m=wires[center_index].length_m / 2.0,
        )

    @property
    def conductor_length_m(self) -> float:
        """Return the physical conductor length, including a sagged path."""

        if self.sag_m <= 0.0:
            return self.total_length_m
        model = self.to_antenna(name="Conductor length")
        return sum(wire.length_m for wire in model.wires)

    def with_length(self, total_length_m: float) -> DipoleParameters:
        return replace(self, total_length_m=total_length_m)
