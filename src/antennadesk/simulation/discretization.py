# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Segment layout and segmentation diagnostics."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.wire import Wire
from ..domain.common import units
from ..domain.common.validation import Diagnostic, Severity
from ..domain.simulation.spec import SimulationSpec


@dataclass(frozen=True, slots=True)
class WireSegmentation:
    wire: Wire
    tag: int
    segments: int
    first_segment: int
    last_segment: int
    segment_length_m: float


@dataclass(frozen=True, slots=True)
class SegmentLayout:
    wires: tuple[WireSegmentation, ...]
    feed_tag: int
    feed_segment: int
    feed_wire_id: str
    feed_offset_m: float

    @property
    def feed_local_segment(self) -> int:
        segmentation = self.wire_segmentation(self.feed_wire_id)
        return self.feed_segment - segmentation.first_segment + 1

    def wire_segmentation(self, wire_id: str) -> WireSegmentation:
        for segmentation in self.wires:
            if segmentation.wire.id == wire_id:
                return segmentation
        raise KeyError(f"unknown wire id: {wire_id}")


def build_segment_layout(model: AntennaModel, spec: SimulationSpec) -> SegmentLayout:
    """Assign tags and global segment numbers, and locate the feed segment.

    The segmentation policy is evaluated at the highest frequency in the plan,
    where the wavelength is shortest and the segment count is largest.
    """

    frequency_hz = spec.frequency_plan.stop_hz
    segmentations: list[WireSegmentation] = []
    first_segment = 1

    for index, wire in enumerate(model.wires):
        segments = spec.segmentation.segments_for(wire, frequency_hz)
        segmentations.append(
            WireSegmentation(
                wire=wire,
                tag=index + 1,
                segments=segments,
                first_segment=first_segment,
                last_segment=first_segment + segments - 1,
                segment_length_m=wire.length_m / segments,
            )
        )
        first_segment += segments

    feed_segmentation = next(
        (
            segmentation
            for segmentation in segmentations
            if segmentation.wire.id == model.feed.wire_id
        ),
        None,
    )
    if feed_segmentation is None:
        raise ValueError(f"feed references an unknown wire: {model.feed.wire_id}")

    index = math.floor(model.feed.offset_m / feed_segmentation.segment_length_m)
    if index >= feed_segmentation.segments or math.isclose(
        model.feed.offset_m,
        feed_segmentation.wire.length_m,
        rel_tol=1e-9,
        abs_tol=1e-9,
    ):
        index = feed_segmentation.segments - 1
    index = max(0, min(index, feed_segmentation.segments - 1))

    return SegmentLayout(
        wires=tuple(segmentations),
        feed_tag=feed_segmentation.tag,
        feed_segment=feed_segmentation.first_segment + index,
        feed_wire_id=feed_segmentation.wire.id,
        feed_offset_m=model.feed.offset_m,
    )


def validate_segmentation(
    model: AntennaModel,
    spec: SimulationSpec,
) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    layout = build_segment_layout(model, spec)
    wavelength = units.wavelength_m(spec.frequency_plan.stop_hz)

    for segmentation in layout.wires:
        wire = segmentation.wire
        segment_length = segmentation.segment_length_m

        if segmentation.segments < 3:
            diagnostics.append(
                Diagnostic(
                    code="segmentation.few_segments",
                    severity=Severity.WARNING,
                    message=(
                        f"wire {wire.id} uses only {segmentation.segments} segment(s); "
                        "the current distribution may be inaccurate"
                    ),
                    field="segmentation",
                )
            )

        if segment_length > wavelength / 10.0:
            diagnostics.append(
                Diagnostic(
                    code="segmentation.segment_too_long",
                    severity=Severity.WARNING,
                    message=(
                        f"wire {wire.id} has segments longer than lambda/10; "
                        "NEC accuracy may degrade"
                    ),
                    field="segmentation",
                )
            )

        if not spec.extended_thin_wire_kernel and segment_length < 2.0 * wire.radius_m:
            diagnostics.append(
                Diagnostic(
                    code="segmentation.segment_too_thin",
                    severity=Severity.WARNING,
                    message=(
                        f"wire {wire.id} has segments shorter than twice its radius; "
                        "the thin-wire approximation may be invalid"
                    ),
                    field="segmentation",
                )
            )

        index = layout.feed_segment - segmentation.first_segment
        if 0 <= index < segmentation.segments:
            center = (index + 0.5) * segment_length
            if abs(model.feed.offset_m - center) > 0.05 * segment_length:
                diagnostics.append(
                    Diagnostic(
                        code="segmentation.feed_offset",
                        severity=Severity.WARNING,
                        message=(
                            "the feed point is not at the center of its segment; "
                            "the delta-gap source is an approximation"
                        ),
                        field="feed.offset_m",
                    )
                )

    return tuple(diagnostics)
