# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Half-square and bobtail-curtain self-contained vertical arrays."""

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

ANTENNA_TYPE_HALF_SQUARE = "half_square"
ANTENNA_TYPE_BOBTAIL_CURTAIN = "bobtail_curtain"

LEFT_VERTICAL_ID = "left-vertical"
TOP_HORIZONTAL_ID = "top-horizontal"
RIGHT_VERTICAL_ID = "right-vertical"
LEFT_TOP_ID = "left-top"
RIGHT_TOP_ID = "right-top"
CENTER_VERTICAL_ID = "center-vertical"

# L. B. Cebik, W4RNL, "SCVs: A Family Album", Table 1, 7.15 MHz, #12 AWG
# copper wire. The table dimensions are free-space, maximum-gain starting
# points; scaling them with frequency is an application heuristic.
SCV_REFERENCE_FREQUENCY_HZ = 7_150_000.0
HALF_SQUARE_REFERENCE_HORIZONTAL_LENGTH_M = 62.4 * 0.3048
HALF_SQUARE_REFERENCE_VERTICAL_HEIGHT_M = 39.0 * 0.3048
BOBTAIL_REFERENCE_HORIZONTAL_LENGTH_M = 125.0 * 0.3048
BOBTAIL_REFERENCE_VERTICAL_HEIGHT_M = 38.0 * 0.3048


class ScvKind(StrEnum):
    """The two catalog variants of the self-contained vertical array."""

    HALF_SQUARE = "half_square"
    BOBTAIL_CURTAIN = "bobtail_curtain"

    @property
    def vertical_count(self) -> int:
        return 2 if self is ScvKind.HALF_SQUARE else 3

    @property
    def template_name(self) -> str:
        return "Half square" if self is ScvKind.HALF_SQUARE else "Bobtail curtain"

    @property
    def antenna_type(self) -> str:
        return (
            ANTENNA_TYPE_HALF_SQUARE
            if self is ScvKind.HALF_SQUARE
            else ANTENNA_TYPE_BOBTAIL_CURTAIN
        )


def scv_starting_dimensions(
    kind: ScvKind,
    frequency_hz: float,
) -> tuple[float, float]:
    """Return the published Cebik dimensions scaled to ``frequency_hz``."""

    ensure_positive(frequency_hz, name="frequency_hz")
    if kind is ScvKind.HALF_SQUARE:
        horizontal_m = HALF_SQUARE_REFERENCE_HORIZONTAL_LENGTH_M
        vertical_m = HALF_SQUARE_REFERENCE_VERTICAL_HEIGHT_M
    else:
        horizontal_m = BOBTAIL_REFERENCE_HORIZONTAL_LENGTH_M
        vertical_m = BOBTAIL_REFERENCE_VERTICAL_HEIGHT_M
    scale = SCV_REFERENCE_FREQUENCY_HZ / frequency_hz
    return horizontal_m * scale, vertical_m * scale


