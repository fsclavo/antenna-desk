# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""VK2ZOI-style half-wave Flower Pot antenna."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_non_negative, ensure_positive
from ..environment.environment import Environment
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_FLOWER_POT = "flower_pot"
TOP_RADIATOR_ID = "top-radiator"
BOTTOM_RADIATOR_ID = "bottom-radiator"

# Published construction rows from the VK2ZOI half-wave Flower Pot / VK4PK
# 6 m construction survey. These are physical coax cut lengths, not electrical
# lengths. The 0.88 factor is a construction factor relative to a free-space
# half-wave; the 1.087 factor is the separate NEC model calibration selected by
# the FP1 length-representation spike.
FLOWER_POT_2M_FREQUENCY_HZ = 146_000_000.0
FLOWER_POT_2M_TOP_LENGTH_M = 0.457
FLOWER_POT_2M_BOTTOM_LENGTH_M = 0.447
FLOWER_POT_2M_CHOKE_HEIGHT_M = 0.045
FLOWER_POT_6M_FREQUENCY_HZ = 52_700_000.0
FLOWER_POT_6M_TOP_LENGTH_M = 1.273
FLOWER_POT_6M_BOTTOM_LENGTH_M = 1.245
FLOWER_POT_6M_CHOKE_HEIGHT_M = 0.063

FLOWER_POT_CONSTRUCTION_SHORTENING_FACTOR = 0.88
FLOWER_POT_ELECTRICAL_LENGTH_SCALE = 1.087
FLOWER_POT_DEFAULT_TOP_RADIUS_M = 0.0005
FLOWER_POT_DEFAULT_BOTTOM_RADIUS_M = 0.0015
# ``base_height_m`` is the physical feed connector at the bottom of the choke.
# The default choke length is zero so a project created before schema 73 keeps
# its original lower-cut geometry; the published 2 m/6 m rows set the measured
# construction lengths explicitly.
FLOWER_POT_DEFAULT_BASE_HEIGHT_M = 1.0
FLOWER_POT_DEFAULT_CHOKE_HEIGHT_M = 0.0


