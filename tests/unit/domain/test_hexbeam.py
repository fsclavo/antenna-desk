# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math
from dataclasses import replace

import pytest

from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    with_primary_dimension,
)
from antennadesk.domain.antennas.family import (
    AntennaFamily,
    antenna_family,
    antenna_template_id,
)
from antennadesk.domain.antennas.hexbeam import (
    PUBLISHED_DRIVER_HALF_M,
    PUBLISHED_HEXBEAM_FREQUENCY_HZ,
    PUBLISHED_REFLECTOR_HALF_M,
    PUBLISHED_TIP_GAP_M,
    PUBLISHED_TURNING_RADIUS_M,
    HexbeamGeometryError,
    HexbeamParameters,
    hexbeam_frame_geometry,
    published_hexbeam_multiband_parameters,
    published_hexbeam_parameters,
)


def _wire(model, wire_id: str):  # type: ignore[no-untyped-def]
    return next(wire for wire in model.wires if wire.id == wire_id)


def _published_multiband():  # type: ignore[no-untyped-def]
    return published_hexbeam_multiband_parameters()


def test_published_hexbeam_reference_dimensions() -> None:
    parameters = published_hexbeam_parameters()

    assert parameters.template_name == "Hexbeam"
    assert parameters.frequency_hz == pytest.approx(PUBLISHED_HEXBEAM_FREQUENCY_HZ)
    assert parameters.driver_half_length_m == pytest.approx(PUBLISHED_DRIVER_HALF_M)
    assert parameters.reflector_half_length_m == pytest.approx(PUBLISHED_REFLECTOR_HALF_M)
    assert parameters.tip_gap_m == pytest.approx(PUBLISHED_TIP_GAP_M)
    assert parameters.turning_radius_m == pytest.approx(PUBLISHED_TURNING_RADIUS_M)
    assert parameters.element_separation_m == pytest.approx(0.0)
    assert parameters.driver_tip_half_span_m < parameters.turning_radius_m
    assert parameters.reflector_tip_half_span_m < parameters.turning_radius_m
    assert parameters.overall_span_m == pytest.approx(2.0 * parameters.turning_radius_m)
    assert parameters.turning_diameter_m == pytest.approx(parameters.overall_span_m)
    assert parameters.total_conductor_length_m == pytest.approx(
        2.0 * (PUBLISHED_DRIVER_HALF_M + PUBLISHED_REFLECTOR_HALF_M) + parameters.feed_gap_m
    )


def test_hexbeam_builds_an_m_driver_and_rear_u_reflector() -> None:
    parameters = published_hexbeam_parameters(height_m=12.0)

    model = parameters.to_antenna()

    assert len(model.wires) == 10
    assert model.feed.wire_id == "hexbeam-feed"
    assert model.feed.offset_m == pytest.approx(parameters.feed_gap_m / 2.0)
    assert parameters.height_m == pytest.approx(12.0)
    assert len(model.sources) == 0
    driver_ids = {wire.id for wire in model.wires if "driver" in wire.id}
    reflector_ids = {wire.id for wire in model.wires if "reflector" in wire.id}
    assert driver_ids == {
        "hexbeam-driver-left-inner",
        "hexbeam-driver-left-tip",
        "hexbeam-driver-right-inner",
        "hexbeam-driver-right-tip",
    }
    assert reflector_ids == {
        "hexbeam-reflector-left-inner",
        "hexbeam-reflector-left-tip",
        "hexbeam-reflector-rear",
        "hexbeam-reflector-right-inner",
        "hexbeam-reflector-right-tip",
    }
    assert all(wire.start.z_m == pytest.approx(12.0) for wire in model.wires)

    rear = _wire(model, "hexbeam-reflector-rear")
    rear_midpoint_x = (rear.start.x_m + rear.end.x_m) / 2.0
    assert rear_midpoint_x == pytest.approx(-parameters.turning_radius_m * math.sqrt(3.0) / 2.0)
    assert rear.start.y_m + rear.end.y_m == pytest.approx(0.0)

    reflector_points = [
        point for wire in model.wires if "reflector" in wire.id for point in (wire.start, wire.end)
    ]
    assert min(math.hypot(point.x_m, point.y_m) for point in reflector_points) > 2.0

    left_tip = _wire(model, "hexbeam-driver-left-tip").end
    right_tip = _wire(model, "hexbeam-driver-right-tip").end
    assert math.hypot(left_tip.x_m, left_tip.y_m) < parameters.turning_radius_m
    assert math.hypot(right_tip.x_m, right_tip.y_m) < parameters.turning_radius_m


