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

    def __post_init__(self) -> None:
        ensure_utc(self.created_at, name="simulation run created_at")