@dataclass(frozen=True, slots=True)
class FlowerPotParameters:
    """Half-wave Flower Pot with physical cut lengths and a NEC equivalent.

    ``top_length_m`` and ``bottom_length_m`` are the physical coax cut lengths
    that the builder must use. ``base_height_m`` is the physical feed connector
    at the bottom of the choke; ``choke_height_m`` is the construction-only
    distance from that feed to the lower cut (the top of the choke). The lower
    radiating arm starts at ``lower_cut_height_m``. ``electrical_length_scale``
    is applied only by :meth:`to_antenna` to obtain the NEC equivalent; it is
    not a velocity factor and must not be used as a construction dimension.
    """

    frequency_hz: float
    top_length_m: float
    bottom_length_m: float
    top_radius_m: float = FLOWER_POT_DEFAULT_TOP_RADIUS_M
    bottom_radius_m: float = FLOWER_POT_DEFAULT_BOTTOM_RADIUS_M
    base_height_m: float = FLOWER_POT_DEFAULT_BASE_HEIGHT_M
    choke_height_m: float = FLOWER_POT_DEFAULT_CHOKE_HEIGHT_M
    construction_shortening_factor: float = FLOWER_POT_CONSTRUCTION_SHORTENING_FACTOR
    electrical_length_scale: float = FLOWER_POT_ELECTRICAL_LENGTH_SCALE
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.top_length_m, name="top_length_m")
        ensure_positive(self.bottom_length_m, name="bottom_length_m")
        ensure_positive(self.top_radius_m, name="top_radius_m")
        ensure_positive(self.bottom_radius_m, name="bottom_radius_m")
        ensure_positive(self.base_height_m, name="base_height_m")
        ensure_non_negative(self.choke_height_m, name="choke_height_m")
        if not 0.5 <= self.construction_shortening_factor <= 1.0:
            raise ValueError("construction_shortening_factor must be between 0.5 and 1.0")
        if not 0.5 <= self.electrical_length_scale <= 1.5:
            raise ValueError("electrical_length_scale must be between 0.5 and 1.5")
        if self.electrical_lower_tip_m <= 0.0:
            raise ValueError(
                f"base_height_m={self.base_height_m:.4f} m places the scaled electrical "
                f"lower tip at {self.electrical_lower_tip_m:.4f} m; increase the feed "
                "or choke height"
            )

    @property
    def physical_total_length_m(self) -> float:
        return self.top_length_m + self.bottom_length_m

    @property
    def electrical_top_length_m(self) -> float:
        return self.top_length_m * self.electrical_length_scale

    @property
    def electrical_bottom_length_m(self) -> float:
        return self.bottom_length_m * self.electrical_length_scale

    @property
    def electrical_total_length_m(self) -> float:
        return self.electrical_top_length_m + self.electrical_bottom_length_m

    @property
    def lower_cut_height_m(self) -> float:
        """Height of the bottom of the lower radiating arm (top of the choke)."""

        return self.base_height_m + self.choke_height_m

    @property
    def physical_feed_height_m(self) -> float:
        """Height of the physical feed connector at the bottom of the choke."""

        return self.base_height_m

    @property
    def physical_junction_height_m(self) -> float:
        """Height of the lower/upper arm junction and the NEC equivalent source."""

        return self.lower_cut_height_m + self.bottom_length_m

    @property
    def electrical_feed_height_m(self) -> float:
        """Height of the feed in the canonical NEC equivalent."""

        return self.physical_junction_height_m

    @property
    def electrical_lower_tip_m(self) -> float:
        return self.electrical_feed_height_m - self.electrical_bottom_length_m

    @property
    def electrical_top_tip_m(self) -> float:
        return self.electrical_feed_height_m + self.electrical_top_length_m

    @property
    def physical_top_tip_m(self) -> float:
        return self.physical_junction_height_m + self.top_length_m

    @property
    def lower_tip_extension_m(self) -> float:
        """How far the electrical lower tip extends below the physical cut."""

        return self.electrical_bottom_length_m - self.bottom_length_m

    @property
    def top_extension_m(self) -> float:
        """How far the electrical top tip extends above the physical cut."""

        return self.electrical_top_tip_m - self.physical_top_tip_m

    @property
    def template_name(self) -> str:
        return "Flower Pot"

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        feed_z = self.electrical_feed_height_m
        top = Wire(
            id=TOP_RADIATOR_ID,
            start=Point3D(x_m=0.0, y_m=0.0, z_m=feed_z),
            end=Point3D(
                x_m=0.0,
                y_m=0.0,
                z_m=feed_z + self.electrical_top_length_m,
            ),
            radius_m=self.top_radius_m,
            material=self.material,
        )
        bottom = Wire(
            id=BOTTOM_RADIATOR_ID,
            start=Point3D(
                x_m=0.0,
                y_m=0.0,
                z_m=feed_z - self.electrical_bottom_length_m,
            ),
            end=Point3D(x_m=0.0, y_m=0.0, z_m=feed_z),
            radius_m=self.bottom_radius_m,
            material=self.material,
        )
        return AntennaModel(
            name=name or self.template_name,
            design_frequency_hz=self.frequency_hz,
            wires=(top, bottom),
            feed=FeedPoint(TOP_RADIATOR_ID, 0.0),
            environment=Environment(ground=self.ground),
        )


def flower_pot_2m() -> FlowerPotParameters:
    """Return the published 2 m starting row plus explicit installation defaults."""

    return FlowerPotParameters(
        frequency_hz=FLOWER_POT_2M_FREQUENCY_HZ,
        top_length_m=FLOWER_POT_2M_TOP_LENGTH_M,
        bottom_length_m=FLOWER_POT_2M_BOTTOM_LENGTH_M,
        choke_height_m=FLOWER_POT_2M_CHOKE_HEIGHT_M,
    )


def flower_pot_6m() -> FlowerPotParameters:
    """Return the published 6 m starting row plus explicit installation defaults."""

    return FlowerPotParameters(
        frequency_hz=FLOWER_POT_6M_FREQUENCY_HZ,
        top_length_m=FLOWER_POT_6M_TOP_LENGTH_M,
        bottom_length_m=FLOWER_POT_6M_BOTTOM_LENGTH_M,
        choke_height_m=FLOWER_POT_6M_CHOKE_HEIGHT_M,
    )
