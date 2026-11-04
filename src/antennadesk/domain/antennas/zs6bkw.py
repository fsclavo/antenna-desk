# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reference-backed ZS6BKW multiband doublet preset.

The main variant follows L. B. Cebik, W4RNL, "The G5RV Antenna System
Re-Visited, Part 3: The Almost-No-ATU ZS6BKW": a 28.4 m wire with a 13.6 m
400-ohm matching section. The second variant records the common commercial
450-ohm / 12.2 m implementation for a 27.5 m wire.
"""

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

ZS6BKW_SOURCE_WIRE_LENGTH_M = 0.1
ZS6BKW_SOURCE_ID = "zs6bkw-source"
ZS6BKW_DIPOLE_ID = "zs6bkw-dipole"
ZS6BKW_LINE_ID = "zs6bkw-matching-line"
ZS6BKW_DESIGN_FREQUENCY_HZ = 7_100_000.0


@dataclass(frozen=True, slots=True)
class ZS6BKWVariant:
    """One published ZS6BKW wire and matching-section combination."""

    dipole_total_length_m: float
    characteristic_impedance_ohm: float
    line_length_m: float


ZS6BKW_VARIANTS: tuple[ZS6BKWVariant, ...] = (
    # Cebik/W4RNL reference: 93.18 ft wire, 44.62 ft 400-ohm line.
    ZS6BKWVariant(
        dipole_total_length_m=28.4,
        characteristic_impedance_ohm=400.0,
        line_length_m=13.6,
    ),
    # Common commercial implementation reported by PA0FRI: 2 x 13.75 m wire
    # with 12.2 m of 450-ohm window line.
    ZS6BKWVariant(
        dipole_total_length_m=27.5,
        characteristic_impedance_ohm=450.0,
        line_length_m=12.2,
    ),
)


def zs6bkw_parameters(
    *,
    frequency_hz: float = ZS6BKW_DESIGN_FREQUENCY_HZ,
    height_m: float = 10.0,
    feed_height_m: float = 1.0,
    azimuth_deg: float = 0.0,
    variant: ZS6BKWVariant = ZS6BKW_VARIANTS[0],
    line_velocity_factor: float = 1.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> CustomAntennaParameters:
    """Build a ZS6BKW geometry with a lossless matching section.

    The dimensions are starting points from the cited references. The line
    velocity factor is installation-specific and defaults to treating the
    published length as the electrical length.
    """

    ensure_positive(frequency_hz, name="frequency_hz")
    ensure_non_negative(height_m, name="height_m")
    ensure_non_negative(feed_height_m, name="feed_height_m")
    ensure_positive(line_velocity_factor, name="line_velocity_factor")
    if line_velocity_factor > 1.0:
        raise ValueError("line_velocity_factor must not exceed 1")
    ensure_positive(wire_radius_m, name="wire_radius_m")
    ensure_positive(variant.dipole_total_length_m, name="dipole_total_length_m")
    ensure_positive(
        variant.characteristic_impedance_ohm,
        name="characteristic_impedance_ohm",
    )
    ensure_positive(variant.line_length_m, name="line_length_m")

    angle = units.degrees_to_radians(units.normalize_azimuth_degrees(azimuth_deg))
    half_length = variant.dipole_total_length_m / 2.0
    dipole = Wire(
        id=ZS6BKW_DIPOLE_ID,
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
        id=ZS6BKW_SOURCE_ID,
        start=Point3D(x_m=0.0, y_m=0.0, z_m=feed_height_m),
        end=Point3D(
            x_m=0.0,
            y_m=0.0,
            z_m=feed_height_m + ZS6BKW_SOURCE_WIRE_LENGTH_M,
        ),
        radius_m=wire_radius_m,
        material=material,
    )
    line = TransmissionLine(
        id=ZS6BKW_LINE_ID,
        start_wire_id=ZS6BKW_SOURCE_ID,
        start_offset_m=ZS6BKW_SOURCE_WIRE_LENGTH_M / 2.0,
        end_wire_id=ZS6BKW_DIPOLE_ID,
        end_offset_m=half_length,
        characteristic_impedance_ohm=variant.characteristic_impedance_ohm,
        length_m=variant.line_length_m,
        velocity_factor=line_velocity_factor,
    )
    return CustomAntennaParameters(
        frequency_hz=frequency_hz,
        wires=(source, dipole),
        feed=FeedPoint(ZS6BKW_SOURCE_ID, ZS6BKW_SOURCE_WIRE_LENGTH_M / 2.0),
        ground=ground,
        transmission_lines=(line,),
        generator_id="zs6bkw",
        generator_name="ZS6BKW",
    )


def zs6bkw_with_dimensions(
    parameters: CustomAntennaParameters,
    *,
    dipole_total_length_m: float,
    line_length_m: float,
) -> CustomAntennaParameters:
    """Rebuild a ZS6BKW preset with new wire and matching-line lengths.

    The characteristic impedance, velocity factor, installation, and feed
    geometry are preserved. This is the domain boundary used by the
    template-specific optimizer.
    """

    if parameters.generator_id != "zs6bkw":
        raise ValueError("parameters are not a ZS6BKW preset")
    if len(parameters.transmission_lines) != 1:
        raise ValueError("a ZS6BKW preset requires exactly one matching line")
    dipole = next(
        (wire for wire in parameters.wires if wire.id == ZS6BKW_DIPOLE_ID),
        None,
    )
    source = next(
        (wire for wire in parameters.wires if wire.id == ZS6BKW_SOURCE_ID),
        None,
    )
    if dipole is None or source is None:
        raise ValueError("a ZS6BKW preset requires dipole and source wires")
    line = parameters.transmission_lines[0]
    angle = math.atan2(
        dipole.end.y_m - dipole.start.y_m,
        dipole.end.x_m - dipole.start.x_m,
    )
    return zs6bkw_parameters(
        frequency_hz=parameters.frequency_hz,
        height_m=dipole.start.z_m,
        feed_height_m=source.start.z_m,
        azimuth_deg=math.degrees(angle),
        variant=ZS6BKWVariant(
            dipole_total_length_m=dipole_total_length_m,
            characteristic_impedance_ohm=line.characteristic_impedance_ohm,
            line_length_m=line_length_m,
        ),
        line_velocity_factor=line.velocity_factor,
        wire_radius_m=dipole.radius_m,
        material=dipole.material,
        ground=parameters.ground,
    )