def test_hexbeam_wire_points_stay_inside_the_turning_radius() -> None:
    parameters = published_hexbeam_parameters()
    model = parameters.to_antenna()

    radii = [
        math.hypot(point.x_m, point.y_m) for wire in model.wires for point in (wire.start, wire.end)
    ]

    assert max(radii) <= parameters.turning_radius_m + 1e-9
    assert max(radii) == pytest.approx(parameters.turning_radius_m)


def test_hexbeam_path_lengths_match_the_published_halves() -> None:
    parameters = published_hexbeam_parameters()
    frame = parameters.frame
    model = parameters.to_antenna()

    assert frame.knee_radius_m + frame.driver_tip_leg_m == pytest.approx(
        parameters.driver_half_length_m,
        abs=1e-9,
    )

    left_half = (
        _wire(model, "hexbeam-driver-left-inner").length_m
        + _wire(model, "hexbeam-driver-left-tip").length_m
    )
    right_half = (
        _wire(model, "hexbeam-driver-right-inner").length_m
        + _wire(model, "hexbeam-driver-right-tip").length_m
    )
    assert left_half > parameters.driver_half_length_m > right_half
    assert (left_half + right_half) / 2.0 == pytest.approx(
        parameters.driver_half_length_m,
        abs=1e-3,
    )

    reflector_left = (
        parameters.turning_radius_m / 2.0
        + _wire(model, "hexbeam-reflector-left-inner").length_m
        + _wire(model, "hexbeam-reflector-left-tip").length_m
    )
    assert reflector_left == pytest.approx(parameters.reflector_half_length_m, abs=1e-9)


def test_hexbeam_tip_gap_matches_the_published_spacer() -> None:
    parameters = published_hexbeam_parameters()
    model = parameters.to_antenna()

    for side in ("left", "right"):
        driver_tip = _wire(model, f"hexbeam-driver-{side}-tip").end
        reflector_end = _wire(model, f"hexbeam-reflector-{side}-tip").start
        gap = math.hypot(
            driver_tip.x_m - reflector_end.x_m,
            driver_tip.y_m - reflector_end.y_m,
        )
        assert gap == pytest.approx(parameters.tip_gap_m, abs=1e-9)


def test_hexbeam_span_is_the_turning_diameter() -> None:
    parameters = published_hexbeam_parameters()

    assert parameters.overall_span_m == pytest.approx(6.604, abs=1e-3)
    assert parameters.overall_span_m == pytest.approx(2.0 * parameters.turning_radius_m)
    assert parameters.driver_tip_half_span_m < parameters.turning_radius_m
    assert parameters.reflector_tip_half_span_m < parameters.turning_radius_m


def test_hexbeam_total_conductor_equals_the_wire_sum() -> None:
    parameters = published_hexbeam_parameters()
    model = parameters.to_antenna()

    assert sum(wire.length_m for wire in model.wires) == pytest.approx(
        parameters.total_conductor_length_m,
        abs=1e-3,
    )