def scv_parameters(
    kind: ScvKind,
    frequency_hz: float,
    *,
    base_height_m: float = 2.5,
    feed_offset_m: float = 0.0,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> ScvParameters:
    """Return the published Cebik starting geometry for a variant."""

    horizontal_m, vertical_m = scv_starting_dimensions(kind, frequency_hz)
    return ScvParameters(
        frequency_hz=frequency_hz,
        kind=kind,
        horizontal_length_m=horizontal_m,
        vertical_height_m=vertical_m,
        base_height_m=base_height_m,
        feed_offset_m=feed_offset_m,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


@dataclass(frozen=True, slots=True)
class ScvParameters:
    """A horizontal top wire (or two) joining quarter-wave verticals.

    ``kind`` selects the two-vertical half square or the three-vertical
    bobtail curtain. ``horizontal_length_m`` is the overall horizontal span
    between the outer verticals, so the bobtail has two top segments of half
    that length. The array is fed at the top junction of the left vertical
    (half square) or the center vertical (bobtail); ``feed_offset_m`` moves the
    feed down the fed vertical from that junction.
    """

    frequency_hz: float
    kind: ScvKind
    horizontal_length_m: float
    vertical_height_m: float
    base_height_m: float = 2.5
    feed_offset_m: float = 0.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        object.__setattr__(self, "kind", ScvKind(self.kind))
        ensure_positive(self.horizontal_length_m, name="horizontal_length_m")
        ensure_positive(self.vertical_height_m, name="vertical_height_m")
        ensure_non_negative(self.base_height_m, name="base_height_m")
        ensure_non_negative(self.feed_offset_m, name="feed_offset_m")
        if self.feed_offset_m >= self.vertical_height_m:
            raise ValueError("feed_offset_m must be shorter than the vertical height")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return self.kind.template_name

    @property
    def vertical_count(self) -> int:
        return self.kind.vertical_count

    @property
    def horizontal_segment_count(self) -> int:
        return self.vertical_count - 1

    @property
    def horizontal_segment_m(self) -> float:
        return self.horizontal_length_m / self.horizontal_segment_count

    @property
    def top_height_m(self) -> float:
        return self.base_height_m + self.vertical_height_m

    @property
    def feed_height_m(self) -> float:
        return self.top_height_m - self.feed_offset_m

    @property
    def total_conductor_length_m(self) -> float:
        return self.vertical_count * self.vertical_height_m + self.horizontal_length_m

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name or self.template_name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        def point(local_x_m: float, z_m: float) -> Point3D:
            return Point3D(
                x_m=local_x_m * cos_angle,
                y_m=local_x_m * sin_angle,
                z_m=z_m,
            )

        bottom_z = self.base_height_m
        top_z = self.top_height_m
        span = self.horizontal_length_m
        wires: tuple[Wire, ...]
        if self.kind is ScvKind.HALF_SQUARE:
            left_bottom = point(0.0, bottom_z)
            left_top = point(0.0, top_z)
            right_top = point(span, top_z)
            right_bottom = point(span, bottom_z)
            wires = (
                Wire(
                    LEFT_VERTICAL_ID,
                    left_top,
                    left_bottom,
                    self.wire_radius_m,
                    self.material,
                ),
                Wire(
                    TOP_HORIZONTAL_ID,
                    left_top,
                    right_top,
                    self.wire_radius_m,
                    self.material,
                ),
                Wire(
                    RIGHT_VERTICAL_ID,
                    right_top,
                    right_bottom,
                    self.wire_radius_m,
                    self.material,
                ),
            )
            feed = FeedPoint(LEFT_VERTICAL_ID, self.feed_offset_m)
        else:
            center_x = span / 2.0
            left_bottom = point(0.0, bottom_z)
            left_top = point(0.0, top_z)
            center_top = point(center_x, top_z)
            right_top = point(span, top_z)
            right_bottom = point(span, bottom_z)
            center_bottom = point(center_x, bottom_z)
            wires = (
                Wire(
                    LEFT_VERTICAL_ID,
                    left_top,
                    left_bottom,
                    self.wire_radius_m,
                    self.material,
                ),
                Wire(
                    LEFT_TOP_ID,
                    left_top,
                    center_top,
                    self.wire_radius_m,
                    self.material,
                ),
                Wire(
                    RIGHT_TOP_ID,
                    center_top,
                    right_top,
                    self.wire_radius_m,
                    self.material,
                ),
                Wire(
                    RIGHT_VERTICAL_ID,
                    right_top,
                    right_bottom,
                    self.wire_radius_m,
                    self.material,
                ),
                Wire(
                    CENTER_VERTICAL_ID,
                    center_top,
                    center_bottom,
                    self.wire_radius_m,
                    self.material,
                ),
            )
            feed = FeedPoint(CENTER_VERTICAL_ID, self.feed_offset_m)
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=wires,
            feed=feed,
            ground=self.ground,
            generator_id=self.kind.value,
            generator_name=self.template_name,
        )

    @classmethod
    def from_custom_parameters(
        cls,
        parameters: CustomAntennaParameters,
    ) -> ScvParameters:
        try:
            kind = ScvKind(parameters.generator_id or "")
        except ValueError as exc:
            raise ValueError("custom parameters are not a half square or bobtail curtain") from exc
        wires = {wire.id: wire for wire in parameters.wires}
        required = (
            {LEFT_VERTICAL_ID, TOP_HORIZONTAL_ID, RIGHT_VERTICAL_ID}
            if kind is ScvKind.HALF_SQUARE
            else {
                LEFT_VERTICAL_ID,
                LEFT_TOP_ID,
                RIGHT_TOP_ID,
                RIGHT_VERTICAL_ID,
                CENTER_VERTICAL_ID,
            }
        )
        if set(wires) != required:
            raise ValueError(f"a {kind.template_name.lower()} must contain its family wires")
        left = wires[LEFT_VERTICAL_ID]
        right = wires[RIGHT_VERTICAL_ID]
        center = wires.get(CENTER_VERTICAL_ID)
        if not _is_vertical(left) or not _is_vertical(right):
            raise ValueError("the outer array elements must be vertical")
        if center is not None and not _is_vertical(center):
            raise ValueError("the bobtail center element must be vertical")
        bottom_z = min(left.start.z_m, left.end.z_m)
        top_z = max(left.start.z_m, left.end.z_m)
        if not math.isclose(bottom_z, min(right.start.z_m, right.end.z_m), abs_tol=1e-6):
            raise ValueError("the array verticals must share the same base height")
        if not math.isclose(top_z, max(right.start.z_m, right.end.z_m), abs_tol=1e-6):
            raise ValueError("the array verticals must share the same top height")
        feed_wire = wires.get(parameters.feed.wire_id)
        if feed_wire is None:
            raise ValueError("the array feed wire is missing")
        if kind is ScvKind.HALF_SQUARE:
            if parameters.feed.wire_id != LEFT_VERTICAL_ID:
                raise ValueError("the half square must be fed at the top of an outer vertical")
        elif parameters.feed.wire_id != CENTER_VERTICAL_ID:
            raise ValueError("the bobtail curtain must be fed on the center vertical")
        feed_offset_m = parameters.feed.offset_m
        if feed_offset_m >= top_z - bottom_z:
            raise ValueError("the array feed offset must be shorter than the vertical height")
        horizontal_length = math.hypot(
            right.start.x_m - left.start.x_m,
            right.start.y_m - left.start.y_m,
        )
        if horizontal_length <= 0.0:
            raise ValueError("the array horizontal span must be positive")
        azimuth = math.degrees(
            math.atan2(
                right.start.y_m - left.start.y_m,
                right.start.x_m - left.start.x_m,
            )
        )
        return cls(
            frequency_hz=parameters.frequency_hz,
            kind=kind,
            horizontal_length_m=horizontal_length,
            vertical_height_m=top_z - bottom_z,
            base_height_m=bottom_z,
            feed_offset_m=feed_offset_m,
            azimuth_deg=azimuth,
            wire_radius_m=sum(wire.radius_m for wire in parameters.wires) / len(parameters.wires),
            material=left.material,
            ground=parameters.ground,
        )


def _is_vertical(wire: Wire) -> bool:
    return (
        math.hypot(
            wire.end.x_m - wire.start.x_m,
            wire.end.y_m - wire.start.y_m,
        )
        <= 1e-9
        and abs(wire.end.z_m - wire.start.z_m) > 1e-9
    )
