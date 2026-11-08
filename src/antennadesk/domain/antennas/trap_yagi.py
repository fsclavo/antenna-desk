# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Two-band Yagi with one parallel LC trap pair per element."""

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
from .load import ParallelLoad
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_TRAP_YAGI = "trap_yagi"
TRAP_YAGI_ID_PREFIX = "trap-yagi-element-"
TRAP_YAGI_LOAD_PREFIX = "trap-yagi-load-"
MIN_ELEMENTS = 2
MAX_ELEMENTS = 3
DRIVEN_ELEMENT_INDEX = 1
MIN_REFLECTOR_SCALE = 1.0
MAX_REFLECTOR_SCALE = 1.2
MIN_DIRECTOR_SCALE = 0.8
MAX_DIRECTOR_SCALE = 1.0


def trap_yagi_parameters(
    *,
    frequency_hz: float = 7_100_000.0,
    high_band_frequency_hz: float = 14_100_000.0,
    element_count: int = 3,
    driven_length_m: float | None = None,
    reflector_spacing_m: float | None = None,
    director_spacing_m: float | None = None,
    trap_inset_m: float | None = None,
    trap_frequency_hz: float | None = None,
    trap_inductance_h: float = 5e-6,
    reflector_scale: float = 1.05,
    director_scale: float = 0.95,
    height_m: float = 10.0,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> TrapYagiParameters:
    """Return a half-wave Yagi with high-band trap pairs on every element."""

    from ..design.formulas import half_wave_length_m, quarter_wave_length_m, wavelength_m

    wavelength = wavelength_m(frequency_hz)
    return TrapYagiParameters(
        frequency_hz=frequency_hz,
        high_band_frequency_hz=high_band_frequency_hz,
        element_count=element_count,
        driven_length_m=(
            half_wave_length_m(frequency_hz) if driven_length_m is None else driven_length_m
        ),
        reflector_spacing_m=(
            wavelength * 0.2 if reflector_spacing_m is None else reflector_spacing_m
        ),
        director_spacing_m=(wavelength * 0.2 if director_spacing_m is None else director_spacing_m),
        trap_inset_m=(
            quarter_wave_length_m(high_band_frequency_hz) if trap_inset_m is None else trap_inset_m
        ),
        trap_frequency_hz=(
            high_band_frequency_hz if trap_frequency_hz is None else trap_frequency_hz
        ),
        trap_inductance_h=trap_inductance_h,
        reflector_scale=reflector_scale,
        director_scale=director_scale,
        height_m=height_m,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


@dataclass(frozen=True, slots=True)
class TrapYagiParameters:
    """A reflector, driven element, and optional director with LC traps.

    Every element is a single straight wire with one parallel LC trap on each
    side of its center. The traps are resonant on the high band, so the outer
    tips are effectively isolated there; on the low band they load and shorten
    the elements. The trap model is ideal and has no core or dielectric loss.
    """

    frequency_hz: float
    high_band_frequency_hz: float
    driven_length_m: float
    reflector_spacing_m: float
    trap_inset_m: float
    trap_frequency_hz: float
    trap_inductance_h: float
    element_count: int = MAX_ELEMENTS
    director_spacing_m: float = 0.0
    reflector_scale: float = 1.05
    director_scale: float = 0.95
    height_m: float = 10.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.high_band_frequency_hz, name="high_band_frequency_hz")
        if self.high_band_frequency_hz <= self.frequency_hz:
            raise ValueError("high_band_frequency_hz must exceed frequency_hz")
        ensure_positive(self.driven_length_m, name="driven_length_m")
        ensure_positive(self.reflector_spacing_m, name="reflector_spacing_m")
        if not MIN_ELEMENTS <= self.element_count <= MAX_ELEMENTS:
            raise ValueError(f"element_count must be between {MIN_ELEMENTS} and {MAX_ELEMENTS}")
        if self.element_count == MAX_ELEMENTS:
            ensure_positive(self.director_spacing_m, name="director_spacing_m")
        else:
            ensure_non_negative(self.director_spacing_m, name="director_spacing_m")
        ensure_positive(self.trap_inset_m, name="trap_inset_m")
        ensure_positive(self.trap_frequency_hz, name="trap_frequency_hz")
        ensure_positive(self.trap_inductance_h, name="trap_inductance_h")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if not MIN_REFLECTOR_SCALE <= self.reflector_scale <= MAX_REFLECTOR_SCALE:
            raise ValueError(
                f"reflector_scale must be between {MIN_REFLECTOR_SCALE} and {MAX_REFLECTOR_SCALE}"
            )
        if not MIN_DIRECTOR_SCALE <= self.director_scale <= MAX_DIRECTOR_SCALE:
            raise ValueError(
                f"director_scale must be between {MIN_DIRECTOR_SCALE} and {MAX_DIRECTOR_SCALE}"
            )
        if self.trap_inset_m >= min(length / 2.0 for length in self.element_lengths_m):
            raise ValueError("trap_inset_m must be less than half of every element")
        if self.trap_inset_m <= 2.0 * self.wire_radius_m:
            raise ValueError("trap_inset_m must exceed the conductor diameter")
        if min(self.element_spacings_m) <= 2.0 * self.wire_radius_m:
            raise ValueError("element spacing must exceed the conductor diameter")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return "Trapped Yagi"

    @property
    def reflector_length_m(self) -> float:
        return self.driven_length_m * self.reflector_scale

    @property
    def director_length_m(self) -> float:
        return self.driven_length_m * self.director_scale

    @property
    def element_lengths_m(self) -> tuple[float, ...]:
        if self.element_count == MAX_ELEMENTS:
            return (
                self.reflector_length_m,
                self.driven_length_m,
                self.director_length_m,
            )
        return (self.reflector_length_m, self.driven_length_m)

    @property
    def element_spacings_m(self) -> tuple[float, ...]:
        if self.element_count == MAX_ELEMENTS:
            return (self.reflector_spacing_m, self.director_spacing_m)
        return (self.reflector_spacing_m,)

    @property
    def element_positions_m(self) -> tuple[float, ...]:
        positions = [0.0]
        for spacing in self.element_spacings_m:
            positions.append(positions[-1] + spacing)
        return tuple(positions)

    @property
    def boom_length_m(self) -> float:
        positions = self.element_positions_m
        return positions[-1] - positions[0]

    @property
    def trap_capacitance_f(self) -> float:
        return 1.0 / ((2.0 * math.pi * self.trap_frequency_hz) ** 2 * self.trap_inductance_h)

    @property
    def total_conductor_length_m(self) -> float:
        return sum(self.element_lengths_m)

    @property
    def managed_load_ids(self) -> frozenset[str]:
        return frozenset(
            _load_id(index, side)
            for index in range(self.element_count)
            for side in ("left", "right")
        )

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
        loads: list[ParallelLoad] = []
        for index, (position, length) in enumerate(
            zip(self.element_positions_m, self.element_lengths_m, strict=True)
        ):
            half = length / 2.0
            wire_id = _element_id(index)
            wires.append(
                Wire(
                    id=wire_id,
                    start=point(position, -half, self.height_m),
                    end=point(position, half, self.height_m),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            for side, offset in (
                ("left", half - self.trap_inset_m),
                ("right", half + self.trap_inset_m),
            ):
                loads.append(
                    ParallelLoad(
                        id=_load_id(index, side),
                        wire_id=wire_id,
                        offset_m=offset,
                        inductance_h=self.trap_inductance_h,
                        capacitance_f=self.trap_capacitance_f,
                    )
                )
        driven = self.element_lengths_m[DRIVEN_ELEMENT_INDEX]
        return AntennaModel(
            name=name or self.template_name,
            design_frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(
                wire_id=_element_id(DRIVEN_ELEMENT_INDEX),
                offset_m=driven / 2.0,
            ),
            environment=Environment(ground=self.ground),
            loads=tuple(loads),
        )


def _element_id(index: int) -> str:
    return f"{TRAP_YAGI_ID_PREFIX}{index}"


def _load_id(index: int, side: str) -> str:
    return f"{TRAP_YAGI_LOAD_PREFIX}{index}-{side}"
