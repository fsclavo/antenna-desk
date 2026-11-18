# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared length presentation policy for the UI and human-readable reports."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from ..domain.common import units

LengthUnit = Literal["mm", "cm", "m", "in", "ft"]


class UnitSystem(StrEnum):
    METRIC = "metric"
    IMPERIAL = "imperial"


class LengthPolicy(StrEnum):
    AUTO = "auto"
    FIXED = "fixed"


@dataclass(frozen=True, slots=True)
class DisplayUnits:
    """Explicit length presentation policy.

    The formatter is Qt-free so the UI and human-readable reports can share the
    same rules. Domain and project values remain canonical meters.
    """

    system: UnitSystem = UnitSystem.METRIC
    length_policy: LengthPolicy = LengthPolicy.AUTO

    def unit_for(
        self,
        value_m: float,
        *,
        scale_hint: LengthUnit | None = None,
    ) -> LengthUnit:
        magnitude = abs(value_m)
        hint = self._valid_hint(scale_hint)
        if self.system is UnitSystem.METRIC:
            if self.length_policy is LengthPolicy.FIXED:
                return "m"
            if magnitude == 0.0:
                return hint or "m"
            if magnitude < 0.01:
                return "mm"
            if magnitude < 1.0:
                return "cm"
            return "m"
        if self.length_policy is LengthPolicy.FIXED:
            return "ft"
        if magnitude == 0.0:
            return hint or "ft"
        if magnitude < units.m_from_ft(1.0):
            return "in"
        return "ft"

    @staticmethod
    def decimals_for(unit: LengthUnit) -> int:
        if unit in {"mm", "cm", "in"}:
            return 2
        return 3

    @staticmethod
    def meters_per_unit(unit: LengthUnit) -> float:
        if unit == "mm":
            return 0.001
        if unit == "cm":
            return 0.01
        if unit == "m":
            return 1.0
        if unit == "in":
            return units.m_from_in(1.0)
        if unit == "ft":
            return units.m_from_ft(1.0)
        raise ValueError(f"unsupported length unit: {unit!r}")

    def format_number(
        self,
        value_m: float,
        *,
        unit: LengthUnit | None = None,
        scale_hint: LengthUnit | None = None,
        trim: bool = True,
    ) -> str:
        resolved = unit or self.unit_for(value_m, scale_hint=scale_hint)
        value = value_m / self.meters_per_unit(resolved)
        text = f"{value:.{self.decimals_for(resolved)}f}"
        if trim:
            text = text.rstrip("0").rstrip(".")
            if text in {"", "-0"}:
                text = "0"
        return text

    def format_length(
        self,
        value_m: float,
        *,
        unit: LengthUnit | None = None,
        scale_hint: LengthUnit | None = None,
        trim: bool = True,
    ) -> str:
        resolved = unit or self.unit_for(value_m, scale_hint=scale_hint)
        return f"{self.format_number(value_m, unit=resolved, trim=trim)} {resolved}"

    def table_unit(
        self,
        values_m: Iterable[float],
        *,
        scale_hint: LengthUnit | None = None,
    ) -> LengthUnit:
        if self.length_policy is LengthPolicy.FIXED:
            return "m" if self.system is UnitSystem.METRIC else "ft"
        largest = max((abs(value) for value in values_m), default=0.0)
        return self.unit_for(largest, scale_hint=scale_hint)

    def _valid_hint(self, hint: LengthUnit | None) -> LengthUnit | None:
        if hint is None:
            return None
        metric = {"mm", "cm", "m"}
        allowed = metric if self.system is UnitSystem.METRIC else {"in", "ft"}
        return hint if hint in allowed else None
