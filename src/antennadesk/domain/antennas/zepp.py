# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Classic end-fed Zepp with a real two-wire quarter-wave matching stub.

The model follows the true Zepp topology: a half-wave radiator is connected to
the top of one conductor of a parallel-wire quarter-wave stub.  The second stub
conductor is open at the antenna end, and both conductors are joined by a short
base connector at the feed end.  The feed point is the middle of that connector,
so the source drives the balanced pair rather than a single wire against an
implicit ground.

The 1:1 common-mode choke at the transmitter end of the stub is a construction
requirement, not a solver element.  NEC-2 has no ferrite or common-mode choke
model, so the choke and the coaxial feed line are deliberately left outside the
electrical model.  The stub itself is real geometry and radiates; its current is
part of the result.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_ZEPP = "zepp"
ZEPP_RADIATOR_ID = "zepp-radiator"
ZEPP_MATCHING_FEED_ID = "zepp-matching-feed"
ZEPP_MATCHING_OPEN_ID = "zepp-matching-open"
ZEPP_BASE_ID = "zepp-base"
ZEPP_DESIGN_FREQUENCY_HZ = 7_100_000.0
ZEPP_DEFAULT_SPACING_M = 0.05
ZEPP_DEFAULT_BASE_HEIGHT_M = 1.0
ZEPP_CHOKE_RATIO = 1.0