def test_hexbeam_azimuth_rotation_preserves_frame_invariants() -> None:
    reference = published_hexbeam_parameters()
    rotated = replace(reference, azimuth_deg=30.0)
    reference_model = reference.to_antenna()
    rotated_model = rotated.to_antenna()

    assert [wire.length_m for wire in rotated_model.wires] == pytest.approx(
        [wire.length_m for wire in reference_model.wires]
    )
    reference_radii = [
        math.hypot(point.x_m, point.y_m)
        for wire in reference_model.wires
        for point in (wire.start, wire.end)
    ]
    rotated_radii = [
        math.hypot(point.x_m, point.y_m)
        for wire in rotated_model.wires
        for point in (wire.start, wire.end)
    ]
    assert sorted(rotated_radii) == pytest.approx(sorted(reference_radii))


def test_hexbeam_element_separation_trims_the_reflector() -> None:
    published = published_hexbeam_parameters()
    trimmed = replace(published, element_separation_m=0.10)
    published_model = published.to_antenna()
    trimmed_model = trimmed.to_antenna()

    for wire in published_model.wires:
        if "driver" not in wire.id and wire.id != "hexbeam-feed":
            continue
        trimmed_wire = _wire(trimmed_model, wire.id)
        assert trimmed_wire.start == wire.start
        assert trimmed_wire.end == wire.end

    rear = _wire(trimmed_model, "hexbeam-reflector-rear")
    published_rear = _wire(published_model, "hexbeam-reflector-rear")
    assert (rear.start.x_m + rear.end.x_m) / 2.0 == pytest.approx(
        (published_rear.start.x_m + published_rear.end.x_m) / 2.0 - 0.10
    )


def test_hexbeam_rejects_paths_that_do_not_fit_the_frame() -> None:
    with pytest.raises(HexbeamGeometryError, match="reflector_half_length_m is too short"):
        HexbeamParameters(
            frequency_hz=14_184_000.0,
            driver_half_length_m=5.5372,
            reflector_half_length_m=4.0,
            turning_radius_m=3.302,
            tip_gap_m=0.6096,
        )
    with pytest.raises(HexbeamGeometryError, match="places the driver tip past"):
        HexbeamParameters(
            frequency_hz=14_184_000.0,
            driver_half_length_m=5.5372,
            reflector_half_length_m=8.25,
            turning_radius_m=3.302,
            tip_gap_m=0.6096,
        )
    with pytest.raises(HexbeamGeometryError, match="no valid knee"):
        HexbeamParameters(
            frequency_hz=14_184_000.0,
            driver_half_length_m=1.0,
            reflector_half_length_m=5.2324,
            turning_radius_m=3.302,
            tip_gap_m=0.6096,
        )
    with pytest.raises(ValueError, match="tip_gap_m"):
        HexbeamParameters(
            frequency_hz=14_184_000.0,
            driver_half_length_m=5.5372,
            reflector_half_length_m=5.2324,
            turning_radius_m=3.302,
            tip_gap_m=0.001,
            wire_radius_m=0.001,
        )


@pytest.mark.parametrize(
    ("driver_in", "reflector_in"),
    [(219.0, 207.0), (218.0, 206.0)],
)
def test_hexbeam_both_published_20m_rows_fit(driver_in: float, reflector_in: float) -> None:
    radius = PUBLISHED_TURNING_RADIUS_M
    frame = hexbeam_frame_geometry(
        turning_radius_m=radius,
        driver_half_length_m=driver_in * 0.0254,
        reflector_half_length_m=reflector_in * 0.0254,
        tip_gap_m=PUBLISHED_TIP_GAP_M,
    )
    parameters = HexbeamParameters(
        frequency_hz=PUBLISHED_HEXBEAM_FREQUENCY_HZ,
        driver_half_length_m=driver_in * 0.0254,
        reflector_half_length_m=reflector_in * 0.0254,
        turning_radius_m=radius,
        tip_gap_m=PUBLISHED_TIP_GAP_M,
    )
    model = parameters.to_antenna()

    assert frame.knee_radius_m <= radius
    assert all(
        math.hypot(point.x_m, point.y_m) <= radius + 1e-9
        for wire in model.wires
        for point in (wire.start, wire.end)
    )
    assert parameters.overall_span_m == pytest.approx(2.0 * radius)


