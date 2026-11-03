# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Two-band center-fed dipole with parallel LC traps."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .dipole import RADIATOR_WIRE_ID, DipoleOrientation
from .feed import FeedPoint
from .geometry import Point3D
from .load import ParallelLoad
from .materials import COPPER, ConductorMaterial
from .wire import Wire

TRAP_LEFT_ID = "trap-left"
TRAP_RIGHT_ID = "trap-right"
ANTENNA_TYPE_TRAP_DIPOLE = "trap_dipole"


@dataclass(frozen=True, slots=True)
class TrapDipoleParameters:
    """A center-fed dipole with one parallel LC trap on each side.

    ``inner_length_m`` is the total span between the traps; it is the driven
    section that radiates on the high band. ``outer_length_m`` is the length of
    each outer section beyond a trap. The total wire length is
    ``inner_length_m + 2 * outer_length_m``.

    The traps store a target frequency and inductance. The capacitance is
    derived from the parallel-resonance condition
    ``f = 1 / (2 * pi * sqrt(L * C))``.
    """

    frequency_hz: float
    high_band_frequency_hz: float
    inner_length_m: float
    outer_length_m: float
    trap_frequency_hz: float
    trap_inductance_h: float
    height_m: float = 10.0
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.high_band_frequency_hz, name="high_band_frequency_hz")
        if self.high_band_frequency_hz <= self.frequency_hz:
            raise ValueError("high_band_frequency_hz must exceed frequency_hz")
        ensure_positive(self.inner_length_m, name="inner_length_m")
        ensure_positive(self.outer_length_m, name="outer_length_m")
        ensure_positive(self.trap_frequency_hz, name="trap_frequency_hz")
        ensure_positive(self.trap_inductance_h, name="trap_inductance_h")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        object.__setattr__(self, "orientation", DipoleOrientation(self.orientation))
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def total_length_m(self) -> float:
        return self.inner_length_m + 2.0 * self.outer_length_m

    @property
    def half_length_m(self) -> float:
        return self.total_length_m / 2.0

    @property
    def trap_capacitance_f(self) -> float:
        return 1.0 / ((2.0 * math.pi * self.trap_frequency_hz) ** 2 * self.trap_inductance_h)

    @property
    def trap_positions_m(self) -> tuple[float, float]:
        """Offsets from the wire start for the two traps."""

        return (
            self.outer_length_m,
            self.outer_length_m + self.inner_length_m,
        )

    @property
    def managed_load_ids(self) -> frozenset[str]:
        """Load identifiers that this template manages."""

        return frozenset({TRAP_LEFT_ID, TRAP_RIGHT_ID})

    def to_custom_parameters(self) -> CustomAntennaParameters:
        total_length = self.total_length_m
        if self.orientation is DipoleOrientation.VERTICAL:
            wire = Wire(
                id=RADIATOR_WIRE_ID,
                start=Point3D(x_m=0.0, y_m=0.0, z_m=self.height_m),
                end=Point3D(x_m=0.0, y_m=0.0, z_m=self.height_m + total_length),
                radius_m=self.wire_radius_m,
                material=self.material,
            )
        else:
            angle = units.degrees_to_radians(self.azimuth_deg)
            offset_x = self.half_length_m * math.cos(angle)
            offset_y = self.half_length_m * math.sin(angle)
            wire = Wire(
                id=RADIATOR_WIRE_ID,
                start=Point3D(x_m=-offset_x, y_m=-offset_y, z_m=self.height_m),
                end=Point3D(x_m=offset_x, y_m=offset_y, z_m=self.height_m),
                radius_m=self.wire_radius_m,
                material=self.material,
            )
        left_position, right_position = self.trap_positions_m
        loads = (
            ParallelLoad(
                id=TRAP_LEFT_ID,
                wire_id=RADIATOR_WIRE_ID,
                offset_m=left_position,
                inductance_h=self.trap_inductance_h,
                capacitance_f=self.trap_capacitance_f,
            ),
            ParallelLoad(
                id=TRAP_RIGHT_ID,
                wire_id=RADIATOR_WIRE_ID,
                offset_m=right_position,
                inductance_h=self.trap_inductance_h,
                capacitance_f=self.trap_capacitance_f,
            ),
        )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=(wire,),
            feed=FeedPoint(RADIATOR_WIRE_ID, self.half_length_m),
            ground=self.ground,
            loads=loads,
            generator_id=ANTENNA_TYPE_TRAP_DIPOLE,
            generator_name="Trap dipole",
        )

    def to_antenna(self, *, name: str = "Trap dipole") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def with_total_length(self, total_length_m: float) -> TrapDipoleParameters:
        ensure_positive(total_length_m, name="total_length_m")
        if total_length_m <= self.inner_length_m:
            raise ValueError("total_length_m must exceed inner_length_m")
        return replace(
            self,
            outer_length_m=(total_length_m - self.inner_length_m) / 2.0,
        )
