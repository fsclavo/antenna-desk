# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Terminated folded dipole (T2FD) with a broadband resistive termination."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .dipole import DipoleOrientation
from .feed import FeedPoint
from .geometry import Point3D
from .load import SeriesLoad
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_T2FD = "t2fd"
T2FD_DRIVEN_WIRE_ID = "t2fd-driven"
T2FD_TERMINATED_WIRE_ID = "t2fd-terminated"
T2FD_START_CONNECTOR_ID = "t2fd-start-connector"
T2FD_END_CONNECTOR_ID = "t2fd-end-connector"
T2FD_TERMINATION_LOAD_ID = "t2fd-termination"

# Starting dimensions from Cebik's "wide-long" T2FD: the span is about
# 300/F(MHz) feet and the conductor spacing about 10/F(MHz) feet. These are
# construction starting points, not a resonance calculation.
T2FD_SPAN_FEET_PER_MHZ = 300.0
T2FD_SPACING_FEET_PER_MHZ = 10.0
FEET_TO_METERS = 0.3048

DEFAULT_T2FD_TERMINATION_OHM = 800.0
DEFAULT_T2FD_TRANSFORMER_RATIO = 16.0
DEFAULT_T2FD_HEIGHT_M = 10.0


def t2fd_starting_dimensions(frequency_hz: float) -> tuple[float, float]:
    """Return the published wide-long span and spacing in meters."""

    ensure_positive(frequency_hz, name="frequency_hz")
    frequency_mhz = frequency_hz / 1_000_000.0
    span_m = T2FD_SPAN_FEET_PER_MHZ * FEET_TO_METERS / frequency_mhz
    spacing_m = T2FD_SPACING_FEET_PER_MHZ * FEET_TO_METERS / frequency_mhz
    return span_m, spacing_m


@dataclass(frozen=True, slots=True)
class T2FDParameters:
    """A terminated folded dipole for broadband HF operation.

    ``frequency_hz`` is the lowest design frequency and
    ``highest_frequency_hz`` the upper end of the intended band. The antenna
    is two parallel conductors joined at both ends. One conductor is fed at
    its midpoint; the other carries a non-inductive terminating resistor at
    its midpoint. The transformer ratio scales the antenna impedance down to
    the transmitter reference impedance in post-processing; it is not part of
    the NEC geometry.

    This model uses an ideal resistor and an ideal transformer. Balun losses,
    resistor temperature rise, and the installation tilt are not modeled.
    """

    frequency_hz: float
    highest_frequency_hz: float
    length_m: float
    spacing_m: float
    height_m: float = DEFAULT_T2FD_HEIGHT_M
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL
    termination_resistance_ohm: float = DEFAULT_T2FD_TERMINATION_OHM
    transformer_ratio: float = DEFAULT_T2FD_TRANSFORMER_RATIO
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.highest_frequency_hz, name="highest_frequency_hz")
        if self.highest_frequency_hz <= self.frequency_hz:
            raise ValueError("highest_frequency_hz must exceed frequency_hz")
        ensure_positive(self.length_m, name="length_m")
        ensure_positive(self.spacing_m, name="spacing_m")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_positive(
            self.termination_resistance_ohm,
            name="termination_resistance_ohm",
        )
        ensure_positive(self.transformer_ratio, name="transformer_ratio")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        object.__setattr__(self, "orientation", DipoleOrientation(self.orientation))
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def half_length_m(self) -> float:
        return self.length_m / 2.0

    @property
    def termination_offset_m(self) -> float:
        return self.half_length_m

    @property
    def total_conductor_length_m(self) -> float:
        return 2.0 * self.length_m + 2.0 * self.spacing_m

    @property
    def managed_load_ids(self) -> frozenset[str]:
        """Load identifiers that this template manages."""

        return frozenset({T2FD_TERMINATION_LOAD_ID})

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        direction_x = math.cos(angle)
        direction_y = math.sin(angle)
        perpendicular_x = -direction_y
        perpendicular_y = direction_x
        half_length = self.half_length_m
        half_spacing = self.spacing_m / 2.0

        if self.orientation is DipoleOrientation.VERTICAL:

            def point(along_m: float, across_m: float) -> Point3D:
                return Point3D(
                    x_m=across_m * perpendicular_x,
                    y_m=across_m * perpendicular_y,
                    z_m=self.height_m + along_m + half_length,
                )

        else:

            def point(along_m: float, across_m: float) -> Point3D:
                return Point3D(
                    x_m=along_m * direction_x + across_m * perpendicular_x,
                    y_m=along_m * direction_y + across_m * perpendicular_y,
                    z_m=self.height_m,
                )

        driven_start = point(-half_length, half_spacing)
        driven_end = point(half_length, half_spacing)
        terminated_start = point(-half_length, -half_spacing)
        terminated_end = point(half_length, -half_spacing)

        wires = (
            Wire(
                id=T2FD_DRIVEN_WIRE_ID,
                start=driven_start,
                end=driven_end,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id=T2FD_TERMINATED_WIRE_ID,
                start=terminated_start,
                end=terminated_end,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id=T2FD_START_CONNECTOR_ID,
                start=driven_start,
                end=terminated_start,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id=T2FD_END_CONNECTOR_ID,
                start=driven_end,
                end=terminated_end,
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
        )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=wires,
            feed=FeedPoint(
                wire_id=T2FD_DRIVEN_WIRE_ID,
                offset_m=self.half_length_m,
            ),
            ground=self.ground,
            loads=(
                SeriesLoad(
                    id=T2FD_TERMINATION_LOAD_ID,
                    wire_id=T2FD_TERMINATED_WIRE_ID,
                    offset_m=self.termination_offset_m,
                    resistance_ohm=self.termination_resistance_ohm,
                ),
            ),
            generator_id=ANTENNA_TYPE_T2FD,
            generator_name="T2FD",
        )

    def to_antenna(self, *, name: str = "T2FD") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def with_length(self, length_m: float) -> T2FDParameters:
        ensure_positive(length_m, name="length_m")
        return replace(self, length_m=length_m)
