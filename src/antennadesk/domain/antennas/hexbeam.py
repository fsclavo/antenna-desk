# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Single-band broadband hexbeam with bent-wire elements."""

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

ANTENNA_TYPE_HEXBEAM = "hexbeam"
HEXBEAM_FEED_ID = "hexbeam-feed"
HEXBEAM_DRIVER_ID_PREFIX = "hexbeam-driver-"
HEXBEAM_REFLECTOR_ID_PREFIX = "hexbeam-reflector-"

# Steve Hunt, G3TXQ, "A Broadband Hexbeam", antenneX no. 128, December 2007,
# as restated by the CyberDev broadband-hexbeam calculator: 20 m reference at
# 14.184 MHz with a 219 in driver half, 207 in reflector half, 24 in tip gap,
# and a 130 in spreader (turning radius).
PUBLISHED_HEXBEAM_FREQUENCY_HZ = 14_184_000.0
PUBLISHED_DRIVER_HALF_M = 219.0 * 0.0254
PUBLISHED_REFLECTOR_HALF_M = 207.0 * 0.0254
PUBLISHED_TIP_GAP_M = 24.0 * 0.0254
PUBLISHED_TURNING_RADIUS_M = 130.0 * 0.0254
DEFAULT_FEED_GAP_M = 1.25 * 0.0254
DEFAULT_ELEMENT_SEPARATION_M = 0.05


