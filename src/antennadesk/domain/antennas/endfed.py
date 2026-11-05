# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""End-fed wire antenna."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_ENDFED = "endfed"
RADIATOR_ID = "radiator"

# Chameleon Antenna CHA LEFS Feather manual: 66.5 ft EFHW radiator, 49:1
# transformer near 3 ft, far end at about 25 ft.
SLOPER_REFERENCE_LENGTH_M = 66.5 * 0.3048
SLOPER_REFERENCE_FEED_HEIGHT_M = 3.0 * 0.3048
SLOPER_REFERENCE_END_HEIGHT_M = 25.0 * 0.3048
SLOPER_REFERENCE_TRANSFORMER_RATIO = 49.0


class EndFedPreset(StrEnum):
    STANDARD = "endfed"
    SLOPER = "sloper"
    RANDOM_WIRE = "random_wire"


COUNTERPOISE_ID = "counterpoise"
COUNTERPOISE_DROP_ID = "counterpoise-drop"


@dataclass(frozen=True, slots=True)
class EndFedParameters:
    """A single wire fed at one end, optionally sloping to a different height."""

    frequency_hz: float
    length_m: float
    feed_height_m: float = 10.0
    end_height_m: float = 10.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE
    transformer_ratio: float = 1.0
    counterpoise_length_m: float = 0.0
    counterpoise_height_m: float = 0.1
    counterpoise_azimuth_deg: float | None = None
    preset: EndFedPreset = EndFedPreset.STANDARD

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.length_m, name="length_m")
        ensure_non_negative(self.feed_height_m, name="feed_height_m")
        ensure_non_negative(self.end_height_m, name="end_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        ensure_positive(self.transformer_ratio, name="transformer_ratio")
        object.__setattr__(self, "preset", EndFedPreset(self.preset))
        ensure_non_negative(self.counterpoise_length_m, name="counterpoise_length_m")
        ensure_non_negative(self.counterpoise_height_m, name="counterpoise_height_m")
        if abs(self.end_height_m - self.feed_height_m) > self.length_m + 1e-12:
            raise ValueError(
                "the height difference between the feed and the end must not exceed the wire length"
            )
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )
        if self.counterpoise_azimuth_deg is not None:
            object.__setattr__(
                self,
                "counterpoise_azimuth_deg",
                units.normalize_azimuth_degrees(self.counterpoise_azimuth_deg),
            )

    @property
    def effective_counterpoise_azimuth_deg(self) -> float:
        if self.counterpoise_azimuth_deg is not None:
            return self.counterpoise_azimuth_deg
        return (self.azimuth_deg + 180.0) % 360.0

    def to_antenna(self, *, name: str = "End-fed wire") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        rise = self.end_height_m - self.feed_height_m
        horizontal_m = math.sqrt(max(self.length_m * self.length_m - rise * rise, 0.0))
        feed_point = Point3D(x_m=0.0, y_m=0.0, z_m=self.feed_height_m)
        wires = [
            Wire(
                id=RADIATOR_ID,
                start=feed_point,
                end=Point3D(
                    x_m=horizontal_m * math.cos(angle),
                    y_m=horizontal_m * math.sin(angle),
                    z_m=self.end_height_m,
                ),
                radius_m=self.wire_radius_m,
                material=self.material,
            )
        ]
        if self.counterpoise_length_m > 0.0:
            counterpoise_angle = units.degrees_to_radians(self.effective_counterpoise_azimuth_deg)
            counterpoise_start = Point3D(
                x_m=0.0,
                y_m=0.0,
                z_m=self.counterpoise_height_m,
            )
            if not math.isclose(self.feed_height_m, self.counterpoise_height_m):
                wires.append(
                    Wire(
                        id=COUNTERPOISE_DROP_ID,
                        start=feed_point,
                        end=counterpoise_start,
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    )
                )
            wires.append(
                Wire(
                    id=COUNTERPOISE_ID,
                    start=counterpoise_start,
                    end=Point3D(
                        x_m=self.counterpoise_length_m * math.cos(counterpoise_angle),
                        y_m=self.counterpoise_length_m * math.sin(counterpoise_angle),
                        z_m=self.counterpoise_height_m,
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
            generator_id="endfed",
            generator_name={
                EndFedPreset.STANDARD: "End-fed",
                EndFedPreset.SLOPER: "Sloper",
                EndFedPreset.RANDOM_WIRE: "Random wire",
            }[self.preset],
        )


def sloper_parameters(
    *,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> EndFedParameters:
    """Return the published Chameleon LEFS 40 m EFHW sloper geometry."""

    return EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=SLOPER_REFERENCE_LENGTH_M,
        feed_height_m=SLOPER_REFERENCE_FEED_HEIGHT_M,
        end_height_m=SLOPER_REFERENCE_END_HEIGHT_M,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
        transformer_ratio=SLOPER_REFERENCE_TRANSFORMER_RATIO,
        preset=EndFedPreset.SLOPER,
    )
