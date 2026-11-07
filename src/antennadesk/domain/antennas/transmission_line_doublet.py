# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Typed G5RV and ZS6BKW doublet presets with a geometry matching line."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .g5rv import (
    G5RV_DIPOLE_TOTAL_LENGTH_M,
    G5RV_LINE_OPTIONS,
    g5rv_parameters,
)
from .materials import COPPER, ConductorMaterial
from .zs6bkw import ZS6BKW_VARIANTS, ZS6BKWVariant, zs6bkw_parameters

ANTENNA_TYPE_G5RV = "g5rv"
ANTENNA_TYPE_ZS6BKW = "zs6bkw"
SOURCE_WIRE_LENGTH_M = 0.1
G5RV_DEFAULT_LINE_IMPEDANCE_OHM = 450.0
G5RV_DEFAULT_LINE_LENGTH_M = G5RV_LINE_OPTIONS[1].length_m
ZS6BKW_DEFAULT_LINE_IMPEDANCE_OHM = ZS6BKW_VARIANTS[0].characteristic_impedance_ohm
ZS6BKW_DEFAULT_LINE_LENGTH_M = ZS6BKW_VARIANTS[0].line_length_m


class DoubletPreset(StrEnum):
    G5RV = "g5rv"
    ZS6BKW = "zs6bkw"

    @property
    def antenna_type(self) -> str:
        return ANTENNA_TYPE_G5RV if self is DoubletPreset.G5RV else ANTENNA_TYPE_ZS6BKW

    @property
    def template_name(self) -> str:
        return "G5RV" if self is DoubletPreset.G5RV else "ZS6BKW"


@dataclass(frozen=True, slots=True)
class TransmissionLineDoubletParameters:
    """A center-fed doublet with a real two-wire matching section.

    The source wire is a short vertical stub at the feed point. The matching
    line is geometry, not the project-level feed-line post-processing model.
    Published G5RV and ZS6BKW dimensions are starting points; height, ground,
    line velocity factor, and the installation change the match.
    """

    frequency_hz: float
    preset: DoubletPreset
    dipole_total_length_m: float
    height_m: float = 10.0
    feed_height_m: float = 1.0
    azimuth_deg: float = 0.0
    line_impedance_ohm: float = G5RV_DEFAULT_LINE_IMPEDANCE_OHM
    line_length_m: float = G5RV_DEFAULT_LINE_LENGTH_M
    line_velocity_factor: float = 1.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        object.__setattr__(self, "preset", DoubletPreset(self.preset))
        ensure_positive(self.dipole_total_length_m, name="dipole_total_length_m")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_non_negative(self.feed_height_m, name="feed_height_m")
        ensure_positive(self.line_impedance_ohm, name="line_impedance_ohm")
        ensure_positive(self.line_length_m, name="line_length_m")
        ensure_positive(self.line_velocity_factor, name="line_velocity_factor")
        if self.line_velocity_factor > 1.0:
            raise ValueError("line_velocity_factor must not exceed 1")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return self.preset.template_name

    @property
    def source_wire_length_m(self) -> float:
        return SOURCE_WIRE_LENGTH_M

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name or self.template_name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        if self.preset is DoubletPreset.G5RV:
            return g5rv_parameters(
                frequency_hz=self.frequency_hz,
                height_m=self.height_m,
                feed_height_m=self.feed_height_m,
                azimuth_deg=self.azimuth_deg,
                line_impedance_ohm=self.line_impedance_ohm,
                line_length_m=self.line_length_m,
                line_velocity_factor=self.line_velocity_factor,
                wire_radius_m=self.wire_radius_m,
                material=self.material,
                ground=self.ground,
            )
        return zs6bkw_parameters(
            frequency_hz=self.frequency_hz,
            height_m=self.height_m,
            feed_height_m=self.feed_height_m,
            azimuth_deg=self.azimuth_deg,
            variant=ZS6BKWVariant(
                dipole_total_length_m=self.dipole_total_length_m,
                characteristic_impedance_ohm=self.line_impedance_ohm,
                line_length_m=self.line_length_m,
            ),
            line_velocity_factor=self.line_velocity_factor,
            wire_radius_m=self.wire_radius_m,
            material=self.material,
            ground=self.ground,
        )


def doublet_starting_parameters(
    preset: DoubletPreset,
    *,
    frequency_hz: float = 14_100_000.0,
    height_m: float = 10.0,
    feed_height_m: float = 1.0,
    azimuth_deg: float = 0.0,
    line_impedance_ohm: float | None = None,
    line_length_m: float | None = None,
    line_velocity_factor: float = 1.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> TransmissionLineDoubletParameters:
    preset = DoubletPreset(preset)
    if preset is DoubletPreset.G5RV:
        default_length = G5RV_DIPOLE_TOTAL_LENGTH_M
        default_impedance = G5RV_DEFAULT_LINE_IMPEDANCE_OHM
        default_line_length = G5RV_DEFAULT_LINE_LENGTH_M
    else:
        default_length = ZS6BKW_VARIANTS[0].dipole_total_length_m
        default_impedance = ZS6BKW_DEFAULT_LINE_IMPEDANCE_OHM
        default_line_length = ZS6BKW_DEFAULT_LINE_LENGTH_M
    return TransmissionLineDoubletParameters(
        frequency_hz=frequency_hz,
        preset=preset,
        dipole_total_length_m=default_length,
        height_m=height_m,
        feed_height_m=feed_height_m,
        azimuth_deg=azimuth_deg,
        line_impedance_ohm=(
            default_impedance if line_impedance_ohm is None else line_impedance_ohm
        ),
        line_length_m=default_line_length if line_length_m is None else line_length_m,
        line_velocity_factor=line_velocity_factor,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )
