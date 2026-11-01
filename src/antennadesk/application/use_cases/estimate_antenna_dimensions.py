# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Estimate initial antenna dimensions from a frequency-first intent."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.design.estimate import DimensionEstimate
from ...domain.design.estimators import estimate_intent
from ...domain.design.intent import DesignIntent


@dataclass(frozen=True, slots=True)
class EstimateAntennaDimensions:
    def execute(self, intent: DesignIntent) -> DimensionEstimate:
        return estimate_intent(intent)
