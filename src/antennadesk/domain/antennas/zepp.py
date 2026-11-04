# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Classic end-fed Zepp preset with a quarter-wave matching section.

This is a simplified model: the half-wave radiator is end-fed through a
lossless transmission line that represents the parallel-wire matching section.
The second conductor, the 1:1 choke, and common-mode current are not part of the
geometry. It is a starting point for the classic Zepp, not a validated
construction design.
"""

from __future__ import annotations

import math

from ..common import units
from ..common.units import ensure_positive
from ..design.formulas import half_wave_length_m, quarter_wave_length_m
from ..environment.ground import FREE_SPACE, GroundModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .transmission_line import TransmissionLine
from .wire import Wire

ZEPP_SOURCE_WIRE_LENGTH_M = 0.1
ZEPP_SOURCE_ID = "zepp-source"
ZEPP_RADIATOR_ID = "zepp-radiator"
ZEPP_LINE_ID = "zepp-matching-line"
ZEPP_DESIGN_FREQUENCY_HZ = 7_100_000.0
ZEPP_LINE_IMPEDANCE_OHM = 400.0


def zepp_starting_dimensions(frequency_hz: float) -> tuple[float, float]:
    """Return the classic half-wave radiator and quarter-wave line lengths."""

    ensure_positive(frequency_hz, name="frequency_hz")
    return half_wave_length_m(frequency_hz), quarter_wave_length_m(frequency_hz)


def zepp_parameters(
    *,
    frequency_hz: float = ZEPP_DESIGN_FREQUENCY_HZ,
    radiator_length_m: float | None = None,
    matching_line_length_m: float | None = None,
    matching_line_impedance_ohm: float = ZEPP_LINE_IMPEDANCE_OHM,
    height_m: float = 10.0,
    feed_height_m: float = 1.0,
    azimuth_deg: float = 0.0,
    line_velocity_factor: float = 1.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> CustomAntennaParameters:
    """Build the simplified end-fed Zepp geometry.

    The matching section is modeled as a lossless two-port. The default lengths
    use the same practical half-wave/quarter-wave factors as the other
    estimators. The user should verify the line length and choke in the real
    installation.
    """

    default_radiator, default_line = zepp_starting_dimensions(frequency_hz)
    radiator_length_m = default_radiator if radiator_length_m is None else radiator_length_m
    matching_line_length_m = (
        default_line if matching_line_length_m is None else matching_line_length_m
    )
    angle = units.degrees_to_radians(units.normalize_azimuth_degrees(azimuth_deg))
    feed = Point3D(x_m=0.0, y_m=0.0, z_m=height_m)
    radiator = Wire(
        id=ZEPP_RADIATOR_ID,
        start=feed,
        end=Point3D(
            x_m=radiator_length_m * math.cos(angle),
            y_m=radiator_length_m * math.sin(angle),
            z_m=height_m,
        ),
        radius_m=wire_radius_m,
        material=material,
    )
    source = Wire(
        id=ZEPP_SOURCE_ID,
        start=Point3D(x_m=0.0, y_m=0.0, z_m=feed_height_m),
        end=Point3D(
            x_m=0.0,
            y_m=0.0,
            z_m=feed_height_m + ZEPP_SOURCE_WIRE_LENGTH_M,
        ),
        radius_m=wire_radius_m,
        material=material,
    )
    line = TransmissionLine(
        id=ZEPP_LINE_ID,
        start_wire_id=ZEPP_SOURCE_ID,
        start_offset_m=ZEPP_SOURCE_WIRE_LENGTH_M / 2.0,
        end_wire_id=ZEPP_RADIATOR_ID,
        end_offset_m=0.0,
        characteristic_impedance_ohm=matching_line_impedance_ohm,
        length_m=matching_line_length_m,
        velocity_factor=line_velocity_factor,
    )
    return CustomAntennaParameters(
        frequency_hz=frequency_hz,
        wires=(source, radiator),
        feed=FeedPoint(ZEPP_RADIATOR_ID, 0.0),
        ground=ground,
        transmission_lines=(line,),
        generator_id="zepp",
        generator_name="Zepp",
    )
