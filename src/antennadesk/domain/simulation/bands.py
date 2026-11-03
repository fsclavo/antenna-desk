# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Amateur-band helpers for far-field pattern snapshots."""

from __future__ import annotations

from dataclasses import dataclass

from .frequency import FrequencyPlan

DEFAULT_PATTERN_SNAPSHOT_MAX = 12
DEFAULT_PATTERN_SNAPSHOT_MIN = 5


@dataclass(frozen=True, slots=True)
class AmateurBand:
    name: str
    start_hz: float
    stop_hz: float

    @property
    def center_hz(self) -> float:
        return (self.start_hz + self.stop_hz) / 2.0


# Widely used HF amateur band ranges. Regional band plans differ at the edges;
# the snapshot only needs a representative frequency inside each band.
AMATEUR_BANDS: tuple[AmateurBand, ...] = (
    AmateurBand("160m", 1_800_000.0, 2_000_000.0),
    AmateurBand("80m", 3_500_000.0, 4_000_000.0),
    AmateurBand("60m", 5_351_500.0, 5_366_500.0),
    AmateurBand("40m", 7_000_000.0, 7_300_000.0),
    AmateurBand("30m", 10_100_000.0, 10_150_000.0),
    AmateurBand("20m", 14_000_000.0, 14_350_000.0),
    AmateurBand("17m", 18_068_000.0, 18_168_000.0),
    AmateurBand("15m", 21_000_000.0, 21_450_000.0),
    AmateurBand("12m", 24_890_000.0, 24_990_000.0),
    AmateurBand("10m", 28_000_000.0, 29_700_000.0),
    AmateurBand("6m", 50_000_000.0, 54_000_000.0),
)


def amateur_band_for(
    frequency_hz: float,
    *,
    tolerance_fraction: float = 0.01,
) -> AmateurBand | None:
    """Return the amateur band containing or nearest to ``frequency_hz``.

    A small relative tolerance keeps coarse sweep grids useful for labels: a
    snapshot chosen from a 100 kHz grid may fall just outside a narrow band
    such as 30 m. The tolerance is for display only; the snapshot selection
    still uses the exact band ranges.
    """

    for band in AMATEUR_BANDS:
        tolerance_hz = band.center_hz * tolerance_fraction
        if band.start_hz - tolerance_hz <= frequency_hz <= band.stop_hz + tolerance_hz:
            return band
    return None


def band_snapshot_frequencies(
    plan: FrequencyPlan,
    *,
    preferred_frequency_hz: float | None = None,
    min_count: int = DEFAULT_PATTERN_SNAPSHOT_MIN,
    max_count: int = DEFAULT_PATTERN_SNAPSHOT_MAX,
) -> tuple[float, ...]:
    """Return one pattern snapshot per amateur band inside the plan.

    The preferred frequency is used when it falls inside a band; otherwise the
    band center clipped to the plan is used. Narrow plans that touch fewer than
    ``min_count`` bands are filled with evenly spaced plan frequencies so a
    single-band sweep still gets a useful set of pattern cuts.
    """

    if min_count < 1:
        raise ValueError("min_count must be at least 1")
    if max_count < min_count:
        raise ValueError("max_count must be at least min_count")
    selected: set[float] = set()
    for band in AMATEUR_BANDS:
        if band.stop_hz < plan.start_hz or band.start_hz > plan.stop_hz:
            continue
        if (
            preferred_frequency_hz is not None
            and band.start_hz <= preferred_frequency_hz <= band.stop_hz
        ):
            target_hz = preferred_frequency_hz
        else:
            target_hz = (max(band.start_hz, plan.start_hz) + min(band.stop_hz, plan.stop_hz)) / 2.0
        selected.add(plan.nearest_frequency(target_hz))
    if len(selected) < min_count:
        for frequency_hz in plan.snapshot_frequencies(
            min_count,
            preferred_frequency_hz=preferred_frequency_hz,
        ):
            selected.add(frequency_hz)
    if len(selected) > max_count:
        ordered = sorted(selected)
        indices = {
            round(index * (len(ordered) - 1) / (max_count - 1)) for index in range(max_count)
        }
        selected = {ordered[index] for index in indices}
    return tuple(sorted(selected))
