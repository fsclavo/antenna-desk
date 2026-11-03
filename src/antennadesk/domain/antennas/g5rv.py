# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reference-backed G5RV antenna preset."""

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
from .transmission_line import TransmissionLine
from .wire import Wire

G5RV_DIPOLE_ELEMENT_LENGTH_M = 15.55
G5RV_DIPOLE_TOTAL_LENGTH_M = 2.0 * G5RV_DIPOLE_ELEMENT_LENGTH_M
G5RV_SOURCE_WIRE_LENGTH_M = 0.1
G5RV_SOURCE_ID = "source"
G5RV_DIPOLE_ID = "dipole"
G5RV_LINE_ID = "g5rv-matching-line"


@dataclass(frozen=True, slots=True)
class G5RVLineOption:
    label: str
    characteristic_impedance_ohm: float
    length_m: float


G5RV_LINE_OPTIONS: tuple[G5RVLineOption, ...] = (
    G5RVLineOption("300 Ω / 8.84 m", 300.0, 8.84),
    G5RVLineOption("450 Ω / 10.36 m", 450.0, 10.36),
)


def g5rv_parameters(
    *,
    frequency_hz: float,
    height_m: float = 10.0,
    feed_height_m: float = 1.0,
    azimuth_deg: float = 0.0,
    line_impedance_ohm: float = 450.0,
    line_length_m: float = 10.36,
    line_velocity_factor: float = 1.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> CustomAntennaParameters:
    """Build the published G5RV geometry with a lossless matching line.

    The dipole and matching-line dimensions are the published 102 ft dipole
    with the 300 Ω / 29 ft or 450 Ω / 34 ft matching section. The velocity
    factor is installation-specific; the default treats the published length
    as the electrical length.
    """

    ensure_positive(frequency_hz, name="frequency_hz")
    ensure_non_negative(height_m, name="height_m")
    ensure_non_negative(feed_height_m, name="feed_height_m")
    ensure_positive(line_impedance_ohm, name="line_impedance_ohm")
    ensure_positive(line_length_m, name="line_length_m")
    ensure_positive(line_velocity_factor, name="line_velocity_factor")
    if line_velocity_factor > 1.0:
        raise ValueError("line_velocity_factor must not exceed 1")
    ensure_positive(wire_radius_m, name="wire_radius_m")

    angle = units.degrees_to_radians(units.normalize_azimuth_degrees(azimuth_deg))
    half_length = G5RV_DIPOLE_TOTAL_LENGTH_M / 2.0
    dipole = Wire(
        id=G5RV_DIPOLE_ID,
        start=Point3D(
            x_m=-half_length * math.cos(angle),
            y_m=-half_length * math.sin(angle),
            z_m=height_m,
        ),
        end=Point3D(
            x_m=half_length * math.cos(angle),
            y_m=half_length * math.sin(angle),
            z_m=height_m,
        ),
        radius_m=wire_radius_m,
        material=material,
    )
    source = Wire(
        id=G5RV_SOURCE_ID,
        start=Point3D(x_m=0.0, y_m=0.0, z_m=feed_height_m),
        end=Point3D(
            x_m=0.0,
            y_m=0.0,
            z_m=feed_height_m + G5RV_SOURCE_WIRE_LENGTH_M,
        ),
        radius_m=wire_radius_m,
        material=material,
    )
    line = TransmissionLine(
        id=G5RV_LINE_ID,
        start_wire_id=G5RV_SOURCE_ID,
        start_offset_m=G5RV_SOURCE_WIRE_LENGTH_M / 2.0,
        end_wire_id=G5RV_DIPOLE_ID,
        end_offset_m=half_length,
        characteristic_impedance_ohm=line_impedance_ohm,
        length_m=line_length_m,
        velocity_factor=line_velocity_factor,
    )
    return CustomAntennaParameters(
        frequency_hz=frequency_hz,
        wires=(source, dipole),
        feed=FeedPoint(G5RV_SOURCE_ID, G5RV_SOURCE_WIRE_LENGTH_M / 2.0),
        ground=ground,
        transmission_lines=(line,),
        generator_id="g5rv",
        generator_name="G5RV",
    )
