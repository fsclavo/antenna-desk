# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Simulation specification."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..antennas.feed_line import FeedLine
from ..antennas.matching_network import MatchingNetwork
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
    pattern_frequencies_hz: tuple[float, ...] = ()
    feed_line: FeedLine | None = None
    matching_network: MatchingNetwork | None = None
    feed_transformer_ratio: float = 1.0
    timeout_s: float = 60.0

    def __post_init__(self) -> None:
        ensure_positive(self.reference_impedance_ohm, name="reference_impedance_ohm")
        ensure_positive(self.feed_transformer_ratio, name="feed_transformer_ratio")
        ensure_positive(self.timeout_s, name="timeout_s")
        if self.timeout_s > MAX_TIMEOUT_S:
            raise ValueError(f"timeout_s must not exceed {MAX_TIMEOUT_S}")
        object.__setattr__(
            self,
            "pattern_frequencies_hz",
            self._snapped_pattern_frequencies(),
        )

    def _snapped_pattern_frequencies(self) -> tuple[float, ...]:
        requested = tuple(float(value) for value in self.pattern_frequencies_hz)
        if not requested:
            return ()
        plan = self.frequency_plan
        snapped: set[float] = set()
        for frequency_hz in requested:
            ensure_positive(frequency_hz, name="pattern frequency")
            if plan.count == 1:
                if abs(frequency_hz - plan.start_hz) > 1e-6:
                    raise ValueError("pattern frequency must match the single-frequency plan")
                snapped.add(plan.start_hz)
                continue
            index = round((frequency_hz - plan.start_hz) / plan.step_hz)
            if index < 0 or index >= plan.count:
                raise ValueError("pattern frequency is outside the frequency plan")
            snapped.add(plan.start_hz + index * plan.step_hz)
        return tuple(sorted(snapped))
