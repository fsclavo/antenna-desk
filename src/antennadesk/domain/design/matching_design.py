# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persisted design target for a project matching network."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_positive

MATCHING_DESIGN_ORIGIN_MANUAL = "manual"
MATCHING_DESIGN_ORIGIN_SIMULATION = "simulation"


@dataclass(frozen=True, slots=True)
class MatchingNetworkDesign:
    """Frequency, load, and source impedance used to design a network."""

    frequency_hz: float
    load_resistance_ohm: float
    load_reactance_ohm: float
    source_impedance_ohm: float = 50.0
    origin: str | None = None

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.load_resistance_ohm, name="load_resistance_ohm")
        ensure_positive(self.source_impedance_ohm, name="source_impedance_ohm")
        if not math.isfinite(self.load_reactance_ohm):
            raise ValueError("load_reactance_ohm must be finite")
        origin = self.origin.strip() if self.origin is not None else None
        if origin is not None and len(origin) > 64:
            raise ValueError("origin must not exceed 64 characters")
        object.__setattr__(self, "origin", origin or None)

    @property
    def load_impedance_ohm(self) -> complex:
        return complex(self.load_resistance_ohm, self.load_reactance_ohm)
