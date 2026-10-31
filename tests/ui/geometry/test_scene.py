# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.ui.geometry.builder import build_scene
from antennadesk.ui.geometry.views import GeometryViewMode, recommended_view
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem

TRANSLATOR = Translator(Language.ENGLISH)


def _scene(
    parameters: object,
    antenna_type: str,
    mode: GeometryViewMode,
    display_name: str | None = None,
):
    model = parameters.to_antenna()
    return build_scene(
        model,
        antenna_type=antenna_type,
        parameters=parameters,
        display_name=display_name,
        mode=mode,
        translator=TRANSLATOR,
        unit_system=UnitSystem.METRIC,
    )


def test_delta_loop_front_view_uses_the_actual_triangle() -> None:
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=3,
    )

    scene = _scene(parameters, "loop", GeometryViewMode.ELEVATION)

    assert len(scene.polylines) == 3
    assert all(len(polyline.points) == 2 for polyline in scene.polylines)
    points = scene.points()
    width = max(point.x_m for point in points) - min(point.x_m for point in points)
    height = max(point.y_m for point in points) - min(point.y_m for point in points)
    assert width == pytest.approx(11.547, abs=1e-3)
    assert height == pytest.approx(13.333, abs=1e-3)
    assert "Delta loop" in scene.summary
    assert "equivalent diameter 15.40 m" in scene.summary


def test_quad_loop_front_view_is_a_square_not_a_circle() -> None:
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
    )

    scene = _scene(parameters, "loop", GeometryViewMode.ELEVATION)

    assert len(scene.polylines) == 4
    vertices = {
        (round(point.x_m, 6), round(point.y_m, 6))
        for polyline in scene.polylines
        for point in polyline.points
    }
    assert len(vertices) == 4
    assert "Quad loop" in scene.summary


def test_vertical_loop_plan_is_edge_on() -> None:
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
    )

    scene = _scene(parameters, "loop", GeometryViewMode.PLAN)

    assert len(scene.polylines) == 4
    assert all(
        math.isclose(point.y_m, 0.0, abs_tol=1e-9)
        for polyline in scene.polylines
        for point in polyline.points
    )
    assert "top view" in scene.summary
    assert "top view is edge-on" in scene.summary
    assert all(dimension.start.distance_to(dimension.end) > 0.0 for dimension in scene.dimensions)


def test_single_wire_elevation_keeps_a_sloped_end_fed_wire() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=2.0,
        end_height_m=10.0,
    )

    scene = _scene(parameters, "endfed", GeometryViewMode.ELEVATION)

    assert len(scene.polylines) == 1
    first, second = scene.polylines[0].points
    assert not math.isclose(first.y_m, second.y_m, abs_tol=1e-9)
    assert "front view" not in scene.summary


def test_yagi_plan_keeps_all_elements_and_elevation_warns_about_overlap() -> None:
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
            YagiElement(position_m=3.5, length_m=9.0, radius_m=0.001),
        ),
        height_m=10.0,
    )

    plan = _scene(parameters, "yagi", GeometryViewMode.PLAN)
    elevation = _scene(parameters, "yagi", GeometryViewMode.ELEVATION)

    assert len(plan.polylines) == 3
    midpoints = {
        round((polyline.points[0].x_m + polyline.points[1].x_m) / 2.0, 6)
        for polyline in plan.polylines
    }
    assert len(midpoints) == 3
    assert "elements 3" in plan.summary
    assert "front view: elements overlap" in elevation.summary


def test_slim_jim_exposes_the_gap_and_the_actual_feed_height() -> None:
    parameters = JPoleParameters(
        frequency_hz=220_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        base_height_m=0.25,
        folded=True,
    )

    scene = _scene(parameters, "j_pole", GeometryViewMode.ELEVATION, "Slim Jim")

    assert len(scene.polylines) == 5
    assert any(marker.kind == "feed" for marker in scene.markers)
    wire = parameters.to_custom_parameters().wires
    feed_wire = next(item for item in wire if item.id == "right-lower")
    feed_ratio = parameters.to_custom_parameters().feed.offset_m / feed_wire.length_m
    expected_z = feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * feed_ratio
    assert expected_z == pytest.approx(parameters.base_height_m + parameters.feed_offset_m)
    assert "Slim Jim" in scene.summary
    assert "gap 0.010 m" in scene.summary
    assert any(inset.label.startswith("gap detail") for inset in scene.insets)


