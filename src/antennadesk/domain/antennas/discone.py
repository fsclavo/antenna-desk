# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Wire approximation of a broadband discone antenna."""

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

ANTENNA_TYPE_DISCONE = "discone"
DISCONE_CONE_ID_PREFIX = "discone-cone-"
DISCONE_DISC_ID_PREFIX = "discone-disc-"
DISCONE_FEED_ID = "discone-feed"
MIN_WIRES = 4
MAX_WIRES = 32
DEFAULT_HALF_ANGLE_DEG = 30.0


def discone_parameters(
    *,
    frequency_hz: float = 145_000_000.0,
    cone_height_m: float | None = None,
    cone_radius_m: float | None = None,
    disc_radius_m: float | None = None,
    base_height_m: float = 0.5,
    disc_gap_m: float = 0.01,
    wire_count: int = 12,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> DisconeParameters:
    """Return a quarter-wave-slant cone with a larger top disc."""

    from ..design.formulas import quarter_wave_length_m

    slant = quarter_wave_length_m(frequency_hz)
    half_angle = units.degrees_to_radians(DEFAULT_HALF_ANGLE_DEG)
    return DisconeParameters(
        frequency_hz=frequency_hz,
        cone_height_m=(slant * math.cos(half_angle) if cone_height_m is None else cone_height_m),
        cone_radius_m=(slant * math.sin(half_angle) if cone_radius_m is None else cone_radius_m),
        disc_radius_m=slant * 0.7 if disc_radius_m is None else disc_radius_m,
        base_height_m=base_height_m,
        disc_gap_m=disc_gap_m,
        wire_count=wire_count,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


@dataclass(frozen=True, slots=True)
class DisconeParameters:
    """A radial-wire cone and disc with a source across the feed gap.

    The cone opens downward from the apex, and the disc sits above the apex
    with a small gap. The source is on a short vertical wire across that gap.
    This is a wire approximation of a solid discone: the skirt, disc, coax, and
    mast are not modeled as solid surfaces.
    """

    frequency_hz: float
    cone_height_m: float
    cone_radius_m: float
    disc_radius_m: float
    base_height_m: float = 0.5
    disc_gap_m: float = 0.01
    wire_count: int = 12
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.cone_height_m, name="cone_height_m")
        ensure_positive(self.cone_radius_m, name="cone_radius_m")
        ensure_positive(self.disc_radius_m, name="disc_radius_m")
        ensure_non_negative(self.base_height_m, name="base_height_m")
        ensure_positive(self.disc_gap_m, name="disc_gap_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if not MIN_WIRES <= self.wire_count <= MAX_WIRES:
            raise ValueError(f"wire_count must be between {MIN_WIRES} and {MAX_WIRES}")
        if (
            min(
                self.cone_slant_m,
                self.cone_radius_m,
                self.disc_radius_m,
                self.disc_gap_m,
            )
            <= 2.0 * self.wire_radius_m
        ):
            raise ValueError("all discone dimensions must exceed the conductor diameter")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return "Discone"

    @property
    def apex_height_m(self) -> float:
        return self.base_height_m + self.cone_height_m

    @property
    def disc_height_m(self) -> float:
        return self.apex_height_m + self.disc_gap_m

    @property
    def top_height_m(self) -> float:
        return self.disc_height_m

    @property
    def cone_slant_m(self) -> float:
        return math.hypot(self.cone_height_m, self.cone_radius_m)

    @property
    def overall_diameter_m(self) -> float:
        return 2.0 * max(self.cone_radius_m, self.disc_radius_m)

    @property
    def feed_height_m(self) -> float:
        return self.apex_height_m + self.disc_gap_m / 2.0

    @property
    def total_conductor_length_m(self) -> float:
        return (
            self.wire_count * self.cone_slant_m
            + self.wire_count * self.disc_radius_m
            + self.disc_gap_m
        )

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        def point(radius_m: float, bearing: float, z_m: float) -> Point3D:
            local_x = radius_m * math.cos(bearing)
            local_y = radius_m * math.sin(bearing)
            return Point3D(
                x_m=local_x * cos_angle - local_y * sin_angle,
                y_m=local_x * sin_angle + local_y * cos_angle,
                z_m=z_m,
            )

        apex = Point3D(0.0, 0.0, self.apex_height_m)
        hub = Point3D(0.0, 0.0, self.disc_height_m)
        wires: list[Wire] = [
            Wire(
                id=DISCONE_FEED_ID,
                start=apex,
                end=hub,
                radius_m=self.wire_radius_m,
                material=self.material,
            )
        ]
        for index in range(self.wire_count):
            bearing = 2.0 * math.pi * index / self.wire_count
            wires.append(
                Wire(
                    id=f"{DISCONE_CONE_ID_PREFIX}{index}",
                    start=apex,
                    end=point(self.cone_radius_m, bearing, self.base_height_m),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            wires.append(
                Wire(
                    id=f"{DISCONE_DISC_ID_PREFIX}{index}",
                    start=hub,
                    end=point(self.disc_radius_m, bearing, self.disc_height_m),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
        return AntennaModel(
            name=name or self.template_name,
            design_frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(DISCONE_FEED_ID, self.disc_gap_m / 2.0),
            environment=Environment(ground=self.ground),
        )
