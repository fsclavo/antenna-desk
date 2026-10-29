"""Segmentation policy for straight-wire models."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..antennas.wire import Wire
from ..common import units
from ..common.units import ensure_positive

DEFAULT_TARGET_SEGMENT_LENGTH_WAVELENGTHS = 0.02
DEFAULT_MAX_SEGMENTS_PER_WIRE = 1_000


@dataclass(frozen=True, slots=True)
class SegmentationPolicy:
    """How physical wires are divided into solver segments.

    The default target is a heuristic, not a universal rule.  Callers can
    provide an explicit segment count when reproducing a reference case.
    """

    segments_per_wire: int | None = None
    target_segment_length_wavelengths: float = DEFAULT_TARGET_SEGMENT_LENGTH_WAVELENGTHS
    min_segments_per_wire: int = 1
    max_segments_per_wire: int = DEFAULT_MAX_SEGMENTS_PER_WIRE

    def __post_init__(self) -> None:
        ensure_positive(
            self.target_segment_length_wavelengths,
            name="target_segment_length_wavelengths",
        )
        if self.min_segments_per_wire < 1:
            raise ValueError("min_segments_per_wire must be at least 1")
        if self.max_segments_per_wire < self.min_segments_per_wire:
            raise ValueError(
                "max_segments_per_wire must be greater than or equal to min_segments_per_wire"
            )
        if self.segments_per_wire is not None:
            if self.segments_per_wire < self.min_segments_per_wire:
                raise ValueError("segments_per_wire is below min_segments_per_wire")
            if self.segments_per_wire > self.max_segments_per_wire:
                raise ValueError("segments_per_wire exceeds max_segments_per_wire")

    def segments_for(self, wire: Wire, frequency_hz: float) -> int:
        if self.segments_per_wire is not None:
            return self.segments_per_wire

        wavelength = units.wavelength_m(frequency_hz)
        target_length = wavelength * self.target_segment_length_wavelengths
        requested = math.ceil(wire.length_m / target_length)
        return min(
            max(requested, self.min_segments_per_wire),
            self.max_segments_per_wire,
        )
