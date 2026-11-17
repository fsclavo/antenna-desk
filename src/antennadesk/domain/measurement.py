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

MAX_MEASUREMENT_SESSION_NAME_LENGTH = 200
MAX_MEASUREMENT_SESSION_TEXT_LENGTH = 4_000


def reflection_coefficient(impedance_ohm: complex, reference_impedance_ohm: float) -> complex:
    """Return the voltage reflection coefficient for an impedance."""

    ensure_positive(reference_impedance_ohm, name="reference_impedance_ohm")
    if not math.isfinite(impedance_ohm.real) or not math.isfinite(impedance_ohm.imag):
        raise ValueError("impedance must be finite")
    denominator = impedance_ohm + reference_impedance_ohm
    if denominator == 0:
        raise ValueError("impedance plus reference impedance must be nonzero")
    return (impedance_ohm - reference_impedance_ohm) / denominator


def impedance_from_reflection(
    reflection: complex,
    reference_impedance_ohm: float,
) -> complex:
    """Return the impedance for a passive voltage reflection coefficient."""

    ensure_positive(reference_impedance_ohm, name="reference_impedance_ohm")
    if not math.isfinite(reflection.real) or not math.isfinite(reflection.imag):
        raise ValueError("reflection coefficient must be finite")
    if abs(reflection) >= 1.0:
        raise ValueError("reflection coefficient magnitude must be less than 1")
    return reference_impedance_ohm * (1.0 + reflection) / (1.0 - reflection)


def swr_for_impedance(impedance_ohm: complex, reference_impedance_ohm: float) -> float:
    """Return the SWR for an impedance at a reference impedance."""

    magnitude = abs(reflection_coefficient(impedance_ohm, reference_impedance_ohm))
    if magnitude >= 1.0:
        return math.inf
    return (1.0 + magnitude) / (1.0 - magnitude)


@dataclass(frozen=True, slots=True)
class MeasurementPoint:
    frequency_hz: float
    impedance_ohm: complex

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        if not math.isfinite(self.impedance_ohm.real) or not math.isfinite(self.impedance_ohm.imag):
            raise ValueError("measurement impedance must be finite")

    def swr(self, reference_impedance_ohm: float) -> float:
        return swr_for_impedance(self.impedance_ohm, reference_impedance_ohm)


@dataclass(frozen=True, slots=True)
class MeasurementSession:
    """A field session that groups measurements taken under one setup."""

    id: UUID
    name: str
    created_at: datetime
    design_id: UUID | None = None
    location: str = ""
    conditions: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        name = self.name.strip()
        if not name:
            raise ValueError("measurement session name must not be empty")
        if len(name) > MAX_MEASUREMENT_SESSION_NAME_LENGTH:
            raise ValueError(
                "measurement session name must be at most "
                f"{MAX_MEASUREMENT_SESSION_NAME_LENGTH} characters"
            )
        ensure_utc(self.created_at, name="measurement session created_at")
        for field_name in ("location", "conditions", "notes"):
            value = getattr(self, field_name)
            if len(value) > MAX_MEASUREMENT_SESSION_TEXT_LENGTH:
                raise ValueError(
                    f"measurement session {field_name} must be at most "
                    f"{MAX_MEASUREMENT_SESSION_TEXT_LENGTH} characters"
                )
        object.__setattr__(self, "name", name)


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
    session_id: UUID | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("measurement name must not be empty")
        ensure_utc(self.created_at, name="created_at")
        ensure_positive(self.reference_impedance_ohm, name="reference_impedance_ohm")
        points = tuple(sorted(self.points, key=lambda point: point.frequency_hz))
        if not points:
            raise ValueError("measurement must contain at least one point")
        object.__setattr__(self, "points", points)
