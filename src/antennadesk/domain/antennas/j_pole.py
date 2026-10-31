# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""J-pole and Slim-Jim vertical antennas."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_J_POLE = "j_pole"


@dataclass(frozen=True, slots=True)
class JPoleParameters:
    """A vertical radiator with a parallel matching stub.

    ``folded`` selects the Slim-Jim variant label. Both variants keep the
    radiator and stub separated at the top, with a gap between their ends.
    """

    frequency_hz: float
    radiator_height_m: float
    stub_length_m: float
    spacing_m: float
    feed_offset_m: float = 0.1
    gap_m: float = 0.01
    base_height_m: float = 0.25
    folded: bool = False
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.radiator_height_m, name="radiator_height_m")
        ensure_positive(self.stub_length_m, name="stub_length_m")
        ensure_positive(self.spacing_m, name="spacing_m")
        ensure_non_negative(self.feed_offset_m, name="feed_offset_m")
        ensure_positive(self.base_height_m, name="base_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if self.feed_offset_m >= self.stub_length_m:
            raise ValueError("feed_offset_m must be shorter than the stub")
        if not self.folded and self.radiator_height_m < self.stub_length_m:
            raise ValueError("radiator_height_m must be at least the stub length")
        if self.folded and self.gap_m <= 0.0:
            raise ValueError("gap_m must be positive for a Slim Jim")

    @property
    def template_name(self) -> str:
        return "Slim Jim" if self.folded else "J Pole"

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name or self.template_name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        base_z = self.base_height_m
        base_left = Point3D(0.0, 0.0, base_z)
        base_right = Point3D(self.spacing_m, 0.0, base_z)
        if not self.folded:
            top_left = Point3D(0.0, 0.0, base_z + self.radiator_height_m)
            top_right = Point3D(self.spacing_m, 0.0, base_z + self.stub_length_m)
            wires = [
                Wire("radiator", base_left, top_left, self.wire_radius_m, self.material),
                Wire("stub", base_right, top_right, self.wire_radius_m, self.material),
                Wire("base-connector", base_left, base_right, self.wire_radius_m, self.material),
            ]
            feed = FeedPoint("stub", self.feed_offset_m)
        else:
            gap_bottom = Point3D(self.spacing_m, 0.0, base_z + self.stub_length_m)
            gap_top = Point3D(
                self.spacing_m,
                0.0,
                base_z + self.stub_length_m + self.gap_m,
            )
            top_left = Point3D(
                0.0,
                0.0,
                gap_top.z_m + self.radiator_height_m,
            )
            top_right = Point3D(self.spacing_m, 0.0, top_left.z_m)
            wires = [
                Wire("left-leg", base_left, top_left, self.wire_radius_m, self.material),
                Wire("right-upper", top_right, gap_top, self.wire_radius_m, self.material),
                Wire("right-lower", gap_bottom, base_right, self.wire_radius_m, self.material),
                Wire("base-connector", base_left, base_right, self.wire_radius_m, self.material),
                Wire("top-connector", top_left, top_right, self.wire_radius_m, self.material),
            ]
            feed = FeedPoint("right-lower", self.stub_length_m)
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=feed,
            ground=self.ground,
            generator_id="slim_jim" if self.folded else "j_pole",
            generator_name=self.template_name,
        )
