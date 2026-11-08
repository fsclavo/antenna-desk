# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Center-fed dipole with symmetric loading coils or open links.

The model is a single straight radiator.  In the normal ``loaded`` state two
series coils sit symmetrically around the feed.  In the ``linked`` state the
outer sections are disconnected at those positions and only the center section
radiates.  Coil resistance is an explicit ideal series resistance; the coil Q
is reported for information, not used as a hidden correction.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .dipole import DipoleOrientation
from .feed import FeedPoint
from .geometry import Point3D
from .load import SeriesLoad
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_LOADED_DIPOLE = "loaded_dipole"
LOADED_DIPOLE_WIRE_ID = "loaded-dipole-wire"
LOADED_DIPOLE_LEFT_LOAD_ID = "loaded-dipole-left-load"
LOADED_DIPOLE_RIGHT_LOAD_ID = "loaded-dipole-right-load"

LOADED_DIPOLE_REFERENCE_FREQUENCY_HZ = 7_100_000.0
LOADED_DIPOLE_DEFAULT_HEIGHT_M = 10.0
LOADED_DIPOLE_DEFAULT_LINK_OFFSET_M = 2.0
LOADED_DIPOLE_DEFAULT_INDUCTANCE_H = 10e-6
LOADED_DIPOLE_DEFAULT_RESISTANCE_OHM = 0.5


def loaded_dipole_parameters(
    *,
    frequency_hz: float = LOADED_DIPOLE_REFERENCE_FREQUENCY_HZ,
    total_length_m: float = 20.0,
    height_m: float = LOADED_DIPOLE_DEFAULT_HEIGHT_M,
    link_offset_m: float = LOADED_DIPOLE_DEFAULT_LINK_OFFSET_M,
    link_open: bool = False,
    loading_coil_enabled: bool = True,
    loading_coil_inductance_h: float = LOADED_DIPOLE_DEFAULT_INDUCTANCE_H,
    loading_coil_resistance_ohm: float = LOADED_DIPOLE_DEFAULT_RESISTANCE_OHM,
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> LoadedDipoleParameters:
    """Return a loaded dipole with editable starting values."""

    return LoadedDipoleParameters(
        frequency_hz=frequency_hz,
        total_length_m=total_length_m,
        height_m=height_m,
        link_offset_m=link_offset_m,
        link_open=link_open,
        loading_coil_enabled=loading_coil_enabled,
        loading_coil_inductance_h=loading_coil_inductance_h,
        loading_coil_resistance_ohm=loading_coil_resistance_ohm,
        orientation=orientation,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


@dataclass(frozen=True, slots=True)
class LoadedDipoleParameters:
    """A center-fed dipole with symmetric links and optional loading coils.

    ``link_offset_m`` is the distance from the feed to each link/coil position.
    When ``link_open`` is true, only the center section of length
    ``2 * link_offset_m`` remains connected and the coils are disconnected.
    When the links are closed, the full ``total_length_m`` is active and the
    optional coils sit at the link positions. The feed is always at the center
    of the active conductor.
    """

    frequency_hz: float
    total_length_m: float
    height_m: float = LOADED_DIPOLE_DEFAULT_HEIGHT_M
    link_offset_m: float = LOADED_DIPOLE_DEFAULT_LINK_OFFSET_M
    link_open: bool = False
    loading_coil_enabled: bool = True
    loading_coil_inductance_h: float = LOADED_DIPOLE_DEFAULT_INDUCTANCE_H
    loading_coil_resistance_ohm: float = LOADED_DIPOLE_DEFAULT_RESISTANCE_OHM
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.total_length_m, name="total_length_m")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_positive(self.link_offset_m, name="link_offset_m")
        if 2.0 * self.link_offset_m > self.total_length_m:
            raise ValueError("link_offset_m must not exceed half the total length")
        ensure_non_negative(
            self.loading_coil_inductance_h,
            name="loading_coil_inductance_h",
        )
        ensure_non_negative(
            self.loading_coil_resistance_ohm,
            name="loading_coil_resistance_ohm",
        )
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        object.__setattr__(self, "orientation", DipoleOrientation(self.orientation))
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return "Linked dipole" if self.link_open else "Loaded dipole"

    @property
    def half_length_m(self) -> float:
        return self.total_length_m / 2.0

    @property
    def active_length_m(self) -> float:
        return 2.0 * self.link_offset_m if self.link_open else self.total_length_m

    @property
    def coil_active(self) -> bool:
        return (
            self.loading_coil_enabled
            and not self.link_open
            and self.loading_coil_inductance_h > 0.0
        )

    @property
    def managed_load_ids(self) -> frozenset[str]:
        if not self.coil_active:
            return frozenset()
        return frozenset({LOADED_DIPOLE_LEFT_LOAD_ID, LOADED_DIPOLE_RIGHT_LOAD_ID})

    @property
    def coil_q(self) -> float | None:
        """Return the series coil Q at the design frequency, if defined."""

        if not self.coil_active or self.loading_coil_resistance_ohm <= 0.0:
            return None
        reactance = 2.0 * math.pi * self.frequency_hz * self.loading_coil_inductance_h
        return reactance / self.loading_coil_resistance_ohm

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name or self.template_name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        half = self.half_length_m
        active_half = self.link_offset_m if self.link_open else half
        if self.orientation is DipoleOrientation.VERTICAL:
            center_z = self.height_m + half
            start = Point3D(0.0, 0.0, center_z - active_half)
            end = Point3D(0.0, 0.0, center_z + active_half)
        else:
            angle = units.degrees_to_radians(self.azimuth_deg)
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)
            start = Point3D(
                x_m=-active_half * cos_angle,
                y_m=-active_half * sin_angle,
                z_m=self.height_m,
            )
            end = Point3D(
                x_m=active_half * cos_angle,
                y_m=active_half * sin_angle,
                z_m=self.height_m,
            )
        wire = Wire(
            id=LOADED_DIPOLE_WIRE_ID,
            start=start,
            end=end,
            radius_m=self.wire_radius_m,
            material=self.material,
        )
        feed = FeedPoint(LOADED_DIPOLE_WIRE_ID, active_half)
        loads: list[SeriesLoad] = []
        if self.coil_active:
            loads.extend(
                [
                    SeriesLoad(
                        id=LOADED_DIPOLE_LEFT_LOAD_ID,
                        wire_id=LOADED_DIPOLE_WIRE_ID,
                        offset_m=half - self.link_offset_m,
                        inductance_h=self.loading_coil_inductance_h,
                        resistance_ohm=self.loading_coil_resistance_ohm,
                    ),
                    SeriesLoad(
                        id=LOADED_DIPOLE_RIGHT_LOAD_ID,
                        wire_id=LOADED_DIPOLE_WIRE_ID,
                        offset_m=half + self.link_offset_m,
                        inductance_h=self.loading_coil_inductance_h,
                        resistance_ohm=self.loading_coil_resistance_ohm,
                    ),
                ]
            )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=(wire,),
            feed=feed,
            ground=self.ground,
            loads=tuple(loads),
            generator_id=ANTENNA_TYPE_LOADED_DIPOLE,
            generator_name=self.template_name,
        )
