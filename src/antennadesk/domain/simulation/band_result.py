# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Per-band simulation results and batch grouping."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ..common.time import ensure_utc
from .bands import AmateurBand, amateur_band_by_id
from .result import SimulationResult, SimulationStatus


@dataclass(frozen=True, slots=True)
class BandResult:
    """One band's normalized simulation result."""

    band: AmateurBand
    result: SimulationResult

    def __post_init__(self) -> None:
        if not self.band.name.strip():
            raise ValueError("band name must not be empty")


@dataclass(frozen=True, slots=True)
class BandAnalysisResult:
    """An immutable batch of band results produced by one analysis action."""

    design_id: UUID
    batch_id: UUID
    created_at: datetime
    bands: tuple[BandResult, ...]

    def __post_init__(self) -> None:
        ensure_utc(self.created_at, name="band analysis created_at")
        bands = tuple(self.bands)
        object.__setattr__(self, "bands", bands)
        ids = [band.band.name for band in bands]
        if len(ids) != len(set(ids)):
            raise ValueError("a band analysis must not contain duplicate bands")

    @property
    def status(self) -> SimulationStatus:
        if not self.bands:
            return SimulationStatus.ERROR
        statuses = [band.result.status for band in self.bands]
        completed = sum(status is SimulationStatus.COMPLETED for status in statuses)
        if completed == len(statuses):
            return SimulationStatus.COMPLETED
        if completed:
            return SimulationStatus.PARTIAL
        if any(status is SimulationStatus.CANCELLED for status in statuses):
            return SimulationStatus.CANCELLED
        return SimulationStatus.ERROR

    def result_for_band(self, band_id: str) -> BandResult | None:
        for band in self.bands:
            if band.band.name == band_id:
                return band
        return None

    @classmethod
    def from_runs(
        cls,
        *,
        design_id: UUID,
        batch_id: UUID,
        created_at: datetime,
        runs: tuple[tuple[str, SimulationResult], ...],
    ) -> BandAnalysisResult:
        bands: list[BandResult] = []
        for band_id, result in runs:
            band = amateur_band_by_id(band_id)
            if band is not None:
                bands.append(BandResult(band=band, result=result))
        return cls(
            design_id=design_id,
            batch_id=batch_id,
            created_at=created_at,
            bands=tuple(bands),
        )
