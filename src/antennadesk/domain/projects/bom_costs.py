# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Manual BOM unit costs stored with a project."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_non_negative

MAX_BOM_COST_LINES = 200
MAX_BOM_CURRENCY_LENGTH = 12


@dataclass(frozen=True, slots=True)
class BomCostLine:
    """One manual unit cost keyed by a stable BOM row identifier."""

    key: str
    unit_cost: float

    def __post_init__(self) -> None:
        key = self.key.strip()
        if not key:
            raise ValueError("BOM cost key must not be empty")
        ensure_non_negative(self.unit_cost, name="unit_cost")
        object.__setattr__(self, "key", key)


@dataclass(frozen=True, slots=True)
class BomCostRecord:
    """Project-level manual BOM costs.

    The record does not fetch prices, convert currencies, or change the
    electrical model.  ``currency`` is a free-form label shown with the
    computed totals.
    """

    currency: str = ""
    lines: tuple[BomCostLine, ...] = ()

    def __post_init__(self) -> None:
        currency = self.currency.strip()
        if len(currency) > MAX_BOM_CURRENCY_LENGTH:
            raise ValueError(f"BOM currency must be at most {MAX_BOM_CURRENCY_LENGTH} characters")
        lines = tuple(self.lines)
        if len(lines) > MAX_BOM_COST_LINES:
            raise ValueError(f"at most {MAX_BOM_COST_LINES} BOM cost lines are supported")
        keys = [line.key for line in lines]
        if len(keys) != len(set(keys)):
            raise ValueError("BOM cost keys must be unique")
        object.__setattr__(self, "currency", currency)
        object.__setattr__(self, "lines", lines)

    @property
    def is_empty(self) -> bool:
        return not self.currency and not self.lines

    def cost_for(self, key: str) -> float | None:
        """Return the manual unit cost for ``key``, or ``None``."""

        for line in self.lines:
            if line.key == key:
                return line.unit_cost
        return None
