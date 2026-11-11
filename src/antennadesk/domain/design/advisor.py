# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic antenna advisor built on suitability profiles.

The advisor applies hard constraints first, then orders the surviving profiles
by transparent preferences. It never runs the solver and never produces a magic
score: every candidate carries reasons, warnings, and its evidence level.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ..common.units import ensure_positive
from ..simulation.bands import amateur_band_by_id
from .suitability import (
    SUITABILITY_PROFILES,
    Complexity,
    OperatingIntent,
    SuitabilityProfile,
    TunerRequirement,
)

MAX_CANDIDATES = 3


class FitStatus(StrEnum):
    EXCELLENT = "excellent"
    GOOD = "good"
    CONDITIONAL = "conditional"

    @property
    def rank(self) -> int:
        return {
            FitStatus.EXCELLENT: 0,
            FitStatus.GOOD: 1,
            FitStatus.CONDITIONAL: 2,
        }[self]


class Directionality(StrEnum):
    OMNI = "omni"
    DIRECTIONAL = "directional"


class AdvisorBlocker(StrEnum):
    BANDS = "bands"
    SPACE = "space"
    HEIGHT = "height"
    PORTABLE = "portable"
    TUNER = "tuner"
    COMPLEXITY = "complexity"
    PATTERN = "pattern"


@dataclass(frozen=True, slots=True)
class AdvisorRequest:
    """The user's practical constraints and preferences."""

    bands: frozenset[str]
    multiband_required: bool = True
    available_height_m: float | None = None
    available_width_m: float | None = None
    portable: bool = False
    intent: OperatingIntent = OperatingIntent.REGIONAL
    tuner_available: bool = False
    max_complexity: Complexity = Complexity.MODERATE
    directionality: Directionality | None = None

    def __post_init__(self) -> None:
        bands = frozenset(self.bands)
        if not bands:
            raise ValueError("advisor request needs at least one band")
        for band in bands:
            if amateur_band_by_id(band) is None:
                raise ValueError(f"unknown amateur band: {band}")
        if self.available_height_m is not None:
            ensure_positive(self.available_height_m, name="available_height_m")
        if self.available_width_m is not None:
            ensure_positive(self.available_width_m, name="available_width_m")
        object.__setattr__(self, "bands", bands)
        object.__setattr__(self, "intent", OperatingIntent(self.intent))
        object.__setattr__(self, "max_complexity", Complexity(self.max_complexity))
        if self.directionality is not None:
            object.__setattr__(self, "directionality", Directionality(self.directionality))


@dataclass(frozen=True, slots=True)
class AdvisorCandidate:
    """One profile that passed the hard constraints."""

    profile: SuitabilityProfile
    status: FitStatus
    footprint_m: float
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        ensure_positive(self.footprint_m, name="footprint_m")
        object.__setattr__(self, "reasons", tuple(self.reasons))
        object.__setattr__(self, "warnings", tuple(self.warnings))


