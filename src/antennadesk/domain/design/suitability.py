# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Structured antenna suitability profiles for the guided advisor.

The profiles are application heuristics, not validated performance claims.
They capture the practical envelope of each catalog family: which bands it can
cover, how much space and height it typically needs, whether it is directional
or portable, and which feed hardware it implies. The advisor uses hard
constraints and transparent reasons; it does not run the solver to rank every
candidate.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..common.units import ensure_non_negative, ensure_positive

HF_BANDS: frozenset[str] = frozenset({"80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m"})
"""HF bands covered by the first advisor slice."""


class OperatingIntent(StrEnum):
    """The operator's main goal, used as a soft preference."""

    NVIS = "nvis"
    REGIONAL = "regional"
    DX = "dx"
    RECEIVE = "receive"


class Complexity(StrEnum):
    """Relative construction and tuning effort."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    ADVANCED = "advanced"

    @property
    def rank(self) -> int:
        return {Complexity.SIMPLE: 0, Complexity.MODERATE: 1, Complexity.ADVANCED: 2}[self]


class TunerRequirement(StrEnum):
    """Whether a tuner is needed for the advertised bands."""

    NONE = "none"
    OPTIONAL = "optional"
    REQUIRED = "required"


class FeedClass(StrEnum):
    """The feed arrangement a family typically implies."""

    DIRECT = "direct"
    TUNER = "tuner"
    TRANSFORMER = "transformer"
    MATCHING = "matching"


class GainClass(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TakeoffClass(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BandwidthClass(StrEnum):
    NARROW = "narrow"
    MODERATE = "moderate"
    WIDE = "wide"


@dataclass(frozen=True, slots=True)
class SuitabilityProfile:
    """Practical envelope of one catalog family.

    ``footprint_m`` is a typical horizontal span at ``footprint_reference_hz``.
    When ``footprint_scales`` is true, the advisor scales it by the wavelength
    ratio for the lowest requested band. The value is a planning heuristic, not
    a construction dimension.
    """

    catalog_key: str
    bands: frozenset[str]
    multiband: bool
    min_height_m: float
    recommended_height_m: float
    footprint_m: float
    footprint_reference_hz: float = 7_100_000.0
    footprint_scales: bool = True
    directional: bool = False
    tuner: TunerRequirement = TunerRequirement.NONE
    complexity: Complexity = Complexity.SIMPLE
    portable: bool = True
    intents: frozenset[OperatingIntent] = frozenset()
    gain_class: GainClass = GainClass.LOW
    takeoff_class: TakeoffClass = TakeoffClass.MEDIUM
    bandwidth_class: BandwidthClass = BandwidthClass.NARROW
    feed: FeedClass = FeedClass.DIRECT
    evidence_level: str = "B"

    def __post_init__(self) -> None:
        if not self.catalog_key.strip():
            raise ValueError("suitability catalog_key must not be empty")
        if not self.bands:
            raise ValueError("suitability bands must not be empty")
        ensure_non_negative(self.min_height_m, name="min_height_m")
        ensure_non_negative(self.recommended_height_m, name="recommended_height_m")
        if self.recommended_height_m < self.min_height_m:
            raise ValueError("recommended_height_m must be at least min_height_m")
        ensure_positive(self.footprint_m, name="footprint_m")
        ensure_positive(self.footprint_reference_hz, name="footprint_reference_hz")
        if not self.intents:
            raise ValueError("suitability intents must not be empty")
        if self.evidence_level not in {"A", "B", "C"}:
            raise ValueError("evidence_level must be A, B, or C")
        object.__setattr__(self, "bands", frozenset(self.bands))
        object.__setattr__(self, "intents", frozenset(self.intents))

    def footprint_at(self, lowest_frequency_hz: float) -> float:
        """Return the typical horizontal span at ``lowest_frequency_hz``."""

        ensure_positive(lowest_frequency_hz, name="lowest_frequency_hz")
        if not self.footprint_scales:
            return self.footprint_m
        return self.footprint_m * self.footprint_reference_hz / lowest_frequency_hz


_HF_ALL = HF_BANDS
_HF_MULTIBAND = frozenset({"80m", "40m", "20m", "15m", "10m"})
_HF_OCFD = frozenset({"80m", "40m", "20m", "10m"})
_HF_FAN = frozenset({"80m", "40m", "20m", "10m"})

SUITABILITY_PROFILES: tuple[SuitabilityProfile, ...] = (
    SuitabilityProfile(
        catalog_key="wire_dipole",
        bands=_HF_ALL,
        multiband=False,
        min_height_m=5.0,
        recommended_height_m=10.0,
        footprint_m=20.0,
        intents=frozenset(
            {
                OperatingIntent.NVIS,
                OperatingIntent.REGIONAL,
                OperatingIntent.DX,
                OperatingIntent.RECEIVE,
            }
        ),
        evidence_level="B",
    ),
    SuitabilityProfile(
        catalog_key="inverted_v",
        bands=_HF_ALL,
        multiband=False,
        min_height_m=8.0,
        recommended_height_m=12.0,
        footprint_m=21.0,
        intents=frozenset({OperatingIntent.NVIS, OperatingIntent.REGIONAL}),
        takeoff_class=TakeoffClass.HIGH,
        evidence_level="B",
    ),
    SuitabilityProfile(
        catalog_key="endfed",
        bands=_HF_MULTIBAND,
        multiband=True,
        min_height_m=8.0,
        recommended_height_m=12.0,
        footprint_m=20.0,
        tuner=TunerRequirement.OPTIONAL,
        complexity=Complexity.MODERATE,
        intents=frozenset(
            {
                OperatingIntent.NVIS,
                OperatingIntent.REGIONAL,
                OperatingIntent.DX,
            }
        ),
        bandwidth_class=BandwidthClass.MODERATE,
        feed=FeedClass.TRANSFORMER,
        evidence_level="B",
    ),
    SuitabilityProfile(
        catalog_key="ocfd",
        bands=_HF_OCFD,
        multiband=True,
        min_height_m=10.0,
        recommended_height_m=12.0,
        footprint_m=41.0,
        footprint_reference_hz=3_500_000.0,
        tuner=TunerRequirement.OPTIONAL,
        complexity=Complexity.MODERATE,
        portable=True,
        intents=frozenset({OperatingIntent.REGIONAL, OperatingIntent.DX}),
        bandwidth_class=BandwidthClass.MODERATE,
        feed=FeedClass.TRANSFORMER,
        evidence_level="B",
    ),
    SuitabilityProfile(
        catalog_key="g5rv",
        bands=_HF_MULTIBAND,
        multiband=True,
        min_height_m=10.0,
        recommended_height_m=12.0,
        footprint_m=31.0,
        footprint_reference_hz=3_500_000.0,
        tuner=TunerRequirement.REQUIRED,
        complexity=Complexity.MODERATE,
        portable=False,
        intents=frozenset({OperatingIntent.REGIONAL, OperatingIntent.DX}),
        gain_class=GainClass.MEDIUM,
        bandwidth_class=BandwidthClass.WIDE,
        feed=FeedClass.TUNER,
        evidence_level="B",
    ),
    SuitabilityProfile(
        catalog_key="vertical",
        bands=_HF_ALL,
        multiband=False,
        min_height_m=0.25,
        recommended_height_m=10.0,
        footprint_m=10.0,
        tuner=TunerRequirement.OPTIONAL,
        intents=frozenset({OperatingIntent.REGIONAL, OperatingIntent.DX}),
        takeoff_class=TakeoffClass.LOW,
        evidence_level="B",
    ),
    SuitabilityProfile(
        catalog_key="loop",
        bands=_HF_ALL,
        multiband=False,
        min_height_m=8.0,
        recommended_height_m=12.0,
        footprint_m=11.0,
        tuner=TunerRequirement.OPTIONAL,
        complexity=Complexity.MODERATE,
        portable=False,
        intents=frozenset(
            {
                OperatingIntent.REGIONAL,
                OperatingIntent.DX,
                OperatingIntent.RECEIVE,
            }
        ),
        takeoff_class=TakeoffClass.HIGH,
        bandwidth_class=BandwidthClass.MODERATE,
        feed=FeedClass.MATCHING,
        evidence_level="B",
    ),
    SuitabilityProfile(
        catalog_key="yagi",
        bands=_HF_ALL,
        multiband=False,
        min_height_m=10.0,
        recommended_height_m=15.0,
        footprint_m=11.0,
        footprint_reference_hz=14_100_000.0,
        directional=True,
        tuner=TunerRequirement.OPTIONAL,
        complexity=Complexity.ADVANCED,
        portable=False,
        intents=frozenset({OperatingIntent.DX}),
        gain_class=GainClass.HIGH,
        takeoff_class=TakeoffClass.LOW,
        feed=FeedClass.MATCHING,
        evidence_level="B",
    ),
    SuitabilityProfile(
        catalog_key="moxon",
        bands=_HF_ALL,
        multiband=False,
        min_height_m=8.0,
        recommended_height_m=12.0,
        footprint_m=6.0,
        footprint_reference_hz=14_100_000.0,
        directional=True,
        tuner=TunerRequirement.OPTIONAL,
        complexity=Complexity.MODERATE,
        intents=frozenset({OperatingIntent.DX}),
        gain_class=GainClass.MEDIUM,
        takeoff_class=TakeoffClass.LOW,
        feed=FeedClass.MATCHING,
        evidence_level="B",
    ),
    SuitabilityProfile(
        catalog_key="random_wire",
        bands=_HF_ALL,
        multiband=True,
        min_height_m=6.0,
        recommended_height_m=10.0,
        footprint_m=20.0,
        tuner=TunerRequirement.REQUIRED,
        intents=frozenset(
            {
                OperatingIntent.REGIONAL,
                OperatingIntent.DX,
                OperatingIntent.RECEIVE,
            }
        ),
        bandwidth_class=BandwidthClass.WIDE,
        feed=FeedClass.TUNER,
        evidence_level="C",
    ),
    SuitabilityProfile(
        catalog_key="fan_dipole",
        bands=_HF_FAN,
        multiband=True,
        min_height_m=10.0,
        recommended_height_m=12.0,
        footprint_m=41.0,
        footprint_reference_hz=3_500_000.0,
        tuner=TunerRequirement.NONE,
        complexity=Complexity.MODERATE,
        portable=False,
        intents=frozenset({OperatingIntent.REGIONAL, OperatingIntent.DX}),
        bandwidth_class=BandwidthClass.MODERATE,
        evidence_level="C",
    ),
    SuitabilityProfile(
        catalog_key="trap_dipole",
        bands=_HF_MULTIBAND,
        multiband=True,
        min_height_m=10.0,
        recommended_height_m=12.0,
        footprint_m=33.0,
        footprint_reference_hz=3_500_000.0,
        tuner=TunerRequirement.OPTIONAL,
        complexity=Complexity.MODERATE,
        portable=False,
        intents=frozenset({OperatingIntent.REGIONAL, OperatingIntent.DX}),
        bandwidth_class=BandwidthClass.MODERATE,
        evidence_level="B",
    ),
)

PROFILES_BY_KEY: dict[str, SuitabilityProfile] = {
    profile.catalog_key: profile for profile in SUITABILITY_PROFILES
}
"""Lookup table used by the advisor and its tests."""
