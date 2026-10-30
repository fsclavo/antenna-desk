# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Imported antenna measurements."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .common.time import ensure_utc
from .common.units import ensure_positive


@dataclass(frozen=True, slots=True)
class MeasurementPoint:
    frequency_hz: float
    impedance_ohm: complex

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        if not math.isfinite(self.impedance_ohm.real) or not math.isfinite(self.impedance_ohm.imag):
            raise ValueError("measurement impedance must be finite")

    def swr(self, reference_impedance_ohm: float) -> float:
        reflection = (self.impedance_ohm - reference_impedance_ohm) / (
            self.impedance_ohm + reference_impedance_ohm
        )
        magnitude = abs(reflection)
        if magnitude >= 1.0:
            return math.inf
        return (1.0 + magnitude) / (1.0 - magnitude)


@dataclass(frozen=True, slots=True)
class Measurement:
    id: UUID
    name: str
    created_at: datetime
    reference_impedance_ohm: float
    points: tuple[MeasurementPoint, ...]
    source: str = ""
    calibration: str = ""
    reference_plane: str = ""
    feed_line: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("measurement name must not be empty")
        ensure_utc(self.created_at, name="created_at")
        ensure_positive(self.reference_impedance_ohm, name="reference_impedance_ohm")
        points = tuple(sorted(self.points, key=lambda point: point.frequency_hz))
        if not points:
            raise ValueError("measurement must contain at least one point")
        object.__setattr__(self, "points", points)
