# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Simulation specification."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.units import ensure_positive
from .far_field import FarFieldRequest
from .frequency import FrequencyPlan
from .segmentation import SegmentationPolicy

MAX_TIMEOUT_S = 3_600.0


@dataclass(frozen=True, slots=True)
class SimulationSpec:
    """Immutable simulation configuration for a model snapshot."""

    frequency_plan: FrequencyPlan
    segmentation: SegmentationPolicy = field(default_factory=SegmentationPolicy)
    reference_impedance_ohm: float = 50.0
    extended_thin_wire_kernel: bool = False
    include_conductor_losses: bool = True
    far_field: FarFieldRequest = field(default_factory=FarFieldRequest)
    timeout_s: float = 60.0

    def __post_init__(self) -> None:
        ensure_positive(self.reference_impedance_ohm, name="reference_impedance_ohm")
        ensure_positive(self.timeout_s, name="timeout_s")
        if self.timeout_s > MAX_TIMEOUT_S:
            raise ValueError(f"timeout_s must not exceed {MAX_TIMEOUT_S}")
