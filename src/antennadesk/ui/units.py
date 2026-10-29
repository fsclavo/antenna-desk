# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Presentation-unit conversions for the GUI."""

from __future__ import annotations

from enum import StrEnum

from ..domain.common import units


class UnitSystem(StrEnum):
    METRIC = "metric"
    IMPERIAL = "imperial"


def length_from_m(value_m: float, system: UnitSystem) -> float:
    if system is UnitSystem.METRIC:
        return value_m
    return units.ft_from_m(value_m)


def length_to_m(value: float, system: UnitSystem) -> float:
    if system is UnitSystem.METRIC:
        return value
    return units.m_from_ft(value)


def length_unit_key(system: UnitSystem) -> str:
    return "unit.m" if system is UnitSystem.METRIC else "unit.ft"


def diameter_from_m(value_m: float, system: UnitSystem) -> float:
    if system is UnitSystem.METRIC:
        return units.mm_from_m(value_m)
    return units.in_from_m(value_m)


def diameter_to_m(value: float, system: UnitSystem) -> float:
    if system is UnitSystem.METRIC:
        return units.m_from_mm(value)
    return units.m_from_in(value)


def diameter_unit_key(system: UnitSystem) -> str:
    return "unit.mm" if system is UnitSystem.METRIC else "unit.in"


def length_bounds(system: UnitSystem) -> tuple[float, float]:
    if system is UnitSystem.METRIC:
        return 0.1, 10_000.0
    return 0.3, 32_808.0


def height_bounds(system: UnitSystem) -> tuple[float, float]:
    if system is UnitSystem.METRIC:
        return 0.0, 10_000.0
    return 0.0, 32_808.0


def diameter_bounds(system: UnitSystem) -> tuple[float, float]:
    if system is UnitSystem.METRIC:
        return 0.01, 1_000.0
    return 0.001, 40.0