@dataclass(frozen=True, slots=True)
class ZeppParameters:
    """Typed classic Zepp geometry with a real matching stub."""

    frequency_hz: float
    radiator_length_m: float
    matching_section_length_m: float
    spacing_m: float = ZEPP_DEFAULT_SPACING_M
    base_height_m: float = ZEPP_DEFAULT_BASE_HEIGHT_M
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.radiator_length_m, name="radiator_length_m")
        ensure_positive(self.matching_section_length_m, name="matching_section_length_m")
        ensure_positive(self.spacing_m, name="spacing_m")
        ensure_non_negative(self.base_height_m, name="base_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if self.spacing_m <= 2.0 * self.wire_radius_m:
            raise ValueError("spacing_m must be greater than the conductor diameter")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return "Zepp"

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name or self.template_name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        return zepp_parameters(
            frequency_hz=self.frequency_hz,
            radiator_length_m=self.radiator_length_m,
            matching_section_length_m=self.matching_section_length_m,
            spacing_m=self.spacing_m,
            base_height_m=self.base_height_m,
            azimuth_deg=self.azimuth_deg,
            wire_radius_m=self.wire_radius_m,
            material=self.material,
            ground=self.ground,
        )


def zepp_starting_parameters(
    *,
    frequency_hz: float = ZEPP_DESIGN_FREQUENCY_HZ,
    base_height_m: float = ZEPP_DEFAULT_BASE_HEIGHT_M,
    spacing_m: float = ZEPP_DEFAULT_SPACING_M,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> ZeppParameters:
    radiator_m, matching_m = zepp_starting_dimensions(frequency_hz)
    return ZeppParameters(
        frequency_hz=frequency_hz,
        radiator_length_m=radiator_m,
        matching_section_length_m=matching_m,
        spacing_m=spacing_m,
        base_height_m=base_height_m,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


@dataclass(frozen=True, slots=True)
class ZeppChoke:
    """The 1:1 common-mode choke required at the transmitter end.

    ``modeled`` is false because the canonical model and NEC-2 have no
    common-mode choke element.  The descriptor keeps the requirement explicit
    and testable instead of implying that an ideal transformer models it.
    """

    ratio: float = ZEPP_CHOKE_RATIO
    modeled: bool = False

    def __post_init__(self) -> None:
        ensure_positive(self.ratio, name="ratio")


def zepp_choke() -> ZeppChoke:
    """Return the construction requirement for the Zepp feed-line choke."""

    return ZeppChoke()


def zepp_starting_dimensions(frequency_hz: float) -> tuple[float, float]:
    """Return the classic half-wave radiator and quarter-wave stub lengths."""

    from ..design.formulas import half_wave_length_m, quarter_wave_length_m

    ensure_positive(frequency_hz, name="frequency_hz")
    return half_wave_length_m(frequency_hz), quarter_wave_length_m(frequency_hz)


def parallel_wire_impedance_ohm(spacing_m: float, wire_radius_m: float) -> float:
    """Estimate the characteristic impedance of an air-spaced parallel pair.

    The standard thin-wire approximation is

    ``Z0 = 276 log10(D / r)``

    where ``D`` is the center-to-center spacing and ``r`` is the conductor
    radius.  It ignores insulation, nearby conductors, and the finite length of
    the stub, so it is a starting value for the geometry, not a measurement.
    """

    ensure_positive(spacing_m, name="spacing_m")
    ensure_positive(wire_radius_m, name="wire_radius_m")
    if spacing_m <= 2.0 * wire_radius_m:
        raise ValueError("spacing_m must be greater than the conductor diameter")
    return 276.0 * math.log10(spacing_m / wire_radius_m)


def zepp_parameters(
    *,
    frequency_hz: float = ZEPP_DESIGN_FREQUENCY_HZ,
    radiator_length_m: float | None = None,
    matching_section_length_m: float | None = None,
    spacing_m: float = ZEPP_DEFAULT_SPACING_M,
    base_height_m: float = ZEPP_DEFAULT_BASE_HEIGHT_M,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> CustomAntennaParameters:
    """Build the classic end-fed Zepp geometry with a real matching stub.

    The radiator runs horizontally from the top of the fed stub conductor.  The
    stub hangs vertically and its two conductors are separated perpendicular to
    the radiator azimuth.  ``base_height_m`` is the feed end of the stub; the
    radiator height is ``base_height_m + matching_section_length_m``.

    The default lengths use the project's practical half-wave/quarter-wave
    factors.  The actual stub length also depends on the open-end and shorting
    bar details, and the match depends on height and ground; tune both in the
    real installation.
    """

    ensure_positive(frequency_hz, name="frequency_hz")
    ensure_non_negative(base_height_m, name="base_height_m")
    ensure_positive(spacing_m, name="spacing_m")
    ensure_positive(wire_radius_m, name="wire_radius_m")
    if spacing_m <= 2.0 * wire_radius_m:
        raise ValueError("spacing_m must be greater than the conductor diameter")

    default_radiator, default_matching = zepp_starting_dimensions(frequency_hz)
    radiator_length_m = default_radiator if radiator_length_m is None else radiator_length_m
    matching_section_length_m = (
        default_matching if matching_section_length_m is None else matching_section_length_m
    )
    ensure_positive(radiator_length_m, name="radiator_length_m")
    ensure_positive(matching_section_length_m, name="matching_section_length_m")

    angle = units.degrees_to_radians(units.normalize_azimuth_degrees(azimuth_deg))
    top_z_m = base_height_m + matching_section_length_m
    stub_dx_m = -math.sin(angle) * spacing_m
    stub_dy_m = math.cos(angle) * spacing_m

    radiator = Wire(
        id=ZEPP_RADIATOR_ID,
        start=Point3D(x_m=0.0, y_m=0.0, z_m=top_z_m),
        end=Point3D(
            x_m=radiator_length_m * math.cos(angle),
            y_m=radiator_length_m * math.sin(angle),
            z_m=top_z_m,
        ),
        radius_m=wire_radius_m,
        material=material,
    )
    matching_feed = Wire(
        id=ZEPP_MATCHING_FEED_ID,
        start=Point3D(x_m=0.0, y_m=0.0, z_m=base_height_m),
        end=Point3D(x_m=0.0, y_m=0.0, z_m=top_z_m),
        radius_m=wire_radius_m,
        material=material,
    )
    matching_open = Wire(
        id=ZEPP_MATCHING_OPEN_ID,
        start=Point3D(x_m=stub_dx_m, y_m=stub_dy_m, z_m=base_height_m),
        end=Point3D(x_m=stub_dx_m, y_m=stub_dy_m, z_m=top_z_m),
        radius_m=wire_radius_m,
        material=material,
    )
    base = Wire(
        id=ZEPP_BASE_ID,
        start=Point3D(x_m=0.0, y_m=0.0, z_m=base_height_m),
        end=Point3D(x_m=stub_dx_m, y_m=stub_dy_m, z_m=base_height_m),
        radius_m=wire_radius_m,
        material=material,
    )
    return CustomAntennaParameters(
        frequency_hz=frequency_hz,
        wires=(radiator, matching_feed, matching_open, base),
        feed=FeedPoint(ZEPP_BASE_ID, spacing_m / 2.0),
        ground=ground,
        generator_id="zepp",
        generator_name="Zepp",
    )
