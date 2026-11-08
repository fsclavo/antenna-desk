# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Beverage traveling-wave receiving antenna.

The model is a long horizontal wire fed at one end and terminated by a
resistor to ground at the far end.  It is a receiving antenna: gain is low and
the pattern is a broad end-fire lobe toward the termination.  The termination
is represented by a short vertical wire and a series resistor.  The starting
length is one wavelength and the termination resistance is a heuristic; neither
is an independently validated construction value.
"""

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
from .load import SeriesLoad
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_BEVERAGE = "beverage"
BEVERAGE_WIRE_ID = "beverage-wire"
BEVERAGE_TERMINATION_WIRE_ID = "beverage-termination"
BEVERAGE_TERMINATION_LOAD_ID = "beverage-termination-load"

BEVERAGE_REFERENCE_FREQUENCY_HZ = 7_100_000.0
BEVERAGE_DEFAULT_HEIGHT_M = 3.0
BEVERAGE_DEFAULT_TERMINATION_OHM = 500.0


def beverage_starting_length_m(frequency_hz: float) -> float:
    """Return one wavelength as the starting traveling-wave length."""

    from ..design.formulas import wavelength_m

    ensure_positive(frequency_hz, name="frequency_hz")
    return wavelength_m(frequency_hz)


def beverage_parameters(
    *,
    frequency_hz: float = BEVERAGE_REFERENCE_FREQUENCY_HZ,
    length_m: float | None = None,
    height_m: float = BEVERAGE_DEFAULT_HEIGHT_M,
    azimuth_deg: float = 0.0,
    termination_enabled: bool = True,
    termination_resistance_ohm: float = BEVERAGE_DEFAULT_TERMINATION_OHM,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> BeverageParameters:
    """Return a one-wavelength starting Beverage."""

    return BeverageParameters(
        frequency_hz=frequency_hz,
        length_m=(beverage_starting_length_m(frequency_hz) if length_m is None else length_m),
        height_m=height_m,
        azimuth_deg=azimuth_deg,
        termination_enabled=termination_enabled,
        termination_resistance_ohm=termination_resistance_ohm,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


@dataclass(frozen=True, slots=True)
class BeverageParameters:
    """A long horizontal wire with an optional resistive termination.

    ``length_m`` runs from the feed at the near end to the termination at the
    far end. ``height_m`` is the uniform wire height. When the termination is
    enabled, a short vertical wire drops from the far end to the ground plane
    and carries a series resistor. The feedpoint is the near end of the main
    wire, so the transmitter/feed line connects directly to the traveling-wave
    wire.
    """

    frequency_hz: float
    length_m: float
    height_m: float = BEVERAGE_DEFAULT_HEIGHT_M
    azimuth_deg: float = 0.0
    termination_enabled: bool = True
    termination_resistance_ohm: float = BEVERAGE_DEFAULT_TERMINATION_OHM
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.length_m, name="length_m")
        ensure_positive(self.height_m, name="height_m")
        ensure_positive(
            self.termination_resistance_ohm,
            name="termination_resistance_ohm",
        )
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return "Beverage"

    @property
    def total_conductor_length_m(self) -> float:
        return self.length_m + self.height_m if self.termination_enabled else self.length_m

    @property
    def feed_height_m(self) -> float:
        return self.height_m

    @property
    def managed_load_ids(self) -> frozenset[str]:
        return (
            frozenset({BEVERAGE_TERMINATION_LOAD_ID}) if self.termination_enabled else frozenset()
        )

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name or self.template_name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        def point(distance_m: float, z_m: float) -> Point3D:
            return Point3D(
                x_m=distance_m * cos_angle,
                y_m=distance_m * sin_angle,
                z_m=z_m,
            )

        near = point(0.0, self.height_m)
        far = point(self.length_m, self.height_m)
        wires: list[Wire] = [
            Wire(
                id=BEVERAGE_WIRE_ID,
                start=near,
                end=far,
                radius_m=self.wire_radius_m,
                material=self.material,
            )
        ]
        loads: list[SeriesLoad] = []
        if self.termination_enabled:
            wires.append(
                Wire(
                    id=BEVERAGE_TERMINATION_WIRE_ID,
                    start=far,
                    end=point(self.length_m, 0.0),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            loads.append(
                SeriesLoad(
                    id=BEVERAGE_TERMINATION_LOAD_ID,
                    wire_id=BEVERAGE_TERMINATION_WIRE_ID,
                    offset_m=self.height_m / 2.0,
                    resistance_ohm=self.termination_resistance_ohm,
                )
            )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(BEVERAGE_WIRE_ID, 0.0),
            ground=self.ground,
            loads=tuple(loads),
            generator_id=ANTENNA_TYPE_BEVERAGE,
            generator_name=self.template_name,
        )
