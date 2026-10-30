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

    ``folded`` connects the top of the radiator to the top of the stub,
    producing a Slim-Jim style folded geometry.
    """

    frequency_hz: float
    radiator_height_m: float
    stub_length_m: float
    spacing_m: float
    feed_offset_m: float = 0.1
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
        if self.radiator_height_m < self.stub_length_m:
            raise ValueError("radiator_height_m must be at least the stub length")

    @property
    def template_name(self) -> str:
        return "Slim Jim" if self.folded else "J Pole"

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name or self.template_name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        base_z = self.base_height_m
        base_left = Point3D(0.0, 0.0, base_z)
        base_right = Point3D(self.spacing_m, 0.0, base_z)
        top_left = Point3D(0.0, 0.0, base_z + self.radiator_height_m)
        top_right = Point3D(self.spacing_m, 0.0, base_z + self.stub_length_m)
        wires = [
            Wire(
                id="radiator",
                start=base_left,
                end=top_left,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="stub",
                start=base_right,
                end=top_right,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="base-connector",
                start=base_left,
                end=base_right,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
        ]
        if self.folded:
            wires.append(
                Wire(
                    id="top-connector",
                    start=top_left,
                    end=top_right,
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint("stub", self.feed_offset_m),
            ground=self.ground,
            generator_id="slim_jim" if self.folded else "j_pole",
            generator_name=self.template_name,
        )
