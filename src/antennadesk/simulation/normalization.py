# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Simulation-facing re-exports of the domain reflection helpers."""

from __future__ import annotations

from ..domain.common.reflection import (
    calculate_reflection_coefficient,
    calculate_swr,
)

__all__ = ["calculate_reflection_coefficient", "calculate_swr"]
