# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Lumped series loads on antenna wires."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..common.units import ensure_non_negative


class LoadKind(StrEnum):
    SERIES = "series"
    PARALLEL = "parallel"


def _validate_load_values(
    *,
    load_id: str,
    wire_id: str,
    offset_m: float,
    resistance_ohm: float,
    inductance_h: float,
    capacitance_f: float,
) -> None:
    if not load_id.strip():
        raise ValueError("load id must not be empty")
    if not wire_id.strip():
        raise ValueError("load wire_id must not be empty")
    ensure_non_negative(offset_m, name="load offset_m")
    ensure_non_negative(resistance_ohm, name="load resistance_ohm")
    ensure_non_negative(inductance_h, name="load inductance_h")
    ensure_non_negative(capacitance_f, name="load capacitance_f")
    if resistance_ohm == 0.0 and inductance_h == 0.0 and capacitance_f == 0.0:
        raise ValueError("load must have a non-zero R, L, or C")


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
        _validate_load_values(
            load_id=self.id,
            wire_id=self.wire_id,
            offset_m=self.offset_m,
            resistance_ohm=self.resistance_ohm,
            inductance_h=self.inductance_h,
            capacitance_f=self.capacitance_f,
        )


@dataclass(frozen=True, slots=True)
class ParallelLoad:
    """A parallel RLC load inserted at a position along a wire."""

    id: str
    wire_id: str
    offset_m: float
    resistance_ohm: float = 0.0
    inductance_h: float = 0.0
    capacitance_f: float = 0.0

    def __post_init__(self) -> None:
        _validate_load_values(
            load_id=self.id,
            wire_id=self.wire_id,
            offset_m=self.offset_m,
            resistance_ohm=self.resistance_ohm,
            inductance_h=self.inductance_h,
            capacitance_f=self.capacitance_f,
        )


LumpedLoad = SeriesLoad | ParallelLoad