def test_published_multiband_uses_the_five_band_table() -> None:
    parameters = published_hexbeam_multiband_parameters()

    assert tuple(band.label for band in parameters.bands) == (
        "20m",
        "17m",
        "15m",
        "12m",
        "10m",
    )
    assert parameters.turning_radius_m == pytest.approx(130.0 * 0.0254)
    assert parameters.driver_half_length_m == pytest.approx(218.0 * 0.0254)
    assert parameters.reflector_half_length_m == pytest.approx(206.0 * 0.0254)
    assert parameters.tip_gap_m == pytest.approx(24.0 * 0.0254)
    assert tuple(round(band.vertical_offset_m / 0.0254, 1) for band in parameters.bands) == (
        38.0,
        15.0,
        9.0,
        5.0,
        0.0,
    )
    assert tuple(
        round(parameters.band_radius_m(band) / 0.0254, 1) for band in parameters.bands
    ) == pytest.approx((130.0, 101.8, 87.0, 73.9, 64.7), abs=0.1)


def test_published_multiband_subset_normalizes_the_reference_height() -> None:
    parameters = published_hexbeam_multiband_parameters(labels=("20m", "17m", "15m"))

    assert tuple(band.label for band in parameters.bands) == ("20m", "17m", "15m")
    assert parameters.turning_radius_m == pytest.approx(130.0 * 0.0254)
    assert tuple(round(band.vertical_offset_m / 0.0254, 1) for band in parameters.bands) == (
        29.0,
        6.0,
        0.0,
    )
    assert parameters.bands[0].vertical_offset_m > parameters.bands[-1].vertical_offset_m


def test_published_multiband_rejects_unknown_labels() -> None:
    with pytest.raises(ValueError, match="unknown hexbeam band labels"):
        published_hexbeam_multiband_parameters(labels=("30m",))


def test_hexbeam_multiband_builds_nested_bands_and_sources() -> None:
    parameters = _published_multiband()
    model = parameters.to_antenna()

    assert len(parameters.resolved_bands) == 5
    assert len(model.wires) == 50
    assert len(model.sources) == 4
    assert model.feed.wire_id == "hexbeam-feed"
    assert {source.wire_id for source in model.sources} == {
        "hexbeam-band2-feed",
        "hexbeam-band3-feed",
        "hexbeam-band4-feed",
        "hexbeam-band5-feed",
    }

    expected_offsets = (0.9652, 0.3810, 0.2286, 0.1270, 0.0)
    band_z = tuple(
        sorted(
            {round(wire.start.z_m, 6) for wire in model.wires if "feed" in wire.id},
            reverse=True,
        )
    )
    assert band_z == pytest.approx(tuple(10.0 + offset for offset in expected_offsets))

    for index, band in enumerate(parameters.resolved_bands):
        if index == 0:
            band_wires = [
                wire
                for wire in model.wires
                if wire.id.startswith("hexbeam-") and not wire.id.startswith("hexbeam-band")
            ]
        else:
            band_wires = [
                wire for wire in model.wires if wire.id.startswith(f"hexbeam-band{index + 1}-")
            ]
        band_radius = parameters.band_radius_m(band)
        assert len(band_wires) == 10
        band_max_radius = max(
            math.hypot(point.x_m, point.y_m)
            for wire in band_wires
            for point in (wire.start, wire.end)
        )
        assert band_max_radius == pytest.approx(band_radius)
        assert band_radius <= parameters.turning_radius_m

    max_radius = max(
        math.hypot(point.x_m, point.y_m) for wire in model.wires for point in (wire.start, wire.end)
    )
    assert max_radius == pytest.approx(parameters.turning_radius_m)


