# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""End-fed wire antenna."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .load import SeriesLoad
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_ENDFED = "endfed"
RADIATOR_ID = "radiator"
ENDFED_LOADING_COIL_ID = "endfed-loading-coil"

# Chameleon Antenna CHA LEFS Feather manual: 66.5 ft EFHW radiator, 49:1
# transformer near 3 ft, far end at about 25 ft.
SLOPER_REFERENCE_LENGTH_M = 66.5 * 0.3048
SLOPER_REFERENCE_FEED_HEIGHT_M = 3.0 * 0.3048
SLOPER_REFERENCE_END_HEIGHT_M = 25.0 * 0.3048
SLOPER_REFERENCE_TRANSFORMER_RATIO = 49.0

# ARRL End-Fed Half-Wave Antenna Kit: 66 ft on 40 m, 33 ft on 20 m, 16 ft on
# 10 m, with a 49:1 transformer. The counterpoise is the PA9X 0.05-wavelength
# starting rule.
EFHW_PRESET_LENGTHS_M = {
    "40m": 66.0 * 0.3048,
    "20m": 33.0 * 0.3048,
    "10m": 16.0 * 0.3048,
}
EFHW_PRESET_FREQUENCIES_HZ = {
    "40m": 7_100_000.0,
    "20m": 14_100_000.0,
    "10m": 28_400_000.0,
}
EFHW_TRANSFORMER_RATIO = 49.0
EFHW_COUNTERPOISE_FRACTION = 0.05

# Published shortened EFHW references. The first design is the G0KYA
# 80-10 m antenna, also documented by EA7EER and G4WIF as 20.35 m + 110 uH +
# 2.39 m. The second is the 40-20-10 m schematic supplied with the radioaficion
# / PA0EJH reference: 10.01 m + 23 uH + 1.85 m.
SHORTENED_80_10_REFERENCE_FREQUENCY_HZ = 3_650_000.0
SHORTENED_80_10_LOWER_LENGTH_M = 20.35
SHORTENED_80_10_TOP_LENGTH_M = 2.39
SHORTENED_80_10_INDUCTANCE_H = 110e-6
SHORTENED_40_10_REFERENCE_FREQUENCY_HZ = 7_100_000.0
SHORTENED_40_10_LOWER_LENGTH_M = 10.01
SHORTENED_40_10_TOP_LENGTH_M = 1.85
SHORTENED_40_10_INDUCTANCE_H = 23e-6
SHORTENED_EFHW_TRANSFORMER_RATIO = 49.0


class EndFedPreset(StrEnum):
    STANDARD = "endfed"
    SLOPER = "sloper"
    RANDOM_WIRE = "random_wire"
    SHORTENED_80_10 = "shortened_80_10"
    SHORTENED_40_10 = "shortened_40_10"


COUNTERPOISE_ID = "counterpoise"
COUNTERPOISE_DROP_ID = "counterpoise-drop"
FEED_SECTION_ID = "endfed-feed-section"
LOADING_COIL_SECTION_ID = "endfed-loading-coil-section"
RADIATOR_TOP_ID = "radiator-top"
INSTALLATION_RETURN_ID = "endfed-installation-return"
INSTALLATION_RETURN_DROP_ID = "endfed-installation-return-drop"
DEFAULT_FEED_SECTION_LENGTH_M = 0.5
DEFAULT_INSTALLATION_RETURN_LENGTH_M = 0.10
ENDFED_FEED_SECTION_SEGMENTS = 3
ENDFED_LOADING_COIL_SECTION_LENGTH_M = 0.10
ENDFED_LOADING_COIL_SECTION_SEGMENTS = 3
MODEL_ONLY_WIRE_IDS = frozenset({INSTALLATION_RETURN_ID, INSTALLATION_RETURN_DROP_ID})


def is_model_only_wire(wire_id: str) -> bool:
    """Return whether a wire is a numerical model proxy, not physical hardware."""

    return wire_id in MODEL_ONLY_WIRE_IDS


