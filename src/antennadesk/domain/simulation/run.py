# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persisted simulation snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ..common.time import ensure_utc
from .result import SimulationResult


@dataclass(frozen=True, slots=True)
class SimulationRun:
    id: UUID
    design_id: UUID
    created_at: datetime
    result: SimulationResult
    band_id: str | None = None
    batch_id: UUID | None = None

    def __post_init__(self) -> None:
        ensure_utc(self.created_at, name="simulation run created_at")
        if self.band_id is not None and not self.band_id.strip():
            raise ValueError("band_id must not be empty")
        if self.band_id is None and self.batch_id is not None:
            raise ValueError("a band analysis run requires a band_id")
        if self.band_id is not None and self.batch_id is None:
            raise ValueError("a band run requires a batch_id")
