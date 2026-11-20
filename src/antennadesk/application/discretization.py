# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Segment layout and segmentation diagnostics."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.wire import Wire
from ..domain.common import units
from ..domain.common.validation import Diagnostic, Severity
from ..domain.simulation.spec import SimulationSpec

THIN_WIRE_MIN_RADIUS_RATIO = 8.0
THIN_WIRE_HARD_MIN_RADIUS_RATIO = 2.0
MIN_SEGMENT_LENGTH_RELATIVE = 1e-3
MAX_SEGMENT_LENGTH_RELATIVE = 0.1
# Very short structural wires (feed gaps, loading-coil sections, return stubs)
# cannot satisfy the 1e-3 lambda segment rule with their fixed segment count.
# Their short-segment warning is expected; only longer wires are treated as a
# blocking over-segmentation failure.
MIN_WIRE_LENGTH_FOR_SEGMENT_QUALITY_RELATIVE = 0.01


@dataclass(frozen=True, slots=True)
class ModelQualityReport:
    """The spec after thin-wire quality adjustments and any blocking codes."""

    spec: SimulationSpec
    blocking_codes: tuple[str, ...] = ()
    adjusted_wire_ids: tuple[str, ...] = ()
    extended_kernel_enabled: bool = False


@dataclass(frozen=True, slots=True)
class WireSegmentation:
    wire: Wire
    tag: int
    segments: int
    first_segment: int
    last_segment: int
    segment_length_m: float


@dataclass(frozen=True, slots=True)
class FeedSegment:
    wire_id: str
    offset_m: float
    tag: int
    segment: int
    local_segment: int
    amplitude: float = 1.0
    phase_deg: float = 0.0


