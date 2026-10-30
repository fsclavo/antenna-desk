# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric Yagi-Uda geometry generated as an editable custom-wire design."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

YAGI_ELEMENT_ID_PREFIX = "element"


@dataclass(frozen=True, slots=True)
class YagiElement:
    """One straight element placed along the boom.

    ``position_m`` is measured from the reflector toward the directors.
    ``length_m`` is the full tip-to-tip element length.
    """

    position_m: float
    length_m: float
    radius_m: float

    def __post_init__(self) -> None:
        ensure_non_negative(self.position_m, name="position_m")
        ensure_positive(self.length_m, name="length_m")
        ensure_positive(self.radius_m, name="radius_m")


@dataclass(frozen=True, slots=True)
class YagiParameters:
    """A Yagi-Uda geometry with arbitrary element lengths and spacings."""

    frequency_hz: float
    elements: tuple[YagiElement, ...]
    height_m: float
    driven_index: int = 1
    azimuth_deg: float = 0.0
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_non_negative(self.height_m, name="height_m")
        elements = tuple(sorted(self.elements, key=lambda element: element.position_m))
        object.__setattr__(self, "elements", elements)
        if len(elements) < 2:
            raise ValueError("a Yagi requires at least a reflector and a driven element")
        for index, element in enumerate(elements):
            if index > 0 and math.isclose(
                element.position_m,
                elements[index - 1].position_m,
                rel_tol=0.0,
                abs_tol=1e-9,
            ):
                raise ValueError("Yagi element positions must be distinct")
        if not 0 <= self.driven_index < len(elements):
            raise ValueError("driven_index is outside the element list")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def wavelength_m(self) -> float:
        return units.wavelength_m(self.frequency_hz)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        wires: list[Wire] = []
        for index, element in enumerate(self.elements):
            half_length = element.length_m / 2.0
            local_start = Point3D(
                x_m=element.position_m,
                y_m=-half_length,
                z_m=self.height_m,
            )
            local_end = Point3D(
                x_m=element.position_m,
                y_m=half_length,
                z_m=self.height_m,
            )
            start = Point3D(
                x_m=local_start.x_m * cos_angle - local_start.y_m * sin_angle,
                y_m=local_start.x_m * sin_angle + local_start.y_m * cos_angle,
                z_m=local_start.z_m,
            )
            end = Point3D(
                x_m=local_end.x_m * cos_angle - local_end.y_m * sin_angle,
                y_m=local_end.x_m * sin_angle + local_end.y_m * cos_angle,
                z_m=local_end.z_m,
            )
            wires.append(
                Wire(
                    id=f"{YAGI_ELEMENT_ID_PREFIX}-{index + 1}",
                    start=start,
                    end=end,
                    radius_m=element.radius_m,
                    material=self.material,
                )
            )

        driven = wires[self.driven_index]
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(wire_id=driven.id, offset_m=driven.length_m / 2.0),
            ground=self.ground,
        )


def nbs_five_element(
    *,
    frequency_hz: float,
    height_m: float,
    azimuth_deg: float = 0.0,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
    radius_m: float | None = None,
) -> YagiParameters:
    """Return the NBS TN-688 5-element, 0.8 wavelength starting design.

    The dimensions are scaled from the published 50.1 MHz example.  The
    reference measured gain is 9.2 dBd over a half-wave dipole.  A single
    straight driven element is used here instead of the published folded
    dipole, so the impedance is not the reference impedance; gain and pattern
    remain the relevant comparison.
    """

    wavelength = units.wavelength_m(frequency_hz)
    radius = radius_m if radius_m is not None else 0.0021 * wavelength
    return YagiParameters(
        frequency_hz=frequency_hz,
        elements=(
            YagiElement(position_m=0.0, length_m=0.490 * wavelength, radius_m=radius),
            YagiElement(position_m=0.2 * wavelength, length_m=0.500 * wavelength, radius_m=radius),
            YagiElement(position_m=0.4 * wavelength, length_m=0.447 * wavelength, radius_m=radius),
            YagiElement(position_m=0.6 * wavelength, length_m=0.443 * wavelength, radius_m=radius),
            YagiElement(position_m=0.8 * wavelength, length_m=0.447 * wavelength, radius_m=radius),
        ),
        height_m=height_m,
        driven_index=1,
        azimuth_deg=azimuth_deg,
        material=material,
        ground=ground,
    )
