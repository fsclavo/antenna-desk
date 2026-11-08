# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Two- or three-element cubical quad beam with square loops."""

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

ANTENNA_TYPE_QUAD_BEAM = "quad_beam"
QUAD_BEAM_ID_PREFIX = "quad-beam-element-"
MIN_ELEMENTS = 2
MAX_ELEMENTS = 3
MIN_REFLECTOR_SCALE = 1.0
MAX_REFLECTOR_SCALE = 1.2
MIN_DIRECTOR_SCALE = 0.8
MAX_DIRECTOR_SCALE = 1.0
DRIVEN_ELEMENT_INDEX = 1
DRIVEN_SIDE_INDEX = 3


def quad_beam_parameters(
    *,
    frequency_hz: float = 14_100_000.0,
    element_count: int = 2,
    loop_side_m: float | None = None,
    reflector_spacing_m: float | None = None,
    director_spacing_m: float | None = None,
    height_m: float | None = None,
    reflector_scale: float = 1.05,
    director_scale: float = 0.95,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> QuadBeamParameters:
    """Return a quarter-wave-side quad beam with fifth-wave spacing."""

    from ..design.formulas import quarter_wave_length_m, wavelength_m

    quarter = quarter_wave_length_m(frequency_hz)
    wavelength = wavelength_m(frequency_hz)
    return QuadBeamParameters(
        frequency_hz=frequency_hz,
        element_count=element_count,
        loop_side_m=quarter if loop_side_m is None else loop_side_m,
        reflector_spacing_m=(
            wavelength * 0.2 if reflector_spacing_m is None else reflector_spacing_m
        ),
        director_spacing_m=(wavelength * 0.2 if director_spacing_m is None else director_spacing_m),
        height_m=wavelength * 0.25 if height_m is None else height_m,
        reflector_scale=reflector_scale,
        director_scale=director_scale,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


@dataclass(frozen=True, slots=True)
class QuadBeamParameters:
    """Square-loop beam with a reflector, driven loop, and optional director.

    Every loop lies in a vertical plane across the boom. The driven loop is in
    the middle position, the reflector is behind it, and the optional director
    is in front. The feed is at the midpoint of the left vertical side of the
    driven loop; the family radiates mainly horizontal polarization. The
    quarter-wave side and fifth-wave spacing are starting heuristics, not
    published gain or impedance references.
    """

    frequency_hz: float
    loop_side_m: float
    reflector_spacing_m: float
    height_m: float
    element_count: int = MIN_ELEMENTS
    director_spacing_m: float = 0.0
    reflector_scale: float = 1.05
    director_scale: float = 0.95
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.loop_side_m, name="loop_side_m")
        ensure_positive(self.reflector_spacing_m, name="reflector_spacing_m")
        ensure_non_negative(self.height_m, name="height_m")
        if not MIN_ELEMENTS <= self.element_count <= MAX_ELEMENTS:
            raise ValueError(f"element_count must be between {MIN_ELEMENTS} and {MAX_ELEMENTS}")
        if self.element_count == MAX_ELEMENTS:
            ensure_positive(self.director_spacing_m, name="director_spacing_m")
        else:
            ensure_non_negative(self.director_spacing_m, name="director_spacing_m")
        if not MIN_REFLECTOR_SCALE <= self.reflector_scale <= MAX_REFLECTOR_SCALE:
            raise ValueError(
                f"reflector_scale must be between {MIN_REFLECTOR_SCALE} and {MAX_REFLECTOR_SCALE}"
            )
        if not MIN_DIRECTOR_SCALE <= self.director_scale <= MAX_DIRECTOR_SCALE:
            raise ValueError(
                f"director_scale must be between {MIN_DIRECTOR_SCALE} and {MAX_DIRECTOR_SCALE}"
            )
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if (
            min(
                self.loop_side_m,
                self.reflector_side_m,
                self.director_side_m if self.element_count == MAX_ELEMENTS else self.loop_side_m,
            )
            <= 2.0 * self.wire_radius_m
        ):
            raise ValueError("loop side must exceed the conductor diameter")
        if self.reflector_spacing_m <= 2.0 * self.wire_radius_m:
            raise ValueError("reflector spacing must exceed the conductor diameter")
        if (
            self.element_count == MAX_ELEMENTS
            and self.director_spacing_m <= 2.0 * self.wire_radius_m
        ):
            raise ValueError("director spacing must exceed the conductor diameter")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return "Quad beam"

    @property
    def reflector_side_m(self) -> float:
        return self.loop_side_m * self.reflector_scale

    @property
    def director_side_m(self) -> float:
        return self.loop_side_m * self.director_scale

    @property
    def element_sides_m(self) -> tuple[float, ...]:
        if self.element_count == MAX_ELEMENTS:
            return (self.reflector_side_m, self.loop_side_m, self.director_side_m)
        return (self.reflector_side_m, self.loop_side_m)

    @property
    def element_positions_m(self) -> tuple[float, ...]:
        if self.element_count == MAX_ELEMENTS:
            return (
                0.0,
                self.reflector_spacing_m,
                self.reflector_spacing_m + self.director_spacing_m,
            )
        return (0.0, self.reflector_spacing_m)

    @property
    def boom_length_m(self) -> float:
        positions = self.element_positions_m
        return positions[-1] - positions[0]

    @property
    def driven_position_m(self) -> float:
        return self.element_positions_m[DRIVEN_ELEMENT_INDEX]

    @property
    def feed_height_m(self) -> float:
        return self.height_m + self.loop_side_m / 2.0

    @property
    def total_conductor_length_m(self) -> float:
        return sum(4.0 * side for side in self.element_sides_m)

    @property
    def driven_wire_id(self) -> str:
        return _side_id(DRIVEN_ELEMENT_INDEX, DRIVEN_SIDE_INDEX)

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

        wires: list[Wire] = []
        for index, (position, side) in enumerate(
            zip(self.element_positions_m, self.element_sides_m, strict=True)
        ):
            half = side / 2.0
            bottom = self.height_m
            top = self.height_m + side
            corners = (
                (position, -half, bottom),
                (position, half, bottom),
                (position, half, top),
                (position, -half, top),
            )
            for side_index in range(4):
                start = corners[side_index]
                end = corners[(side_index + 1) % 4]
                wires.append(
                    Wire(
                        id=_side_id(index, side_index),
                        start=point(*start),
                        end=point(*end),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    )
                )
        return AntennaModel(
            name=name or self.template_name,
            design_frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(
                wire_id=self.driven_wire_id,
                offset_m=self.loop_side_m / 2.0,
            ),
            environment=Environment(ground=self.ground),
        )


def _side_id(element_index: int, side_index: int) -> str:
    return f"{QUAD_BEAM_ID_PREFIX}{element_index}-side-{side_index}"