def published_hexbeam_parameters(
    *,
    frequency_hz: float = PUBLISHED_HEXBEAM_FREQUENCY_HZ,
    height_m: float = 10.0,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> HexbeamParameters:
    """Return the G3TXQ 20 m reference scaled linearly to ``frequency_hz``."""

    scale = PUBLISHED_HEXBEAM_FREQUENCY_HZ / frequency_hz
    return HexbeamParameters(
        frequency_hz=frequency_hz,
        driver_half_length_m=PUBLISHED_DRIVER_HALF_M * scale,
        reflector_half_length_m=PUBLISHED_REFLECTOR_HALF_M * scale,
        turning_radius_m=PUBLISHED_TURNING_RADIUS_M * scale,
        tip_gap_m=PUBLISHED_TIP_GAP_M * scale,
        height_m=height_m,
        feed_gap_m=DEFAULT_FEED_GAP_M * scale,
        element_separation_m=DEFAULT_ELEMENT_SEPARATION_M * scale,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


@dataclass(frozen=True, slots=True)
class HexbeamParameters:
    """A W-shaped driver and U-shaped reflector on a six-spreader frame.

    The driver wire is split into two bent halves around a small center feed
    gap. The reflector is a single U-shaped wire whose center sits just behind
    the driver center. The apex of each half lies on the 60-degree spreader
    ray at the turning radius. The tip half-span is derived from the published
    wire half-length, so the wire path is preserved rather than forced to a
    fixed hexagon vertex.

    The model is a wire approximation of a single band. The support frame,
    spreader sag, feed balun, and multi-band nesting are not modeled.
    """

    frequency_hz: float
    driver_half_length_m: float
    reflector_half_length_m: float
    turning_radius_m: float
    tip_gap_m: float
    height_m: float = 10.0
    feed_gap_m: float = DEFAULT_FEED_GAP_M
    element_separation_m: float = DEFAULT_ELEMENT_SEPARATION_M
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.driver_half_length_m, name="driver_half_length_m")
        ensure_positive(self.reflector_half_length_m, name="reflector_half_length_m")
        ensure_positive(self.turning_radius_m, name="turning_radius_m")
        ensure_positive(self.tip_gap_m, name="tip_gap_m")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_positive(self.feed_gap_m, name="feed_gap_m")
        ensure_non_negative(self.element_separation_m, name="element_separation_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if self.driver_half_length_m <= 1.5 * self.turning_radius_m:
            raise ValueError("driver_half_length_m must exceed 1.5 times turning_radius_m")
        if self.reflector_half_length_m <= self.turning_radius_m + abs(
            self.turning_radius_m / 2.0 - self.tip_gap_m
        ):
            raise ValueError(
                "reflector_half_length_m is too short for the turning radius and tip gap"
            )
        if self.tip_gap_m <= 2.0 * self.wire_radius_m:
            raise ValueError("tip_gap_m must exceed the conductor diameter")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return "Hexbeam"

    @property
    def driver_tip_half_span_m(self) -> float:
        apex_half = self.turning_radius_m * math.sqrt(3.0) / 2.0
        tip_leg = self.driver_half_length_m - self.turning_radius_m
        offset = math.sqrt(max(0.0, tip_leg**2 - (self.turning_radius_m / 2.0) ** 2))
        return apex_half + offset

    @property
    def reflector_tip_half_span_m(self) -> float:
        apex_half = self.turning_radius_m * math.sqrt(3.0) / 2.0
        tip_leg = self.reflector_half_length_m - self.turning_radius_m
        horizontal = self.turning_radius_m / 2.0 - self.tip_gap_m
        offset = math.sqrt(max(0.0, tip_leg**2 - horizontal**2))
        return apex_half + offset

    @property
    def overall_span_m(self) -> float:
        return 2.0 * max(
            self.driver_tip_half_span_m,
            self.reflector_tip_half_span_m,
        )

    @property
    def turning_diameter_m(self) -> float:
        return 2.0 * self.turning_radius_m

    @property
    def total_conductor_length_m(self) -> float:
        return 2.0 * (self.driver_half_length_m + self.reflector_half_length_m) + self.feed_gap_m

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        def point(local_x_m: float, local_y_m: float, z_m: float) -> Point3D:
            return Point3D(
                x_m=local_x_m * cos_angle - local_y_m * sin_angle,
                y_m=local_x_m * sin_angle + local_y_m * cos_angle,
                z_m=z_m,
            )

        driver_x = self.element_separation_m / 2.0
        reflector_x = -self.element_separation_m / 2.0
        apex_x = self.turning_radius_m / 2.0
        apex_y = self.turning_radius_m * math.sqrt(3.0) / 2.0
        driver_center_left = point(driver_x - self.feed_gap_m / 2.0, 0.0, self.height_m)
        driver_center_right = point(driver_x + self.feed_gap_m / 2.0, 0.0, self.height_m)
        reflector_center = point(reflector_x, 0.0, self.height_m)

        wires: list[Wire] = [
            Wire(
                id=HEXBEAM_FEED_ID,
                start=driver_center_left,
                end=driver_center_right,
                radius_m=self.wire_radius_m,
                material=self.material,
            )
        ]
        for side, sign in (("left", 1.0), ("right", -1.0)):
            driver_apex = point(driver_x + apex_x, sign * apex_y, self.height_m)
            driver_tip = point(
                driver_x,
                sign * self.driver_tip_half_span_m,
                self.height_m,
            )
            center = driver_center_left if sign > 0.0 else driver_center_right
            wires.append(
                Wire(
                    id=f"{HEXBEAM_DRIVER_ID_PREFIX}{side}-inner",
                    start=center,
                    end=driver_apex,
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            wires.append(
                Wire(
                    id=f"{HEXBEAM_DRIVER_ID_PREFIX}{side}-tip",
                    start=driver_apex,
                    end=driver_tip,
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            reflector_apex = point(reflector_x - apex_x, sign * apex_y, self.height_m)
            reflector_tip = point(
                reflector_x - self.tip_gap_m,
                sign * self.reflector_tip_half_span_m,
                self.height_m,
            )
            wires.append(
                Wire(
                    id=f"{HEXBEAM_REFLECTOR_ID_PREFIX}{side}-inner",
                    start=reflector_center,
                    end=reflector_apex,
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            wires.append(
                Wire(
                    id=f"{HEXBEAM_REFLECTOR_ID_PREFIX}{side}-tip",
                    start=reflector_apex,
                    end=reflector_tip,
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
        return AntennaModel(
            name=name or self.template_name,
            design_frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(HEXBEAM_FEED_ID, self.feed_gap_m / 2.0),
            environment=Environment(ground=self.ground),
        )
