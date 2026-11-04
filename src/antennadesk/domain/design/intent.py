# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""User intent for frequency-first antenna dimension estimation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ..antennas.dipole import DipoleOrientation
from ..antennas.materials import COPPER, ConductorMaterial
from ..antennas.polarization import Polarization
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel


class LoopShape(StrEnum):
    LOOP = "loop"
    QUAD = "quad"
    DELTA = "delta"

    @property
    def sides(self) -> int:
        if self is LoopShape.DELTA:
            return 3
        if self is LoopShape.QUAD:
            return 4
        return 16


class VerticalForm(StrEnum):
    QUARTER_WAVE = "quarter_wave"
    HALF_WAVE = "half_wave"
    FIVE_EIGHTH_WAVE = "five_eighth_wave"


@dataclass(frozen=True, slots=True)
class DesignIntent:
    """Common intent fields used by every family estimator.

    Not every field applies to every family. Estimators validate the fields
    they use and ignore the rest.
    """

    frequency_hz: float
    antenna_type: str
    height_m: float = 10.0
    base_height_m: float = 0.0
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL
    polarization: Polarization = Polarization.HORIZONTAL
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE
    loop_shape: LoopShape = LoopShape.QUAD
    vertical_form: VerticalForm = VerticalForm.QUARTER_WAVE
    folded: bool = False
    included_angle_deg: float = 120.0
    radial_count: int = 4
    radial_length_m: float | None = None
    feed_offset_m: float | None = None
    gap_m: float = 0.01
    fan_bands_hz: tuple[float, ...] = ()
    yagi_elements: int = 5
    end_height_m: float | None = None
    highest_frequency_hz: float | None = None

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_non_negative(self.base_height_m, name="base_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if not self.antenna_type.strip():
            raise ValueError("antenna_type must not be empty")
        object.__setattr__(self, "orientation", DipoleOrientation(self.orientation))
        object.__setattr__(self, "polarization", Polarization(self.polarization))
        object.__setattr__(self, "loop_shape", LoopShape(self.loop_shape))
        object.__setattr__(self, "vertical_form", VerticalForm(self.vertical_form))
        if not 0.0 < self.included_angle_deg < 180.0:
            raise ValueError("included_angle_deg must be between 0 and 180")
        if not 0 <= self.radial_count <= 128:
            raise ValueError("radial_count must be between 0 and 128")
        if self.radial_length_m is not None:
            ensure_positive(self.radial_length_m, name="radial_length_m")
        if self.feed_offset_m is not None:
            ensure_non_negative(self.feed_offset_m, name="feed_offset_m")
        if self.gap_m <= 0.0:
            raise ValueError("gap_m must be positive")
        if self.fan_bands_hz:
            object.__setattr__(self, "fan_bands_hz", tuple(self.fan_bands_hz))
            for band in self.fan_bands_hz:
                ensure_positive(band, name="fan band")
        if self.yagi_elements < 2:
            raise ValueError("yagi_elements must be at least 2")
        if self.end_height_m is not None:
            ensure_non_negative(self.end_height_m, name="end_height_m")
        if self.highest_frequency_hz is not None:
            ensure_positive(self.highest_frequency_hz, name="highest_frequency_hz")
            if self.highest_frequency_hz <= self.frequency_hz:
                raise ValueError("highest_frequency_hz must exceed frequency_hz")
        if not math.isfinite(self.azimuth_deg):
            raise ValueError("azimuth_deg must be finite")
