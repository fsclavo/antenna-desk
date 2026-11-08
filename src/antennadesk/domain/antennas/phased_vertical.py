# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Phased vertical array with ideal per-element amplitude and phase."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.environment import Environment
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .feed import FeedPoint, Source
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_PHASED_VERTICAL = "phased_vertical"
PHASED_VERTICAL_ID_PREFIX = "phased-vertical-"
PHASED_RADIAL_ID_PREFIX = "phased-radial-"
MIN_ELEMENTS = 2
MAX_ELEMENTS = 4
MAX_RADIALS = 36
MAX_AMPLITUDE_TAPER = 0.9


def phased_vertical_parameters(
    *,
    frequency_hz: float = 14_100_000.0,
    element_count: int = 2,
    height_m: float | None = None,
    spacing_m: float | None = None,
    base_height_m: float = 0.25,
    phase_step_deg: float = 0.0,
    amplitude_taper: float = 0.0,
    radial_count: int = 4,
    radial_length_m: float | None = None,
    radial_angle_deg: float = 0.0,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> PhasedVerticalParameters:
    """Return a quarter-wave-spaced starting phased vertical array."""

    from ..design.formulas import quarter_wave_length_m

    quarter = quarter_wave_length_m(frequency_hz)
    return PhasedVerticalParameters(
        frequency_hz=frequency_hz,
        element_count=element_count,
        height_m=quarter if height_m is None else height_m,
        spacing_m=quarter if spacing_m is None else spacing_m,
        base_height_m=base_height_m,
        phase_step_deg=phase_step_deg,
        amplitude_taper=amplitude_taper,
        radial_count=radial_count,
        radial_length_m=quarter if radial_length_m is None else radial_length_m,
        radial_angle_deg=radial_angle_deg,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


@dataclass(frozen=True, slots=True)
class PhasedVerticalParameters:
    """A line of vertical radiators driven with an ideal phase progression.

    Elements are spaced along the array line and each has its own radial
    screen. The first element is the primary feed (unit amplitude, zero phase);
    later elements use ``index * phase_step_deg`` and a linear amplitude taper
    from 1.0 to ``1 - amplitude_taper``. The combining network is ideal: no
    feed-line loss or mutual-impedance matching network is modeled here.
    """

    frequency_hz: float
    height_m: float
    spacing_m: float
    element_count: int = MIN_ELEMENTS
    base_height_m: float = 0.25
    phase_step_deg: float = 0.0
    amplitude_taper: float = 0.0
    radial_count: int = 4
    radial_length_m: float = 0.0
    radial_angle_deg: float = 0.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.height_m, name="height_m")
        ensure_positive(self.spacing_m, name="spacing_m")
        if not MIN_ELEMENTS <= self.element_count <= MAX_ELEMENTS:
            raise ValueError(f"element_count must be between {MIN_ELEMENTS} and {MAX_ELEMENTS}")
        ensure_non_negative(self.base_height_m, name="base_height_m")
        if not math.isfinite(self.phase_step_deg) or abs(self.phase_step_deg) > 360.0:
            raise ValueError("phase_step_deg must be finite and within +/-360")
        if not 0.0 <= self.amplitude_taper <= MAX_AMPLITUDE_TAPER:
            raise ValueError(f"amplitude_taper must be between 0 and {MAX_AMPLITUDE_TAPER}")
        if not 0 <= self.radial_count <= MAX_RADIALS:
            raise ValueError(f"radial_count must be between 0 and {MAX_RADIALS}")
        ensure_non_negative(self.radial_length_m, name="radial_length_m")
        if self.radial_count > 0 and self.radial_length_m <= 0.0:
            raise ValueError("a radial screen requires a positive radial length")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if self.spacing_m <= 2.0 * self.wire_radius_m:
            raise ValueError("spacing_m must exceed the conductor diameter")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )
        object.__setattr__(
            self,
            "radial_angle_deg",
            units.normalize_azimuth_degrees(self.radial_angle_deg),
        )

    @property
    def template_name(self) -> str:
        return "Phased vertical array"

    @property
    def source_amplitudes(self) -> tuple[float, ...]:
        denominator = max(self.element_count - 1, 1)
        return tuple(
            1.0 - self.amplitude_taper * index / denominator for index in range(self.element_count)
        )

    @property
    def source_phases(self) -> tuple[float, ...]:
        return tuple(index * self.phase_step_deg for index in range(self.element_count))

    @property
    def total_conductor_length_m(self) -> float:
        verticals = self.element_count * self.height_m
        radials = self.element_count * self.radial_count * self.radial_length_m
        return verticals + radials

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
        vertical_ids: list[str] = []
        top_z = self.base_height_m + self.height_m
        for index in range(self.element_count):
            local_x = index * self.spacing_m
            vertical_id = f"{PHASED_VERTICAL_ID_PREFIX}{index}"
            vertical_ids.append(vertical_id)
            wires.append(
                Wire(
                    id=vertical_id,
                    start=point(local_x, 0.0, self.base_height_m),
                    end=point(local_x, 0.0, top_z),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            for radial in range(self.radial_count):
                radial_angle = math.radians(
                    self.radial_angle_deg + 360.0 * radial / self.radial_count
                )
                wires.append(
                    Wire(
                        id=f"{PHASED_RADIAL_ID_PREFIX}{index}-{radial}",
                        start=point(local_x, 0.0, self.base_height_m),
                        end=point(
                            local_x + self.radial_length_m * math.cos(radial_angle),
                            self.radial_length_m * math.sin(radial_angle),
                            self.base_height_m,
                        ),
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    )
                )
        sources = tuple(
            Source(
                wire_id=vertical_ids[index],
                offset_m=0.0,
                amplitude=self.source_amplitudes[index],
                phase_deg=self.source_phases[index],
            )
            for index in range(1, self.element_count)
        )
        return AntennaModel(
            name=name or self.template_name,
            design_frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(vertical_ids[0], 0.0),
            environment=Environment(ground=self.ground),
            sources=sources,
        )
