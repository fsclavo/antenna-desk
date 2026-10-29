# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Lumped series loads on antenna wires."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_non_negative


@dataclass(frozen=True, slots=True)
class SeriesLoad:
    """A series RLC load inserted at a position along a wire."""

    id: str
    wire_id: str
    offset_m: float
    resistance_ohm: float = 0.0
    inductance_h: float = 0.0
    capacitance_f: float = 0.0

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("load id must not be empty")
        if not self.wire_id.strip():
            raise ValueError("load wire_id must not be empty")
        ensure_non_negative(self.offset_m, name="load offset_m")
        ensure_non_negative(self.resistance_ohm, name="load resistance_ohm")
        ensure_non_negative(self.inductance_h, name="load inductance_h")
        ensure_non_negative(self.capacitance_f, name="load capacitance_f")
        if self.resistance_ohm == 0.0 and self.inductance_h == 0.0 and self.capacitance_f == 0.0:
            raise ValueError("load must have a non-zero R, L, or C")
