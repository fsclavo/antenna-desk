# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Biquad and double-biquad wire antennas.

The model is a vertical ladder of square loops with a rectangular wire
reflector.  A single biquad has two loops; the double variant has four.  The
loops share their horizontal rails, the feed sits at the midpoint of the
central rail, and the reflector is a closed rectangle offset behind the driven
plane.  The quarter-wave loop side and eighth-wave reflector spacing are
starting heuristics, not validated gain or impedance claims.
"""

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

ANTENNA_TYPE_BIQUAD = "biquad"
ANTENNA_TYPE_DOUBLE_BIQUAD = "double_biquad"

RAIL_ID_PREFIX = "biquad-rail-"
LEFT_SIDE_ID_PREFIX = "biquad-left-"
RIGHT_SIDE_ID_PREFIX = "biquad-right-"
REFLECTOR_BOTTOM_ID = "biquad-reflector-bottom"
REFLECTOR_RIGHT_ID = "biquad-reflector-right"
REFLECTOR_TOP_ID = "biquad-reflector-top"
REFLECTOR_LEFT_ID = "biquad-reflector-left"

BIQUAD_REFERENCE_FREQUENCY_HZ = 14_100_000.0
BIQUAD_DEFAULT_BASE_HEIGHT_M = 1.0
# A quarter-wave loop side gives an eighth-wave reflector spacing.
REFLECTOR_SPACING_FRACTION = 0.5


class BiquadKind(StrEnum):
    """The two catalog variants of the biquad family."""

    SINGLE = "single"
    DOUBLE = "double"

    @property
    def loop_count(self) -> int:
        return 2 if self is BiquadKind.SINGLE else 4

    @property
    def template_name(self) -> str:
        return "Biquad" if self is BiquadKind.SINGLE else "Double biquad"

    @property
    def antenna_type(self) -> str:
        return ANTENNA_TYPE_BIQUAD if self is BiquadKind.SINGLE else ANTENNA_TYPE_DOUBLE_BIQUAD


def biquad_starting_side_m(frequency_hz: float) -> float:
    """Return the quarter-wave loop side used as the starting dimension."""

    from ..design.formulas import quarter_wave_length_m

    ensure_positive(frequency_hz, name="frequency_hz")
    return quarter_wave_length_m(frequency_hz)


def biquad_parameters(
    kind: BiquadKind = BiquadKind.SINGLE,
    *,
    frequency_hz: float = BIQUAD_REFERENCE_FREQUENCY_HZ,
    base_height_m: float = BIQUAD_DEFAULT_BASE_HEIGHT_M,
    azimuth_deg: float = 0.0,
    reflector_enabled: bool = True,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> BiquadParameters:
    """Return a quarter-wave-sided starting biquad."""

    side_m = biquad_starting_side_m(frequency_hz)
    return BiquadParameters(
        frequency_hz=frequency_hz,
        kind=kind,
        loop_side_m=side_m,
        reflector_spacing_m=side_m * REFLECTOR_SPACING_FRACTION,
        base_height_m=base_height_m,
        reflector_enabled=reflector_enabled,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


@dataclass(frozen=True, slots=True)
class BiquadParameters:
    """A vertical stack of square loops with an optional wire reflector.

    ``loop_side_m`` is one side of each square. ``base_height_m`` is the
    height of the lowest rail; the feed is at the midpoint of the central rail.
    ``reflector_spacing_m`` is the distance between the driven plane and the
    reflector plane. The feed sees the driven structure as a single port.
    """

    frequency_hz: float
    loop_side_m: float
    reflector_spacing_m: float
    kind: BiquadKind = BiquadKind.SINGLE
    base_height_m: float = BIQUAD_DEFAULT_BASE_HEIGHT_M
    reflector_enabled: bool = True
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        object.__setattr__(self, "kind", BiquadKind(self.kind))
        ensure_positive(self.loop_side_m, name="loop_side_m")
        ensure_non_negative(self.base_height_m, name="base_height_m")
        ensure_positive(self.reflector_spacing_m, name="reflector_spacing_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if self.reflector_spacing_m <= 2.0 * self.wire_radius_m:
            raise ValueError("reflector_spacing_m must exceed the conductor diameter")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return self.kind.template_name

    @property
    def loop_count(self) -> int:
        return self.kind.loop_count

    @property
    def total_height_m(self) -> float:
        return self.loop_count * self.loop_side_m

    @property
    def top_height_m(self) -> float:
        return self.base_height_m + self.total_height_m

    @property
    def feed_rail_index(self) -> int:
        return self.loop_count // 2

    @property
    def feed_height_m(self) -> float:
        return self.base_height_m + self.feed_rail_index * self.loop_side_m

    @property
    def total_conductor_length_m(self) -> float:
        driven = (3 * self.loop_count + 1) * self.loop_side_m
        if not self.reflector_enabled:
            return driven
        reflector = 2.0 * (self.loop_side_m + self.total_height_m)
        return driven + reflector

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        return self.to_custom_parameters().to_antenna(
            name=name or self.template_name,
        )

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        def point(local_x_m: float, local_y_m: float, z_m: float) -> Point3D:
            return Point3D(
                x_m=local_x_m * cos_angle - local_y_m * sin_angle,
                y_m=local_x_m * sin_angle + local_y_m * cos_angle,
                z_m=z_m,
            )

        side = self.loop_side_m
        half = side / 2.0
        wires: list[Wire] = []
        for index in range(self.loop_count + 1):
            z_m = self.base_height_m + index * side
            wires.append(
                Wire(
                    id=f"{RAIL_ID_PREFIX}{index}",
                    start=point(-half, 0.0, z_m),
                    end=point(half, 0.0, z_m),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
        for index in range(self.loop_count):
            z_low = self.base_height_m + index * side
            z_high = z_low + side
            wires.append(
                Wire(
                    id=f"{LEFT_SIDE_ID_PREFIX}{index}",
                    start=point(-half, 0.0, z_low),
                    end=point(-half, 0.0, z_high),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            wires.append(
                Wire(
                    id=f"{RIGHT_SIDE_ID_PREFIX}{index}",
                    start=point(half, 0.0, z_low),
                    end=point(half, 0.0, z_high),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
        if self.reflector_enabled:
            offset = -self.reflector_spacing_m
            z_low = self.base_height_m
            z_high = self.top_height_m
            wires.extend(
                [
                    Wire(
                        id=REFLECTOR_BOTTOM_ID,
                        start=point(-half, offset, z_low),
                        end=point(half, offset, z_low),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                    Wire(
                        id=REFLECTOR_RIGHT_ID,
                        start=point(half, offset, z_low),
                        end=point(half, offset, z_high),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                    Wire(
                        id=REFLECTOR_TOP_ID,
                        start=point(half, offset, z_high),
                        end=point(-half, offset, z_high),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                    Wire(
                        id=REFLECTOR_LEFT_ID,
                        start=point(-half, offset, z_high),
                        end=point(-half, offset, z_low),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                ]
            )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(
                f"{RAIL_ID_PREFIX}{self.feed_rail_index}",
                half,
            ),
            ground=self.ground,
            generator_id=self.kind.antenna_type,
            generator_name=self.template_name,
        )
