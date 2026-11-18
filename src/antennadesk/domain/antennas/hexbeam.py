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
from .feed import FeedPoint, Source
from .geometry import Point3D
from .materials import ALUMINUM, COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_HEXBEAM = "hexbeam"
HEXBEAM_FEED_ID = "hexbeam-feed"
HEXBEAM_DRIVER_ID_PREFIX = "hexbeam-driver-"
HEXBEAM_REFLECTOR_ID_PREFIX = "hexbeam-reflector-"
HEXBEAM_REFLECTOR_REAR_ID = "hexbeam-reflector-rear"

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
DEFAULT_ELEMENT_SEPARATION_M = 0.0

_FRONT_HALF_ANGLE_RAD = math.radians(30.0)
_FRONT_COS = math.cos(_FRONT_HALF_ANGLE_RAD)
_FRONT_SIN = math.sin(_FRONT_HALF_ANGLE_RAD)


class HexbeamGeometryError(ValueError):
    """A published HexBeam row that cannot be fitted to the hexagonal frame."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field = field


@dataclass(frozen=True, slots=True)
class HexbeamFrameGeometry:
    """The upper half of the reconstructed six-spreader wire path.

    Coordinates are local to the boom axis: +x points forward, +y points to
    the ``left`` side, and the frame center is the origin. The lower half is the
    mirror image across the boom axis.
    """

    front_vertex: tuple[float, float]
    lateral_vertex: tuple[float, float]
    rear_vertex: tuple[float, float]
    rear_midpoint: tuple[float, float]
    driver_knee: tuple[float, float]
    driver_tip: tuple[float, float]
    reflector_end: tuple[float, float]
    end_extension_m: float
    knee_radius_m: float
    driver_tip_leg_m: float


def hexbeam_frame_geometry(
    *,
    turning_radius_m: float,
    driver_half_length_m: float,
    reflector_half_length_m: float,
    tip_gap_m: float,
) -> HexbeamFrameGeometry:
    """Fit the published wire lengths to the six-spreader frame.

    The driver half-length is measured from the feed center to the driver tip.
    The reflector half-length is measured from the middle of the rear side to
    the reflector end. Both paths stay at or inside the turning radius.
    """

    for name, value in (
        ("turning_radius_m", turning_radius_m),
        ("driver_half_length_m", driver_half_length_m),
        ("reflector_half_length_m", reflector_half_length_m),
        ("tip_gap_m", tip_gap_m),
    ):
        if not math.isfinite(value) or value <= 0.0:
            raise HexbeamGeometryError(name, f"{name} must be positive")

    radius = turning_radius_m
    end_extension = reflector_half_length_m - 1.5 * radius
    if end_extension < 0.0:
        raise HexbeamGeometryError(
            "reflector_half_length_m",
            "reflector_half_length_m is too short for the turning radius",
        )
    if end_extension + tip_gap_m > radius:
        raise HexbeamGeometryError(
            "tip_gap_m",
            "tip_gap_m places the driver tip past the front spreader",
        )

    front_vertex = (radius * _FRONT_COS, radius * _FRONT_SIN)
    lateral_vertex = (0.0, radius)
    rear_vertex = (-radius * _FRONT_COS, radius * _FRONT_SIN)
    rear_midpoint = (-radius * _FRONT_COS, 0.0)

    side_x = front_vertex[0] - lateral_vertex[0]
    side_y = front_vertex[1] - lateral_vertex[1]
    reflector_end = (
        lateral_vertex[0] + end_extension * side_x / radius,
        lateral_vertex[1] + end_extension * side_y / radius,
    )
    driver_tip = (
        lateral_vertex[0] + (end_extension + tip_gap_m) * side_x / radius,
        lateral_vertex[1] + (end_extension + tip_gap_m) * side_y / radius,
    )

    tip_dot = driver_tip[0] * _FRONT_COS + driver_tip[1] * _FRONT_SIN
    denominator = 2.0 * (driver_half_length_m - tip_dot)
    if abs(denominator) < 1e-12:
        raise HexbeamGeometryError(
            "driver_half_length_m",
            "driver_half_length_m has no valid knee on the front spreader",
        )
    knee_radius = (driver_half_length_m**2 - driver_tip[0] ** 2 - driver_tip[1] ** 2) / denominator
    if not math.isfinite(knee_radius) or knee_radius < 0.0 or knee_radius > radius:
        raise HexbeamGeometryError(
            "driver_half_length_m",
            "driver_half_length_m has no valid knee on the front spreader",
        )
    knee = (knee_radius * _FRONT_COS, knee_radius * _FRONT_SIN)
    tip_leg = math.hypot(driver_tip[0] - knee[0], driver_tip[1] - knee[1])
    if not math.isclose(knee_radius + tip_leg, driver_half_length_m, abs_tol=1e-9):
        raise HexbeamGeometryError(
            "driver_half_length_m",
            "driver_half_length_m has no valid knee on the front spreader",
        )

    return HexbeamFrameGeometry(
        front_vertex=front_vertex,
        lateral_vertex=lateral_vertex,
        rear_vertex=rear_vertex,
        rear_midpoint=rear_midpoint,
        driver_knee=knee,
        driver_tip=driver_tip,
        reflector_end=reflector_end,
        end_extension_m=end_extension,
        knee_radius_m=knee_radius,
        driver_tip_leg_m=tip_leg,
    )


@dataclass(frozen=True, slots=True)
class HexbeamBand:
    """One nested driver/reflector pair on the shared six-spreader frame."""

    label: str
    frequency_hz: float
    driver_half_length_m: float
    reflector_half_length_m: float
    tip_gap_m: float
    feed_gap_m: float = DEFAULT_FEED_GAP_M
    vertical_offset_m: float = 0.0

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("HexbeamBand.label must not be empty")
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.driver_half_length_m, name="driver_half_length_m")
        ensure_positive(self.reflector_half_length_m, name="reflector_half_length_m")
        ensure_positive(self.tip_gap_m, name="tip_gap_m")
        ensure_positive(self.feed_gap_m, name="feed_gap_m")
        ensure_non_negative(self.vertical_offset_m, name="vertical_offset_m")


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
    """An M-shaped driver and a rear U-shaped reflector on a hexagon frame.

    The driver wire is split into two bent halves around a small center feed
    gap. Each half runs from the feed to a knee on the front spreader, then
    along a chord to the driver tip near the lateral vertex. The reflector is
    one wire around the rear three sides, with its midpoint at the rear side.
    A 24 in tip spacer separates each driver tip from the reflector end.

    ``driver_half_length_m`` is measured from the feed center to the tip.
    ``reflector_half_length_m`` is measured from the rear midpoint to the
    reflector end. ``element_separation_m`` is a small rearward fore-aft trim
    of the reflector, not a center-to-center element spacing.

    ``bands`` optionally carries one to five nested pairs. The first band is the
    largest/lowest-frequency element, defines the shared turning radius, and
    must match the scalar fields. ``height_m`` is the reference plane of the
    lowest band; each band adds its vertical offset. Additional bands are
    excited by ideal unit-amplitude, zero-phase sources.

    The model is a wire approximation. The support frame, spreader sag, feed
    harness, balun, and inter-band coupling are not modeled.
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
    material: ConductorMaterial = ALUMINUM
    ground: GroundModel = FREE_SPACE
    bands: tuple[HexbeamBand, ...] = ()

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
        if self.tip_gap_m <= 2.0 * self.wire_radius_m:
            raise ValueError("tip_gap_m must exceed the conductor diameter")
        hexbeam_frame_geometry(
            turning_radius_m=self.turning_radius_m,
            driver_half_length_m=self.driver_half_length_m,
            reflector_half_length_m=self.reflector_half_length_m,
            tip_gap_m=self.tip_gap_m,
        )
        if self.bands:
            if len(self.bands) > 5:
                raise ValueError("HexbeamParameters supports at most 5 bands")
            labels = [band.label.casefold() for band in self.bands]
            if len(set(labels)) != len(labels):
                raise ValueError("Hexbeam band labels must be unique")
            frequencies = [band.frequency_hz for band in self.bands]
            if len(set(frequencies)) != len(frequencies):
                raise ValueError("Hexbeam band frequencies must be unique")
            primary = self.bands[0]
            if any(band.frequency_hz < primary.frequency_hz for band in self.bands):
                raise ValueError(
                    "the first hexbeam band must be the lowest frequency (largest element)"
                )
            for band in self.bands:
                hexbeam_frame_geometry(
                    turning_radius_m=self.band_radius_m(band),
                    driver_half_length_m=band.driver_half_length_m,
                    reflector_half_length_m=band.reflector_half_length_m,
                    tip_gap_m=band.tip_gap_m,
                )
            for name, scalar, band_value in (
                ("frequency_hz", self.frequency_hz, primary.frequency_hz),
                ("driver_half_length_m", self.driver_half_length_m, primary.driver_half_length_m),
                (
                    "reflector_half_length_m",
                    self.reflector_half_length_m,
                    primary.reflector_half_length_m,
                ),
                ("tip_gap_m", self.tip_gap_m, primary.tip_gap_m),
                ("feed_gap_m", self.feed_gap_m, primary.feed_gap_m),
            ):
                if not math.isclose(scalar, band_value, rel_tol=1e-9, abs_tol=1e-12):
                    raise ValueError(f"{name} must match the primary hexbeam band")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return "Hexbeam"

    @property
    def reference_frequency_hz(self) -> float:
        return self.resolved_bands[0].frequency_hz

    def band_radius_m(self, band: HexbeamBand) -> float:
        """Return the band's effective spreader radius.

        The largest band defines the shared turning radius. Higher bands use the
        same linear frequency-scaling rule as the published single-band
        reference, so their paths stay nested inside the frame.
        """

        return self.turning_radius_m * self.reference_frequency_hz / band.frequency_hz

    def band_frame(self, band: HexbeamBand) -> HexbeamFrameGeometry:
        return hexbeam_frame_geometry(
            turning_radius_m=self.band_radius_m(band),
            driver_half_length_m=band.driver_half_length_m,
            reflector_half_length_m=band.reflector_half_length_m,
            tip_gap_m=band.tip_gap_m,
        )

    @property
    def frame(self) -> HexbeamFrameGeometry:
        return self.band_frame(self.resolved_bands[0])

    @property
    def resolved_bands(self) -> tuple[HexbeamBand, ...]:
        if self.bands:
            return self.bands
        return (
            HexbeamBand(
                label="primary",
                frequency_hz=self.frequency_hz,
                driver_half_length_m=self.driver_half_length_m,
                reflector_half_length_m=self.reflector_half_length_m,
                tip_gap_m=self.tip_gap_m,
                feed_gap_m=self.feed_gap_m,
                vertical_offset_m=0.0,
            ),
        )

    @property
    def driver_tip_half_span_m(self) -> float:
        return self.frame.driver_tip[1]

    @property
    def reflector_tip_half_span_m(self) -> float:
        return self.frame.reflector_end[1]

    @property
    def overall_span_m(self) -> float:
        return 2.0 * self.turning_radius_m

    @property
    def turning_diameter_m(self) -> float:
        return 2.0 * self.turning_radius_m

    @property
    def total_conductor_length_m(self) -> float:
        return sum(
            2.0 * (band.driver_half_length_m + band.reflector_half_length_m) + band.feed_gap_m
            for band in self.resolved_bands
        )

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        trim = self.element_separation_m
        wires: list[Wire] = []
        sources: list[Source] = []
        primary_feed_id = HEXBEAM_FEED_ID
        primary_feed_offset = self.feed_gap_m / 2.0

        for index, band in enumerate(self.resolved_bands):
            prefix = "hexbeam-" if index == 0 else f"hexbeam-band{index + 1}-"
            feed_id = f"{prefix}feed"
            z_m = self.height_m + band.vertical_offset_m
            frame = self.band_frame(band)

            def point(
                local_x_m: float,
                local_y_m: float,
                band_z_m: float = z_m,
            ) -> Point3D:
                return Point3D(
                    x_m=local_x_m * cos_angle - local_y_m * sin_angle,
                    y_m=local_x_m * sin_angle + local_y_m * cos_angle,
                    z_m=band_z_m,
                )

            def mirror(local_y_m: float) -> float:
                return -local_y_m

            def reflector_point(local_x_m: float, local_y_m: float) -> Point3D:
                return point(local_x_m - trim, local_y_m)

            driver_center_left = point(-band.feed_gap_m / 2.0, 0.0)
            driver_center_right = point(band.feed_gap_m / 2.0, 0.0)
            knee_left = frame.driver_knee
            knee_right = (knee_left[0], mirror(knee_left[1]))
            tip_left = frame.driver_tip
            tip_right = (tip_left[0], mirror(tip_left[1]))
            lateral_left = frame.lateral_vertex
            lateral_right = (lateral_left[0], mirror(lateral_left[1]))
            rear_left = frame.rear_vertex
            rear_right = (rear_left[0], mirror(rear_left[1]))
            end_left = frame.reflector_end
            end_right = (end_left[0], mirror(end_left[1]))

            wires.append(
                Wire(
                    id=feed_id,
                    start=driver_center_left,
                    end=driver_center_right,
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            for side, center, knee, tip in (
                ("left", driver_center_left, knee_left, tip_left),
                ("right", driver_center_right, knee_right, tip_right),
            ):
                wires.append(
                    Wire(
                        id=f"{prefix}driver-{side}-inner",
                        start=center,
                        end=point(knee[0], knee[1]),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    )
                )
                wires.append(
                    Wire(
                        id=f"{prefix}driver-{side}-tip",
                        start=point(knee[0], knee[1]),
                        end=point(tip[0], tip[1]),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    )
                )

            wires.extend(
                [
                    Wire(
                        id=f"{prefix}reflector-left-tip",
                        start=reflector_point(end_left[0], end_left[1]),
                        end=reflector_point(lateral_left[0], lateral_left[1]),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                    Wire(
                        id=f"{prefix}reflector-left-inner",
                        start=reflector_point(lateral_left[0], lateral_left[1]),
                        end=reflector_point(rear_left[0], rear_left[1]),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                    Wire(
                        id=f"{prefix}reflector-rear",
                        start=reflector_point(rear_left[0], rear_left[1]),
                        end=reflector_point(rear_right[0], rear_right[1]),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                    Wire(
                        id=f"{prefix}reflector-right-inner",
                        start=reflector_point(lateral_right[0], lateral_right[1]),
                        end=reflector_point(rear_right[0], rear_right[1]),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                    Wire(
                        id=f"{prefix}reflector-right-tip",
                        start=reflector_point(end_right[0], end_right[1]),
                        end=reflector_point(lateral_right[0], lateral_right[1]),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                ]
            )
            if index == 0:
                primary_feed_id = feed_id
                primary_feed_offset = band.feed_gap_m / 2.0
            else:
                sources.append(Source(feed_id, band.feed_gap_m / 2.0))

        return AntennaModel(
            name=name or self.template_name,
            design_frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(primary_feed_id, primary_feed_offset),
            environment=Environment(ground=self.ground),
            sources=tuple(sources),
        )