@dataclass(frozen=True, slots=True)
class EndFedParameters:
    """A single wire fed at one end, optionally sloping to a different height."""

    frequency_hz: float
    length_m: float
    feed_section_length_m: float = 0.0
    installation_return_length_m: float = 0.0
    feed_height_m: float = 10.0
    end_height_m: float = 10.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.001
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE
    transformer_ratio: float = 1.0
    counterpoise_length_m: float = 0.0
    counterpoise_height_m: float = 0.1
    counterpoise_azimuth_deg: float | None = None
    loading_coil_enabled: bool = False
    loading_coil_offset_m: float = 0.0
    loading_coil_inductance_h: float = 0.0
    loading_coil_resistance_ohm: float = 0.0
    preset: EndFedPreset = EndFedPreset.STANDARD

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.length_m, name="length_m")
        ensure_non_negative(self.feed_section_length_m, name="feed_section_length_m")
        ensure_non_negative(
            self.installation_return_length_m,
            name="installation_return_length_m",
        )
        if self.feed_section_length_m >= self.length_m:
            raise ValueError("feed_section_length_m must be shorter than length_m")
        ensure_non_negative(self.feed_height_m, name="feed_height_m")
        ensure_non_negative(self.end_height_m, name="end_height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        ensure_positive(self.transformer_ratio, name="transformer_ratio")
        object.__setattr__(self, "preset", EndFedPreset(self.preset))
        ensure_non_negative(self.counterpoise_length_m, name="counterpoise_length_m")
        ensure_non_negative(self.counterpoise_height_m, name="counterpoise_height_m")
        ensure_non_negative(self.loading_coil_offset_m, name="loading_coil_offset_m")
        ensure_non_negative(
            self.loading_coil_inductance_h,
            name="loading_coil_inductance_h",
        )
        ensure_non_negative(
            self.loading_coil_resistance_ohm,
            name="loading_coil_resistance_ohm",
        )
        if self.loading_coil_offset_m > self.length_m:
            raise ValueError("loading_coil_offset_m must not exceed length_m")
        if self.loading_coil_enabled:
            ensure_positive(
                self.loading_coil_inductance_h,
                name="loading_coil_inductance_h",
            )
            if self.loading_coil_offset_m <= 0.0:
                raise ValueError("loading_coil_offset_m must be positive when the coil is enabled")
        if abs(self.end_height_m - self.feed_height_m) > self.length_m + 1e-12:
            raise ValueError(
                "the height difference between the feed and the end must not exceed the wire length"
            )
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )
        if self.counterpoise_azimuth_deg is not None:
            object.__setattr__(
                self,
                "counterpoise_azimuth_deg",
                units.normalize_azimuth_degrees(self.counterpoise_azimuth_deg),
            )

    @property
    def coil_active(self) -> bool:
        return self.loading_coil_enabled and self.loading_coil_inductance_h > 0.0

    @property
    def feed_section_active(self) -> bool:
        return self.feed_section_length_m > 0.0

    @property
    def loading_coil_section_active(self) -> bool:
        if not self.coil_active:
            return False
        half_section_m = ENDFED_LOADING_COIL_SECTION_LENGTH_M / 2.0
        section_start_m = self.loading_coil_offset_m - half_section_m
        section_end_m = self.loading_coil_offset_m + half_section_m
        return (
            section_start_m > self.feed_section_length_m + 1e-9
            and section_end_m < self.length_m - 1e-9
        )

    @property
    def loading_coil_section_start_m(self) -> float:
        return self.loading_coil_offset_m - ENDFED_LOADING_COIL_SECTION_LENGTH_M / 2.0

    @property
    def loading_coil_section_end_m(self) -> float:
        return self.loading_coil_offset_m + ENDFED_LOADING_COIL_SECTION_LENGTH_M / 2.0

    @property
    def loading_coil_lower_length_m(self) -> float:
        if not self.loading_coil_section_active:
            return 0.0
        return max(self.loading_coil_section_start_m - self.feed_section_length_m, 0.0)

    @property
    def loading_coil_upper_length_m(self) -> float:
        if not self.loading_coil_section_active:
            return 0.0
        return max(self.length_m - self.loading_coil_section_end_m, 0.0)

    @property
    def main_radiator_length_m(self) -> float:
        return max(self.length_m - self.feed_section_length_m, 0.0)

    @property
    def installation_return_active(self) -> bool:
        return self.counterpoise_length_m <= 0.0 and self.installation_return_length_m > 0.0

    @property
    def effective_return_length_m(self) -> float:
        if self.counterpoise_length_m > 0.0:
            return self.counterpoise_length_m
        return self.installation_return_length_m

    @property
    def managed_load_ids(self) -> frozenset[str]:
        if not self.coil_active:
            return frozenset()
        return frozenset({ENDFED_LOADING_COIL_ID})

    @property
    def loading_coil_q(self) -> float | None:
        if not self.coil_active or self.loading_coil_resistance_ohm <= 0.0:
            return None
        reactance = 2.0 * math.pi * self.frequency_hz * self.loading_coil_inductance_h
        return reactance / self.loading_coil_resistance_ohm

    @property
    def loading_coil_top_length_m(self) -> float:
        if not self.coil_active:
            return 0.0
        return max(self.length_m - self.loading_coil_offset_m, 0.0)

    @property
    def template_name(self) -> str:
        return {
            EndFedPreset.STANDARD: "End-fed",
            EndFedPreset.SLOPER: "Sloper",
            EndFedPreset.RANDOM_WIRE: "Random wire",
            EndFedPreset.SHORTENED_80_10: "Shortened EFHW 80-10 m",
            EndFedPreset.SHORTENED_40_10: "Shortened EFHW 40-20-10 m",
        }[self.preset]

    @property
    def effective_counterpoise_azimuth_deg(self) -> float:
        if self.counterpoise_azimuth_deg is not None:
            return self.counterpoise_azimuth_deg
        return (self.azimuth_deg + 180.0) % 360.0

    def to_antenna(self, *, name: str = "End-fed wire") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        rise = self.end_height_m - self.feed_height_m
        horizontal_m = math.sqrt(max(self.length_m * self.length_m - rise * rise, 0.0))
        feed_point = Point3D(x_m=0.0, y_m=0.0, z_m=self.feed_height_m)
        end_point = Point3D(
            x_m=horizontal_m * math.cos(angle),
            y_m=horizontal_m * math.sin(angle),
            z_m=self.end_height_m,
        )

        def point_at(distance_m: float) -> Point3D:
            ratio = distance_m / self.length_m
            return Point3D(
                x_m=feed_point.x_m + (end_point.x_m - feed_point.x_m) * ratio,
                y_m=feed_point.y_m + (end_point.y_m - feed_point.y_m) * ratio,
                z_m=feed_point.z_m + (end_point.z_m - feed_point.z_m) * ratio,
            )

        wires: list[Wire] = []
        if self.feed_section_active:
            feed_end = point_at(self.feed_section_length_m)
            wires.append(
                Wire(
                    id=FEED_SECTION_ID,
                    start=feed_point,
                    end=feed_end,
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )
            radiator_start = feed_end
            feed_wire_id = FEED_SECTION_ID
        else:
            radiator_start = feed_point
            feed_wire_id = RADIATOR_ID
        if self.loading_coil_section_active:
            coil_start = point_at(self.loading_coil_section_start_m)
            coil_end = point_at(self.loading_coil_section_end_m)
            wires.extend(
                [
                    Wire(
                        id=RADIATOR_ID,
                        start=radiator_start,
                        end=coil_start,
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                    Wire(
                        id=LOADING_COIL_SECTION_ID,
                        start=coil_start,
                        end=coil_end,
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                    Wire(
                        id=RADIATOR_TOP_ID,
                        start=coil_end,
                        end=end_point,
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    ),
                ]
            )
        else:
            wires.append(
                Wire(
                    id=RADIATOR_ID,
                    start=radiator_start,
                    end=end_point,
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )

        if self.effective_return_length_m > 0.0:
            counterpoise_angle = units.degrees_to_radians(self.effective_counterpoise_azimuth_deg)
            return_height_m = 0.0 if self.installation_return_active else self.counterpoise_height_m
            counterpoise_start = Point3D(
                x_m=0.0,
                y_m=0.0,
                z_m=return_height_m,
            )
            if not math.isclose(self.feed_height_m, return_height_m):
                wires.append(
                    Wire(
                        id=(
                            INSTALLATION_RETURN_DROP_ID
                            if self.installation_return_active
                            else COUNTERPOISE_DROP_ID
                        ),
                        start=feed_point,
                        end=counterpoise_start,
                        radius_m=self.wire_radius_m,
                        material=self.material,
                    )
                )
            wires.append(
                Wire(
                    id=(
                        INSTALLATION_RETURN_ID
                        if self.installation_return_active
                        else COUNTERPOISE_ID
                    ),
                    start=counterpoise_start,
                    end=Point3D(
                        x_m=self.effective_return_length_m * math.cos(counterpoise_angle),
                        y_m=self.effective_return_length_m * math.sin(counterpoise_angle),
                        z_m=return_height_m,
                    ),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )

        loads: tuple[SeriesLoad, ...] = ()
        if self.coil_active:
            if self.loading_coil_section_active:
                coil_wire_id = LOADING_COIL_SECTION_ID
                coil_offset_m = ENDFED_LOADING_COIL_SECTION_LENGTH_M / 2.0
            elif (
                self.feed_section_active and self.loading_coil_offset_m < self.feed_section_length_m
            ):
                coil_wire_id = FEED_SECTION_ID
                coil_offset_m = self.loading_coil_offset_m
            else:
                coil_wire_id = RADIATOR_ID
                coil_offset_m = self.loading_coil_offset_m - (
                    self.feed_section_length_m if self.feed_section_active else 0.0
                )
            loads = (
                SeriesLoad(
                    id=ENDFED_LOADING_COIL_ID,
                    wire_id=coil_wire_id,
                    offset_m=coil_offset_m,
                    inductance_h=self.loading_coil_inductance_h,
                    resistance_ohm=self.loading_coil_resistance_ohm,
                ),
            )

        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(feed_wire_id, 0.0),
            ground=self.ground,
            loads=loads,
            generator_id="endfed",
            generator_name=self.template_name,
        )


def endfed_segmentation_overrides(
    parameters: EndFedParameters,
) -> tuple[tuple[str, int], ...]:
    """Return the fixed segmentation for the end-fed model partitions."""

    overrides: list[tuple[str, int]] = []
    if parameters.feed_section_active:
        overrides.append((FEED_SECTION_ID, ENDFED_FEED_SECTION_SEGMENTS))
    if parameters.loading_coil_section_active:
        overrides.append((LOADING_COIL_SECTION_ID, ENDFED_LOADING_COIL_SECTION_SEGMENTS))
    return tuple(overrides)


def endfed_model_warning_keys(parameters: EndFedParameters) -> tuple[str, ...]:
    """Return user-visible warning keys for a numerically fragile model."""

    keys: list[str] = []
    if not parameters.feed_section_active:
        keys.append("endfed.warning.feed_section")
    if parameters.effective_return_length_m <= 0.0:
        keys.append("endfed.warning.return")
    return tuple(keys)


def efhw_parameters(
    band_id: str,
    *,
    feed_height_m: float = 10.0,
    end_height_m: float = 10.0,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> EndFedParameters:
    """Return the published ARRL EFHW kit starting geometry for a band."""

    if band_id not in EFHW_PRESET_LENGTHS_M:
        raise ValueError(f"unsupported EFHW preset band: {band_id!r}")
    frequency_hz = EFHW_PRESET_FREQUENCIES_HZ[band_id]
    wavelength_m = units.wavelength_m(frequency_hz)
    return EndFedParameters(
        frequency_hz=frequency_hz,
        length_m=EFHW_PRESET_LENGTHS_M[band_id],
        feed_section_length_m=DEFAULT_FEED_SECTION_LENGTH_M,
        feed_height_m=feed_height_m,
        end_height_m=end_height_m,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
        transformer_ratio=EFHW_TRANSFORMER_RATIO,
        counterpoise_length_m=EFHW_COUNTERPOISE_FRACTION * wavelength_m,
        counterpoise_height_m=0.1,
        preset=EndFedPreset.STANDARD,
    )


def sloper_parameters(
    *,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> EndFedParameters:
    """Return the published Chameleon LEFS 40 m EFHW sloper geometry."""

    return EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=SLOPER_REFERENCE_LENGTH_M,
        feed_section_length_m=DEFAULT_FEED_SECTION_LENGTH_M,
        installation_return_length_m=DEFAULT_INSTALLATION_RETURN_LENGTH_M,
        feed_height_m=SLOPER_REFERENCE_FEED_HEIGHT_M,
        end_height_m=SLOPER_REFERENCE_END_HEIGHT_M,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
        transformer_ratio=SLOPER_REFERENCE_TRANSFORMER_RATIO,
        preset=EndFedPreset.SLOPER,
    )


def shortened_efhw_80_10_parameters(
    *,
    feed_height_m: float = 10.0,
    end_height_m: float | None = None,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel | None = None,
) -> EndFedParameters:
    """Return the published 80-10 m shortened EFHW with a 110 uH coil.

    The source dimensions are 20.35 m from the feed to the coil and 2.39 m
    after it. The default installation is horizontal at 10 m; pass both
    ``feed_height_m`` and ``end_height_m`` for a sloper or vertical run. The
    published inverted-L bend and the matching unit are construction notes, not
    modeled geometry.
    """

    length_m = SHORTENED_80_10_LOWER_LENGTH_M + SHORTENED_80_10_TOP_LENGTH_M
    return EndFedParameters(
        frequency_hz=SHORTENED_80_10_REFERENCE_FREQUENCY_HZ,
        length_m=length_m,
        feed_section_length_m=DEFAULT_FEED_SECTION_LENGTH_M,
        installation_return_length_m=DEFAULT_INSTALLATION_RETURN_LENGTH_M,
        feed_height_m=feed_height_m,
        end_height_m=feed_height_m if end_height_m is None else end_height_m,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=(
            GroundModel.finite(
                relative_permittivity=13.0,
                conductivity_s_per_m=0.005,
            )
            if ground is None
            else ground
        ),
        transformer_ratio=SHORTENED_EFHW_TRANSFORMER_RATIO,
        loading_coil_enabled=True,
        loading_coil_offset_m=SHORTENED_80_10_LOWER_LENGTH_M,
        loading_coil_inductance_h=SHORTENED_80_10_INDUCTANCE_H,
        loading_coil_resistance_ohm=0.0,
        preset=EndFedPreset.SHORTENED_80_10,
    )


def shortened_efhw_40_10_parameters(
    *,
    feed_height_m: float = 10.0,
    end_height_m: float | None = None,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel | None = None,
) -> EndFedParameters:
    """Return the published 40-20-10 m shortened EFHW with a 23 uH coil.

    The source schematic is 10.01 m from the feed to the coil and 1.85 m after
    it. The default installation is horizontal at 10 m; pass both
    ``feed_height_m`` and ``end_height_m`` for a sloper or vertical run. The
    matching unit and straight-wire approximation are documented limitations.
    """

    length_m = SHORTENED_40_10_LOWER_LENGTH_M + SHORTENED_40_10_TOP_LENGTH_M
    return EndFedParameters(
        frequency_hz=SHORTENED_40_10_REFERENCE_FREQUENCY_HZ,
        length_m=length_m,
        feed_section_length_m=DEFAULT_FEED_SECTION_LENGTH_M,
        installation_return_length_m=DEFAULT_INSTALLATION_RETURN_LENGTH_M,
        feed_height_m=feed_height_m,
        end_height_m=feed_height_m if end_height_m is None else end_height_m,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=(
            GroundModel.finite(
                relative_permittivity=13.0,
                conductivity_s_per_m=0.005,
            )
            if ground is None
            else ground
        ),
        transformer_ratio=SHORTENED_EFHW_TRANSFORMER_RATIO,
        loading_coil_enabled=True,
        loading_coil_offset_m=SHORTENED_40_10_LOWER_LENGTH_M,
        loading_coil_inductance_h=SHORTENED_40_10_INDUCTANCE_H,
        loading_coil_resistance_ohm=0.0,
        preset=EndFedPreset.SHORTENED_40_10,
    )