def test_ringo_gets_a_top_inset_with_the_matching_ring() -> None:
    parameters = RingoParameters(
        frequency_hz=29_000_000.0,
        radiator_height_m=5.0,
        ring_diameter_m=0.5,
        ring_height_m=0.25,
        ring_sides=16,
    )

    scene = _scene(parameters, "ringo", GeometryViewMode.ELEVATION)

    assert len(scene.polylines) == 18
    assert any(inset.label == "top view" for inset in scene.insets)
    inset = next(inset for inset in scene.insets if inset.label == "top view")
    assert len(inset.polylines) == 18
    assert "diameter 0.50 m" in scene.summary


def test_recommended_view_uses_the_geometry_shape() -> None:
    loop = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
    ).to_antenna()
    yagi = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
    ).to_antenna()
    dipole = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna()

    assert recommended_view(loop) is GeometryViewMode.ELEVATION
    assert recommended_view(yagi) is GeometryViewMode.PLAN
    assert recommended_view(dipole) is GeometryViewMode.ELEVATION


def test_folded_plan_draws_all_four_wires() -> None:
    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )

    scene = _scene(parameters, "folded_dipole", GeometryViewMode.PLAN)

    assert len(scene.polylines) == 4
    assert "spacing 0.20 m" in scene.summary
    assert any(inset.label.startswith("spacing detail") for inset in scene.insets)


def test_vertical_with_radials_gets_a_top_inset() -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        radial_count=4,
        radial_length_m=5.2,
    )

    scene = _scene(parameters, "vertical", GeometryViewMode.ELEVATION)

    assert any(inset.label == "top view" for inset in scene.insets)
    assert "radials 4" in scene.summary


def test_legacy_custom_slim_jim_keeps_its_presentation_type() -> None:
    parameters = JPoleParameters(
        frequency_hz=220_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        base_height_m=0.25,
        folded=True,
    )
    custom = parameters.to_custom_parameters()

    scene = build_scene(
        custom.to_antenna(),
        antenna_type="custom",
        parameters=custom,
        display_name=None,
        mode=GeometryViewMode.ELEVATION,
        translator=TRANSLATOR,
        unit_system=UnitSystem.METRIC,
    )

    assert "Slim Jim" in scene.summary
    assert any(inset.label.startswith("gap detail") for inset in scene.insets)


def test_series_loads_are_marked_in_every_two_dimensional_view() -> None:
    from antennadesk.domain.antennas.load import SeriesLoad

    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
    )
    model = parameters.to_antenna().with_loads(
        (SeriesLoad("load-1", "loop-0", 2.0, resistance_ohm=50.0),)
    )

    for mode in (GeometryViewMode.ELEVATION, GeometryViewMode.PLAN):
        scene = build_scene(
            model,
            antenna_type="loop",
            parameters=parameters,
            display_name=None,
            mode=mode,
            translator=TRANSLATOR,
            unit_system=UnitSystem.METRIC,
        )
        assert any(marker.kind == "load" for marker in scene.markers)


def test_legacy_custom_yagi_keeps_semantic_dimensions() -> None:
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
            YagiElement(position_m=3.5, length_m=9.0, radius_m=0.001),
        ),
        height_m=10.0,
    )
    custom = parameters.to_custom_parameters()

    scene = build_scene(
        custom.to_antenna(),
        antenna_type="custom",
        parameters=custom,
        display_name=None,
        mode=GeometryViewMode.PLAN,
        translator=TRANSLATOR,
        unit_system=UnitSystem.METRIC,
    )

    assert "elements 3" in scene.summary
    assert "boom length 3.50 m" in scene.summary


def test_inverted_v_has_an_included_angle_annotation() -> None:
    from antennadesk.domain.antennas.inverted_v import InvertedVParameters

    parameters = InvertedVParameters(
        frequency_hz=7_100_000.0,
        leg_length_m=10.0,
        apex_height_m=12.0,
        included_angle_deg=120.0,
    )

    scene = _scene(parameters, "inverted_v", GeometryViewMode.ELEVATION)

    assert len(scene.angular_dimensions) == 1
    assert scene.angular_dimensions[0].text == "120.0°"


def test_fan_dipole_has_one_angle_annotation_per_element() -> None:
    from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement

    parameters = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(FanElement(20.0, 120.0), FanElement(10.0, 90.0)),
        apex_height_m=12.0,
    )

    scene = _scene(parameters, "fan_dipole", GeometryViewMode.ELEVATION)

    assert len(scene.angular_dimensions) == 2
    assert {dimension.text for dimension in scene.angular_dimensions} == {
        "120.0°",
        "90.0°",
    }