@dataclass(frozen=True, slots=True)
class AdvisorResult:
    """The shortlist and the constraints that blocked other profiles."""

    candidates: tuple[AdvisorCandidate, ...] = field(default_factory=tuple)
    blockers: tuple[AdvisorBlocker, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidates", tuple(self.candidates))
        object.__setattr__(self, "blockers", tuple(self.blockers))


def recommend(
    request: AdvisorRequest,
    profiles: tuple[SuitabilityProfile, ...] = SUITABILITY_PROFILES,
) -> AdvisorResult:
    """Return up to ``MAX_CANDIDATES`` profiles ordered by fit.

    Hard constraints exclude a profile and increment a blocker counter. Soft
    preferences only add warnings and change the order.
    """

    lowest_hz = min(
        band.center_hz
        for band_id in request.bands
        if (band := amateur_band_by_id(band_id)) is not None
    )
    blockers: dict[AdvisorBlocker, int] = {}
    ranked: list[tuple[tuple[object, ...], AdvisorCandidate]] = []

    requires_multiband = request.multiband_required and len(request.bands) > 1
    for profile in profiles:
        covered = request.bands & profile.bands
        if requires_multiband:
            if not profile.multiband or covered != request.bands:
                blockers[AdvisorBlocker.BANDS] = blockers.get(AdvisorBlocker.BANDS, 0) + 1
                continue
        elif not covered:
            blockers[AdvisorBlocker.BANDS] = blockers.get(AdvisorBlocker.BANDS, 0) + 1
            continue

        footprint = profile.footprint_at(lowest_hz)
        if request.available_width_m is not None and footprint > request.available_width_m:
            blockers[AdvisorBlocker.SPACE] = blockers.get(AdvisorBlocker.SPACE, 0) + 1
            continue
        if (
            request.available_height_m is not None
            and profile.min_height_m > request.available_height_m
        ):
            blockers[AdvisorBlocker.HEIGHT] = blockers.get(AdvisorBlocker.HEIGHT, 0) + 1
            continue
        if request.portable and not profile.portable:
            blockers[AdvisorBlocker.PORTABLE] = blockers.get(AdvisorBlocker.PORTABLE, 0) + 1
            continue
        if not request.tuner_available and profile.tuner is TunerRequirement.REQUIRED:
            blockers[AdvisorBlocker.TUNER] = blockers.get(AdvisorBlocker.TUNER, 0) + 1
            continue
        if profile.complexity.rank > request.max_complexity.rank:
            blockers[AdvisorBlocker.COMPLEXITY] = blockers.get(AdvisorBlocker.COMPLEXITY, 0) + 1
            continue
        if request.directionality is Directionality.OMNI and profile.directional:
            blockers[AdvisorBlocker.PATTERN] = blockers.get(AdvisorBlocker.PATTERN, 0) + 1
            continue
        if request.directionality is Directionality.DIRECTIONAL and not profile.directional:
            blockers[AdvisorBlocker.PATTERN] = blockers.get(AdvisorBlocker.PATTERN, 0) + 1
            continue

        reasons: list[str] = [
            "covers_requested_bands" if requires_multiband else "covers_a_requested_band"
        ]
        if request.available_width_m is not None:
            reasons.append("fits_available_space")
        if request.available_height_m is not None:
            reasons.append("fits_available_height")
        if request.portable:
            reasons.append("portable_supported")
        if profile.tuner is TunerRequirement.NONE:
            reasons.append("no_tuner_required")
        elif profile.tuner is TunerRequirement.OPTIONAL:
            reasons.append("tuner_optional")
        else:
            reasons.append("tuner_required")

        warnings: list[str] = []
        if (
            request.available_height_m is not None
            and profile.recommended_height_m > request.available_height_m
        ):
            warnings.append("height_below_recommended")
        if profile.tuner is TunerRequirement.REQUIRED:
            warnings.append("needs_tuner")
        if request.intent not in profile.intents:
            warnings.append("intent_mismatch")
        if request.available_width_m is not None and footprint > request.available_width_m * 0.9:
            warnings.append("space_tight")
        if profile.evidence_level == "C":
            warnings.append("experimental_starting_point")

        status = (
            FitStatus.EXCELLENT
            if not warnings
            else FitStatus.GOOD
            if len(warnings) == 1
            else FitStatus.CONDITIONAL
        )
        candidate = AdvisorCandidate(
            profile=profile,
            status=status,
            footprint_m=footprint,
            reasons=tuple(reasons),
            warnings=tuple(warnings),
        )
        intent_rank = 0 if request.intent in profile.intents else 1
        tuner_rank = {
            TunerRequirement.NONE: 0,
            TunerRequirement.OPTIONAL: 1,
            TunerRequirement.REQUIRED: 2,
        }[profile.tuner]
        ranked.append(
            (
                (
                    status.rank,
                    intent_rank,
                    tuner_rank,
                    profile.complexity.rank,
                    footprint,
                    profile.catalog_key,
                ),
                candidate,
            )
        )

    ranked.sort(key=lambda item: item[0])
    ordered_blockers = tuple(
        blocker
        for blocker, _count in sorted(
            blockers.items(),
            key=lambda item: (-item[1], item[0].value),
        )
    )
    return AdvisorResult(
        candidates=tuple(candidate for _key, candidate in ranked[:MAX_CANDIDATES]),
        blockers=ordered_blockers,
    )
