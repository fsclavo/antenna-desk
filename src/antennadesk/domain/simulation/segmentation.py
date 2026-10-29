# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Segmentation policy for straight-wire models."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from ..antennas.antenna import AntennaModel
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
    wire_segments: tuple[tuple[str, int], ...] = ()

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
        seen: set[str] = set()
        for wire_id, segments in self.wire_segments:
            if not wire_id:
                raise ValueError("wire segment override id must not be empty")
            if wire_id in seen:
                raise ValueError(f"duplicate wire segment override: {wire_id}")
            seen.add(wire_id)
            if segments < self.min_segments_per_wire:
                raise ValueError("wire segment override is below min_segments_per_wire")
            if segments > self.max_segments_per_wire:
                raise ValueError("wire segment override exceeds max_segments_per_wire")

    def segments_for(self, wire: Wire, frequency_hz: float) -> int:
        for wire_id, segments in self.wire_segments:
            if wire_id == wire.id:
                return segments
        if self.segments_per_wire is not None:
            return self.segments_per_wire

        wavelength = units.wavelength_m(frequency_hz)
        target_length = wavelength * self.target_segment_length_wavelengths
        requested = math.ceil(wire.length_m / target_length)
        return min(
            max(requested, self.min_segments_per_wire),
            self.max_segments_per_wire,
        )


def _aligned_feed_count(
    wire: Wire,
    feed_offset_m: float,
    target: int,
    policy: SegmentationPolicy,
) -> int:
    candidates = range(
        max(policy.min_segments_per_wire, target - 2),
        min(policy.max_segments_per_wire, target + 2) + 1,
    )

    def distance(count: int) -> float:
        segment_length = wire.length_m / count
        index = min(int(feed_offset_m / segment_length), count - 1)
        center = (index + 0.5) * segment_length
        return abs(feed_offset_m - center)

    return min(candidates, key=lambda count: (distance(count), abs(count - target)))


def aligned_policy_for_model(
    model: AntennaModel,
    frequency_hz: float,
    base: SegmentationPolicy | None = None,
) -> SegmentationPolicy:
    """Return a policy with explicit counts and a feed-aligned feed wire.

    The heuristic target still drives non-feed wires.  On the feed wire, a
    nearby count is chosen so the feed offset falls closest to a segment
    center, reducing the delta-gap placement warning.
    """

    policy = base if base is not None else SegmentationPolicy()
    overrides: list[tuple[str, int]] = []
    for wire in model.wires:
        target = policy.segments_for(wire, frequency_hz)
        if wire.id == model.feed.wire_id:
            target = _aligned_feed_count(wire, model.feed.offset_m, target, policy)
        overrides.append((wire.id, target))
    return replace(policy, segments_per_wire=None, wire_segments=tuple(overrides))