def test_hexbeam_multiband_total_conductor_sums_every_band() -> None:
    parameters = _published_multiband()
    model = parameters.to_antenna()

    expected = sum(
        2.0 * (band.driver_half_length_m + band.reflector_half_length_m) + band.feed_gap_m
        for band in parameters.resolved_bands
    )

    assert parameters.total_conductor_length_m == pytest.approx(expected)
    assert sum(wire.length_m for wire in model.wires) == pytest.approx(expected, abs=1e-3)


def test_hexbeam_multiband_requires_the_largest_band_first() -> None:
    parameters = _published_multiband()

    with pytest.raises(ValueError, match="lowest frequency"):
        replace(parameters, bands=tuple(reversed(parameters.bands)))


def test_hexbeam_multiband_validates_unique_labels_and_frequencies() -> None:
    parameters = _published_multiband()
    duplicate_label = replace(parameters.bands[1], label=parameters.bands[0].label)

    with pytest.raises(ValueError, match="labels must be unique"):
        replace(parameters, bands=(parameters.bands[0], duplicate_label))

    duplicate_frequency = replace(
        parameters.bands[1],
        frequency_hz=parameters.bands[0].frequency_hz,
    )
    with pytest.raises(ValueError, match="frequencies must be unique"):
        replace(parameters, bands=(parameters.bands[0], duplicate_frequency))


def test_hexbeam_multiband_scales_all_bands_with_the_primary_dimension() -> None:
    parameters = _published_multiband()

    scaled = with_primary_dimension(
        parameters,
        parameters.driver_half_length_m * 1.1,
    )

    assert isinstance(scaled, HexbeamParameters)
    assert len(scaled.bands) == 5
    assert scaled.driver_half_length_m == pytest.approx(parameters.driver_half_length_m * 1.1)
    for original, changed in zip(parameters.bands, scaled.bands, strict=True):
        assert changed.label == original.label
        assert changed.driver_half_length_m == pytest.approx(original.driver_half_length_m * 1.1)
        assert changed.reflector_half_length_m == pytest.approx(
            original.reflector_half_length_m * 1.1
        )
        assert changed.vertical_offset_m == pytest.approx(original.vertical_offset_m * 1.1)


def test_hexbeam_scales_with_frequency() -> None:
    reference = published_hexbeam_parameters()
    lower = published_hexbeam_parameters(frequency_hz=7_092_000.0)
    ratio = 2.0
    assert lower.driver_half_length_m == pytest.approx(reference.driver_half_length_m * ratio)
    assert lower.reflector_half_length_m == pytest.approx(reference.reflector_half_length_m * ratio)
    assert lower.turning_radius_m == pytest.approx(reference.turning_radius_m * ratio)
    assert lower.tip_gap_m == pytest.approx(reference.tip_gap_m * ratio)
    assert lower.overall_span_m == pytest.approx(reference.overall_span_m * ratio)


def test_hexbeam_primary_dimension_scales_the_wire_path() -> None:
    parameters = published_hexbeam_parameters()

    assert primary_dimension_m(parameters) == pytest.approx(parameters.driver_half_length_m)

    scaled = with_primary_dimension(parameters, parameters.driver_half_length_m * 1.1)

    assert isinstance(scaled, HexbeamParameters)
    assert scaled.driver_half_length_m == pytest.approx(parameters.driver_half_length_m * 1.1)
    assert scaled.turning_radius_m == pytest.approx(parameters.turning_radius_m * 1.1)
    assert scaled.tip_gap_m == pytest.approx(parameters.tip_gap_m * 1.1)
    assert scaled.overall_span_m == pytest.approx(parameters.overall_span_m * 1.1)
    assert antenna_type_for(scaled) == "hexbeam"
    assert antenna_template_id(scaled) == "hexbeam"
    assert antenna_family(scaled) is AntennaFamily.YAGI