@dataclass(frozen=True, slots=True)
class SegmentLayout:
    wires: tuple[WireSegmentation, ...]
    feed_tag: int
    feed_segment: int
    feed_wire_id: str
    feed_offset_m: float
    feeds: tuple[FeedSegment, ...] = ()

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

    by_wire_id = {segmentation.wire.id: segmentation for segmentation in segmentations}

    def feed_segment_for(
        wire_id: str,
        offset_m: float,
        amplitude: float,
        phase_deg: float,
    ) -> FeedSegment:
        segmentation = by_wire_id.get(wire_id)
        if segmentation is None:
            raise ValueError(f"feed references an unknown wire: {wire_id}")
        index = math.floor(offset_m / segmentation.segment_length_m)
        if index >= segmentation.segments or math.isclose(
            offset_m,
            segmentation.wire.length_m,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            index = segmentation.segments - 1
        index = max(0, min(index, segmentation.segments - 1))
        return FeedSegment(
            wire_id=segmentation.wire.id,
            offset_m=offset_m,
            tag=segmentation.tag,
            segment=segmentation.first_segment + index,
            local_segment=index + 1,
            amplitude=amplitude,
            phase_deg=phase_deg,
        )

    feeds = tuple(
        feed_segment_for(
            source.wire_id,
            source.offset_m,
            source.amplitude,
            source.phase_deg,
        )
        for source in model.effective_sources
    )
    primary = feeds[0]

    return SegmentLayout(
        wires=tuple(segmentations),
        feed_tag=primary.tag,
        feed_segment=primary.segment,
        feed_wire_id=primary.wire_id,
        feed_offset_m=primary.offset_m,
        feeds=feeds,
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
        relative_length = segment_length / wavelength
        radius_ratio = segment_length / wire.radius_m

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

        if relative_length > 0.1:
            diagnostics.append(
                Diagnostic(
                    code="segmentation.segment_too_long",
                    severity=Severity.WARNING,
                    message=(
                        f"wire {wire.id} has segments of {relative_length:.3f} lambda; "
                        "NEC recommends at most 0.1 lambda"
                    ),
                    field="segmentation",
                )
            )

        if relative_length < 1e-3:
            diagnostics.append(
                Diagnostic(
                    code="segmentation.segment_too_short",
                    severity=Severity.WARNING,
                    message=(
                        f"wire {wire.id} has segments of {relative_length:.2e} lambda; "
                        "NEC recommends at least 1e-3 lambda"
                    ),
                    field="segmentation",
                )
            )

        if not spec.extended_thin_wire_kernel and 2.0 <= radius_ratio < 8.0:
            diagnostics.append(
                Diagnostic(
                    code="segmentation.radius_ratio_low",
                    severity=Severity.WARNING,
                    message=(
                        f"wire {wire.id} has a segment length to radius ratio of "
                        f"{radius_ratio:.1f}; the thin-wire kernel needs more than 8 "
                        "for 1% error"
                    ),
                    field="segmentation",
                )
            )

        if not spec.extended_thin_wire_kernel and radius_ratio < 2.0:
            diagnostics.append(
                Diagnostic(
                    code="segmentation.segment_too_thin",
                    severity=Severity.WARNING,
                    message=(
                        f"wire {wire.id} has a segment length to radius ratio of "
                        f"{radius_ratio:.2f}; the thin-wire approximation may be invalid"
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

    for line in model.transmission_lines:
        for label, wire_id, offset_m in (
            ("start", line.start_wire_id, line.start_offset_m),
            ("end", line.end_wire_id, line.end_offset_m),
        ):
            segmentation = layout.wire_segmentation(wire_id)
            index = int(offset_m / segmentation.segment_length_m)
            index = min(max(index, 0), segmentation.segments - 1)
            center = (index + 0.5) * segmentation.segment_length_m
            if abs(offset_m - center) > 0.05 * segmentation.segment_length_m:
                diagnostics.append(
                    Diagnostic(
                        code="segmentation.transmission_line_offset",
                        severity=Severity.WARNING,
                        message=(
                            f"transmission line {line.id} {label} point is not at "
                            "the center of its segment; the TL connection is an "
                            "approximation"
                        ),
                        field="transmission_lines",
                    )
                )

    return tuple(diagnostics)


def resolve_model_quality(
    model: AntennaModel,
    spec: SimulationSpec,
    *,
    supports_extended_kernel: bool,
) -> ModelQualityReport:
    """Adjust segmentation and select the extended kernel when needed.

    Short high-frequency wires can fall below the default kernel's segment/radius
    ratio. Reducing their segment count is preferred when the resulting segment
    is still at most 0.1 lambda. If that is not possible, the extended kernel is
    selected when the solver supports it. A segment/radius ratio below 2 or a
    segment shorter than 1e-3 lambda remains blocking.
    """

    frequency_hz = spec.frequency_plan.stop_hz
    wavelength = units.wavelength_m(frequency_hz)
    layout = build_segment_layout(model, spec)
    overrides = dict(spec.segmentation.wire_segments)
    adjusted: list[str] = []

    for segmentation in layout.wires:
        wire = segmentation.wire
        if segmentation.segments <= 1 or wire.radius_m <= 0.0:
            continue
        if segmentation.segment_length_m / wire.radius_m >= THIN_WIRE_MIN_RADIUS_RATIO:
            continue
        maximum_count = max(
            1,
            int(wire.length_m / (THIN_WIRE_MIN_RADIUS_RATIO * wire.radius_m)),
        )
        candidate_count = min(segmentation.segments, maximum_count)
        if candidate_count >= segmentation.segments:
            continue
        candidate_length = wire.length_m / candidate_count
        if candidate_length > MAX_SEGMENT_LENGTH_RELATIVE * wavelength:
            continue
        overrides[wire.id] = candidate_count
        adjusted.append(wire.id)

    if adjusted:
        spec = replace(
            spec,
            segmentation=replace(
                spec.segmentation,
                min_segments_per_wire=1,
                wire_segments=tuple(overrides.items()),
            ),
        )

    final_layout = build_segment_layout(model, spec)
    short = False
    thin = False
    radius_low = False
    for segmentation in final_layout.wires:
        wire = segmentation.wire
        if wire.radius_m <= 0.0:
            continue
        relative_length = segmentation.segment_length_m / wavelength
        radius_ratio = segmentation.segment_length_m / wire.radius_m
        wire_relative = wire.length_m / wavelength
        if radius_ratio < THIN_WIRE_HARD_MIN_RADIUS_RATIO:
            thin = True
        elif radius_ratio < THIN_WIRE_MIN_RADIUS_RATIO:
            radius_low = True
        if (
            relative_length < MIN_SEGMENT_LENGTH_RELATIVE
            and wire_relative >= MIN_WIRE_LENGTH_FOR_SEGMENT_QUALITY_RELATIVE
        ):
            short = True

    if (
        radius_low
        and not spec.extended_thin_wire_kernel
        and supports_extended_kernel
        and not short
        and not thin
    ):
        spec = replace(spec, extended_thin_wire_kernel=True)
        radius_low = False

    blocking: list[str] = []
    if short:
        blocking.append("segmentation.segment_too_short")
    if thin:
        blocking.append("segmentation.segment_too_thin")
    if radius_low and not spec.extended_thin_wire_kernel:
        blocking.append("segmentation.radius_ratio_low")

    return ModelQualityReport(
        spec=spec,
        blocking_codes=tuple(blocking),
        adjusted_wire_ids=tuple(adjusted),
        extended_kernel_enabled=spec.extended_thin_wire_kernel,
    )
