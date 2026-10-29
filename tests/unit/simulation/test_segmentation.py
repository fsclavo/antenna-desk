# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.discretization import (
    build_segment_layout,
    validate_segmentation,
)


def _wire(
    wire_id: str = "radiator",
    length_m: float = 20.0,
    radius_m: float = 0.001,
) -> Wire:
    return Wire(
        id=wire_id,
        start=Point3D(-length_m / 2.0, 0.0, 8.0),
        end=Point3D(length_m / 2.0, 0.0, 8.0),
        radius_m=radius_m,
        material=COPPER,
    )


def _model(
    wire: Wire | None = None,
    *,
    feed_offset_m: float | None = None,
) -> AntennaModel:
    antenna_wire = wire if wire is not None else _wire()
    offset = feed_offset_m if feed_offset_m is not None else antenna_wire.length_m / 2.0
    return AntennaModel(
        name="test",
        design_frequency_hz=7_100_000.0,
        wires=(antenna_wire,),
        feed=FeedPoint(antenna_wire.id, offset),
    )


def _spec(
    *,
    segments_per_wire: int | None = None,
    frequency_hz: float = 7_100_000.0,
    extended_thin_wire_kernel: bool = False,
) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(frequency_hz),
        segmentation=SegmentationPolicy(segments_per_wire=segments_per_wire),
        extended_thin_wire_kernel=extended_thin_wire_kernel,
        far_field=FarFieldRequest(enabled=False),
    )


def test_explicit_segment_count() -> None:
    policy = SegmentationPolicy(segments_per_wire=7)
    assert policy.segments_for(_wire(length_m=0.5), 299_800_000.0) == 7


def test_default_segment_count_uses_shortest_wavelength() -> None:
    policy = SegmentationPolicy()
    assert policy.segments_for(_wire(length_m=20.0), 7_100_000.0) == 24


def test_segment_count_is_clamped() -> None:
    short_wire = _wire(length_m=0.1)
    policy = SegmentationPolicy(min_segments_per_wire=5, max_segments_per_wire=10)
    assert policy.segments_for(short_wire, 7_100_000.0) == 5

    long_wire = _wire(length_m=100.0)
    policy = SegmentationPolicy(max_segments_per_wire=10)
    assert policy.segments_for(long_wire, 7_100_000.0) == 10


def test_invalid_policy_values_are_rejected() -> None:
    with pytest.raises(ValueError, match="positive"):
        SegmentationPolicy(target_segment_length_wavelengths=0.0)
    with pytest.raises(ValueError, match="at least 1"):
        SegmentationPolicy(min_segments_per_wire=0)
    with pytest.raises(ValueError, match="greater than or equal"):
        SegmentationPolicy(min_segments_per_wire=10, max_segments_per_wire=5)
    with pytest.raises(ValueError, match="below"):
        SegmentationPolicy(segments_per_wire=1, min_segments_per_wire=2)


def test_single_wire_layout() -> None:
    model = _model(_wire(length_m=0.5))
    spec = _spec(segments_per_wire=7, frequency_hz=299_800_000.0)
    layout = build_segment_layout(model, spec)

    assert layout.feed_tag == 1
    assert layout.feed_segment == 4
    segmentation = layout.wires[0]
    assert segmentation.tag == 1
    assert segmentation.segments == 7
    assert segmentation.first_segment == 1
    assert segmentation.last_segment == 7
    assert segmentation.segment_length_m == pytest.approx(0.5 / 7.0)


def test_multi_wire_layout_and_feed_mapping() -> None:
    first = Wire(
        id="first",
        start=Point3D(-1.0, 0.0, 0.0),
        end=Point3D(0.0, 0.0, 0.0),
        radius_m=0.001,
        material=COPPER,
    )
    second = Wire(
        id="second",
        start=Point3D(0.0, 0.0, 0.0),
        end=Point3D(1.0, 0.0, 0.0),
        radius_m=0.001,
        material=COPPER,
    )
    model = AntennaModel(
        name="two wires",
        design_frequency_hz=7_100_000.0,
        wires=(first, second),
        feed=FeedPoint("second", 0.5),
    )
    spec = _spec(segments_per_wire=10)
    layout = build_segment_layout(model, spec)

    assert layout.feed_tag == 2
    assert layout.feed_segment == 16
    assert layout.wires[0].first_segment == 1
    assert layout.wires[0].last_segment == 10
    assert layout.wires[1].first_segment == 11
    assert layout.wires[1].last_segment == 20
    assert layout.wire_segmentation("second") == layout.wires[1]


def test_unknown_wire_lookup_raises() -> None:
    layout = build_segment_layout(_model(), _spec(segments_per_wire=7))
    with pytest.raises(KeyError):
        layout.wire_segmentation("missing")


def test_long_segments_and_few_segments_warn() -> None:
    model = _model(_wire(length_m=1.0), feed_offset_m=0.5)
    spec = _spec(segments_per_wire=1, frequency_hz=300_000_000.0)
    codes = {diagnostic.code for diagnostic in validate_segmentation(model, spec)}

    assert "segmentation.few_segments" in codes
    assert "segmentation.segment_too_long" in codes


def test_thin_wire_warning_is_suppressed_with_extended_kernel() -> None:
    model = _model(_wire(length_m=1.0, radius_m=0.75), feed_offset_m=0.5)
    standard = _spec(segments_per_wire=1, frequency_hz=300_000_000.0)
    extended = _spec(
        segments_per_wire=1,
        frequency_hz=300_000_000.0,
        extended_thin_wire_kernel=True,
    )

    assert "segmentation.segment_too_thin" in {
        diagnostic.code for diagnostic in validate_segmentation(model, standard)
    }
    assert "segmentation.segment_too_thin" not in {
        diagnostic.code for diagnostic in validate_segmentation(model, extended)
    }


def test_feed_at_segment_boundary_warns() -> None:
    model = _model(_wire(length_m=20.0), feed_offset_m=10.0)
    spec = _spec(segments_per_wire=20)
    codes = {diagnostic.code for diagnostic in validate_segmentation(model, spec)}

    assert "segmentation.feed_offset" in codes


def test_centered_feed_does_not_warn() -> None:
    model = _model(_wire(length_m=20.0), feed_offset_m=10.0)
    spec = _spec(segments_per_wire=21)
    codes = {diagnostic.code for diagnostic in validate_segmentation(model, spec)}

    assert "segmentation.feed_offset" not in codes
