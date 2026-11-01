# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Result objects for frequency-first dimension estimation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ..antennas.design import AntennaDesignParameters


class Confidence(StrEnum):
    PHYSICAL = "physical"
    EMPIRICAL = "empirical"
    REFERENCE_SCALED = "reference_scaled"
    HEURISTIC = "heuristic"


class DimensionUnit(StrEnum):
    LENGTH = "length"
    ANGLE = "angle"
    COUNT = "count"


@dataclass(frozen=True, slots=True)
class DimensionRow:
    label_key: str
    value: float
    unit: DimensionUnit = DimensionUnit.LENGTH


@dataclass(frozen=True, slots=True)
class DimensionEstimate:
    parameters: AntennaDesignParameters
    method_id: str
    confidence: Confidence
    assumptions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    tolerance_m: float = 0.0
    source_ids: tuple[str, ...] = ()
    rows: tuple[DimensionRow, ...] = field(default_factory=tuple)
