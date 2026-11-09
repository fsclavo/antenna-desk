# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric Moxon rectangle."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .polarization import Polarization
from .wire import Wire

ANTENNA_TYPE_MOXON = "moxon"
REFLECTOR_ID = "reflector"
DRIVEN_ID = "driven"


@dataclass(frozen=True, slots=True)
class MoxonParameters:
    """A Moxon rectangle with bent reflector and driven-element tips."""

    frequency_hz: float
    width_m: float
    depth_m: float
    reflector_tip_m: float
    driven_tip_m: float
    height_m: float = 10.0
    azimuth_deg: float = 0.0
    polarization: Polarization = Polarization.HORIZONTAL
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.width_m, name="width_m")
        ensure_positive(self.depth_m, name="depth_m")
        ensure_positive(self.reflector_tip_m, name="reflector_tip_m")
        ensure_positive(self.driven_tip_m, name="driven_tip_m")
        ensure_positive(self.height_m, name="height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if self.reflector_tip_m + self.driven_tip_m >= self.depth_m:
            raise ValueError("Moxon tip lengths must leave a gap between elements")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )
        object.__setattr__(self, "polarization", Polarization(self.polarization))
        if self.polarization is Polarization.VERTICAL:
            lowest_edge = self.height_m - self.width_m / 2.0
            if lowest_edge <= 0.0:
                raise ValueError(
                    "a vertical Moxon would extend below ground; "
                    "increase height_m or reduce width_m"
                )

    @property
    def lowest_edge_m(self) -> float:
        """Return the height of the lowest point of the radiating rectangle."""

        if self.polarization is Polarization.HORIZONTAL:
            return self.height_m
        return self.height_m - self.width_m / 2.0

    @property
    def gap_m(self) -> float:
        return self.depth_m - self.reflector_tip_m - self.driven_tip_m

    def to_antenna(self, *, name: str = "Moxon") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        half_width = self.width_m / 2.0
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        if self.polarization is Polarization.HORIZONTAL:

            def rotate(boom_m: float, element_m: float) -> Point3D:
                return Point3D(
                    x_m=boom_m * cos_angle - element_m * sin_angle,
                    y_m=boom_m * sin_angle + element_m * cos_angle,
                    z_m=self.height_m,
                )

        else:

            def rotate(boom_m: float, element_m: float) -> Point3D:
                return Point3D(
                    x_m=boom_m * cos_angle,
                    y_m=boom_m * sin_angle,
                    z_m=self.height_m + element_m,
                )

        wires = (
            Wire(
                id=REFLECTOR_ID,
                start=rotate(0.0, -half_width),
                end=rotate(0.0, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="reflector-tip-1",
                start=rotate(0.0, -half_width),
                end=rotate(self.reflector_tip_m, -half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="reflector-tip-2",
                start=rotate(0.0, half_width),
                end=rotate(self.reflector_tip_m, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id=DRIVEN_ID,
                start=rotate(self.depth_m, -half_width),
                end=rotate(self.depth_m, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="driven-tip-1",
                start=rotate(self.depth_m, -half_width),
                end=rotate(self.depth_m - self.driven_tip_m, -half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="driven-tip-2",
                start=rotate(self.depth_m, half_width),
                end=rotate(self.depth_m - self.driven_tip_m, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
        )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=wires,
            feed=FeedPoint(DRIVEN_ID, half_width),
            ground=self.ground,
            generator_id="moxon",
            generator_name="Moxon",
        )


FOOT_M = 0.3048
MOXON_REFERENCE_FREQUENCY_HZ = 14_170_000.0


def moxon_20m_wire(
    *,
    frequency_hz: float = MOXON_REFERENCE_FREQUENCY_HZ,
    height_m: float = 10.0,
    azimuth_deg: float = 0.0,
    polarization: Polarization = Polarization.HORIZONTAL,
    wire_radius_m: float = 0.000912,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> MoxonParameters:
    """Return the published 20 m wire Moxon from L. B. Cebik, W4RNL.

    The 14.17 MHz case is the exact published reference: Table 1 (20 m wire),
    using #14 copper wire. The source reports 56-58 ohm feedpoint impedance,
    5.8 dBi free-space gain, and greater than 32 dB front-to-back ratio.
    Other frequencies are scaled linearly from that reference and are a
    heuristic starting point, not an independent reference.
    """

    ensure_positive(frequency_hz, name="frequency_hz")
    scale = MOXON_REFERENCE_FREQUENCY_HZ / frequency_hz
    return MoxonParameters(
        frequency_hz=frequency_hz,
        width_m=25.00 * FOOT_M * scale,
        depth_m=9.57 * FOOT_M * scale,
        reflector_tip_m=4.85 * FOOT_M * scale,
        driven_tip_m=4.00 * FOOT_M * scale,
        height_m=height_m,
        azimuth_deg=azimuth_deg,
        polarization=polarization,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )
