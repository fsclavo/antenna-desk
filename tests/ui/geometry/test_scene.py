# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import discone_parameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loop import LoopOrientation, LoopParameters
from antennadesk.domain.antennas.magnetic_loop import (
    CAPACITOR_WIRE_ID,
    MagneticLoopParameters,
)
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.polarization import Polarization
from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiMatchType, YagiParameters
from antennadesk.ui.geometry.builder import build_scene, effective_antenna_type
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


def test_vertical_yagi_elevation_shows_the_vertical_elements_and_boom() -> None:
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
            YagiElement(position_m=3.5, length_m=9.0, radius_m=0.001),
        ),
        height_m=10.0,
        polarization=Polarization.VERTICAL,
    )

    plan = _scene(parameters, "yagi", GeometryViewMode.PLAN)
    elevation = _scene(parameters, "yagi", GeometryViewMode.ELEVATION)

    assert recommended_view(parameters.to_antenna()) is GeometryViewMode.ELEVATION
    assert len(elevation.polylines) == 3
    for polyline in elevation.polylines:
        first, second = polyline.points
        assert first.x_m == pytest.approx(second.x_m)
        assert abs(second.y_m - first.y_m) > 1.0
    assert "polarization vertical" in elevation.summary
    assert "height 10.00 m" in elevation.summary
    assert any(dimension.text == "3.50 m" for dimension in elevation.dimensions)
    assert "vertical plane is edge-on" in plan.summary


def test_vertical_moxon_elevation_shows_the_rectangle_and_clearance() -> None:
    parameters = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.0,
        depth_m=3.0,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
        polarization=Polarization.VERTICAL,
    )

    elevation = _scene(parameters, "moxon", GeometryViewMode.ELEVATION)
    plan = _scene(parameters, "moxon", GeometryViewMode.PLAN)

    assert recommended_view(parameters.to_antenna()) is GeometryViewMode.ELEVATION
    assert len(elevation.polylines) == 6
    vertical_wires = [
        polyline
        for polyline in elevation.polylines
        if polyline.points[0].x_m == pytest.approx(polyline.points[1].x_m)
    ]
    assert len(vertical_wires) == 2
    assert "polarization vertical" in elevation.summary
    assert "height 10.00 m" in elevation.summary
    assert any(dimension.text == "10.00 m" for dimension in elevation.dimensions)
    assert "vertical plane is edge-on" in plan.summary


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


def test_inverted_l_elevation_shows_the_vertical_and_horizontal_runs() -> None:
    parameters = InvertedLParameters(
        frequency_hz=7_100_000.0,
        vertical_height_m=10.0,
        horizontal_length_m=20.0,
        base_height_m=1.0,
    )

    scene = _scene(parameters, "inverted_l", GeometryViewMode.ELEVATION)
    plan = _scene(parameters, "inverted_l", GeometryViewMode.PLAN)

    assert recommended_view(parameters.to_antenna()) is GeometryViewMode.ELEVATION
    assert len(scene.polylines) == 2
    assert scene.summary.startswith("Inverted L")
    assert "vertical height 10.00 m" in scene.summary
    assert "horizontal length 20.00 m" in scene.summary
    assert "vertical plane is edge-on" in plan.summary
    assert all(dimension.start.distance_to(dimension.end) > 0.0 for dimension in scene.dimensions)
    dimension_texts = {dimension.text for dimension in scene.dimensions}
    assert "10.00 m" in dimension_texts
    assert "20.00 m" in dimension_texts
    assert "11.00 m" in dimension_texts
    assert "1.00 m" in dimension_texts


def test_horizontal_loop_plan_shows_the_polygon_and_elevation_is_edge_on() -> None:
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
        orientation=LoopOrientation.HORIZONTAL,
    )

    plan = _scene(parameters, "loop", GeometryViewMode.PLAN)
    elevation = _scene(parameters, "loop", GeometryViewMode.ELEVATION)

    assert recommended_view(parameters.to_antenna()) is GeometryViewMode.PLAN
    assert len(plan.polylines) == 4
    assert (
        len(
            {
                (round(point.x_m, 6), round(point.y_m, 6))
                for polyline in plan.polylines
                for point in polyline.points
            }
        )
        == 4
    )
    assert "orientation horizontal" in plan.summary
    assert "height 8.00 m" in plan.summary
    assert "horizontal loop is edge-on" in elevation.summary
    assert all(dimension.start.distance_to(dimension.end) > 0.0 for dimension in plan.dimensions)
    assert all(
        dimension.start.distance_to(dimension.end) > 0.0 for dimension in elevation.dimensions
    )


def test_folded_yagi_preserves_the_driven_element_wires() -> None:
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
        driven_folded=True,
        driven_fold_spacing_m=0.1,
    )
    model = parameters.to_antenna()

    scene = _scene(parameters, "yagi", GeometryViewMode.PLAN)

    assert len(model.wires) == 5
    assert model.feed.wire_id == "element-2-a"
    assert len(scene.polylines) == 5
    assert "folded driven" in scene.summary
    assert all(dimension.start.distance_to(dimension.end) > 0.0 for dimension in scene.dimensions)


def test_beta_hairpin_yagi_preserves_the_stub_wires() -> None:
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
        match_type=YagiMatchType.BETA_HAIRPIN,
        match_length_m=0.2,
        match_spacing_m=0.1,
    )
    model = parameters.to_antenna()

    scene = _scene(parameters, "yagi", GeometryViewMode.PLAN)

    assert len(model.wires) == 7
    assert model.feed.wire_id == "element-2-feed"
    assert len(scene.polylines) == 7
    assert "beta / hairpin" in scene.summary
    assert all(dimension.start.distance_to(dimension.end) > 0.0 for dimension in scene.dimensions)


def test_magnetic_loop_shows_the_gap_and_capacitor_in_elevation() -> None:
    parameters = MagneticLoopParameters(
        frequency_hz=7_100_000.0,
        diameter_m=1.0,
        height_m=1.5,
        sides=8,
        gap_length_m=0.05,
        capacitor_esr_ohm=0.2,
    )

    scene = _scene(parameters, "magnetic_loop", GeometryViewMode.ELEVATION)
    plan = _scene(parameters, "magnetic_loop", GeometryViewMode.PLAN)

    assert recommended_view(parameters.to_antenna()) is GeometryViewMode.ELEVATION
    assert len(scene.polylines) == parameters.sides + 2
    assert "Magnetic loop" in scene.summary
    assert "diameter 1.00 m" in scene.summary
    assert "gap 0.050 m" in scene.summary
    assert "200.000 pF" in scene.summary
    assert all(dimension.start.distance_to(dimension.end) > 0.0 for dimension in scene.dimensions)
    assert "vertical plane is edge-on" in plan.summary
    assert CAPACITOR_WIRE_ID in {wire.id for wire in parameters.to_antenna().wires}


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


def test_transmission_lines_are_drawn_as_dashed_construction_lines() -> None:
    from antennadesk.domain.antennas.transmission_line import TransmissionLine

    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=10.0,
    )
    line = TransmissionLine(
        id="line-1",
        start_wire_id="radiator",
        start_offset_m=0.0,
        end_wire_id="radiator",
        end_offset_m=20.0,
        characteristic_impedance_ohm=300.0,
        length_m=10.0,
        velocity_factor=0.9,
    )
    model = parameters.to_antenna().with_transmission_lines((line,))

    scene = build_scene(
        model,
        antenna_type="wire_dipole",
        parameters=parameters,
        display_name=None,
        mode=GeometryViewMode.ELEVATION,
        translator=TRANSLATOR,
        unit_system=UnitSystem.METRIC,
    )

    lines = [polyline for polyline in scene.polylines if polyline.role == "transmission-line"]
    assert len(lines) == 1
    assert lines[0].style == "dashed"
    assert "transmission lines: 1" in scene.summary


def test_loaded_vertical_marks_the_loading_coil() -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        radial_count=4,
        radial_length_m=1.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=12e-6,
    )

    for mode in (GeometryViewMode.ELEVATION, GeometryViewMode.PLAN):
        scene = _scene(parameters, "vertical", mode)
        assert any(marker.kind == "load" for marker in scene.markers)
        assert "radials 4" in scene.summary
        assert "loading coil 12.000 µH" in scene.summary

    elevation = _scene(parameters, "vertical", GeometryViewMode.ELEVATION)
    assert any(
        dimension.label == "Coil height above base" and dimension.text == "1.00 m"
        for dimension in elevation.dimensions
    )


def test_vertical_top_hat_dimensions_the_hat_radius() -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=5.0,
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=2.5,
        top_hat_enabled=True,
        top_hat_radius_m=0.75,
        top_hat_wire_count=4,
    )

    scene = _scene(parameters, "vertical", GeometryViewMode.ELEVATION)

    assert any(
        dimension.label == "Hat radius" and dimension.text == "0.75 m"
        for dimension in scene.dimensions
    )
    assert "capacitive top hat 4 x 0.75 m" in scene.summary


def test_ocfd_construction_view_dimensions_the_feed_offset() -> None:
    from antennadesk.domain.antennas.ocfd import OCFDParameters

    parameters = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=40.0,
        height_m=10.0,
    )

    scene = _scene(parameters, "ocfd", GeometryViewMode.ELEVATION)

    assert any(
        dimension.label == "feed offset" and dimension.text == "13.33 m"
        for dimension in scene.dimensions
    )


def test_trap_dipole_dimensions_the_trap_positions() -> None:
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    parameters = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=10e-6,
        height_m=12.0,
    )

    scene = _scene(parameters, "trap_dipole", GeometryViewMode.ELEVATION)

    dimensions = {(dimension.label, dimension.text) for dimension in scene.dimensions}
    assert ("L1", "5.00 m") in dimensions
    assert ("L2", "15.00 m") in dimensions


def test_loaded_dipole_dimensions_links_from_the_feed() -> None:
    from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters

    scene = _scene(loaded_dipole_parameters(), "loaded_dipole", GeometryViewMode.ELEVATION)

    dimensions = {(dimension.label, dimension.text) for dimension in scene.dimensions}
    assert ("Total length", "20.00 m") in dimensions
    assert ("L1", "2.00 m") in dimensions
    assert ("L2", "2.00 m") in dimensions


def test_scv_construction_view_dimensions_a_nonzero_feed_offset() -> None:
    from antennadesk.domain.antennas.scv import ScvKind, scv_parameters

    parameters = scv_parameters(
        ScvKind.HALF_SQUARE,
        7_150_000.0,
        feed_offset_m=2.0,
    )

    scene = _scene(parameters, "half_square", GeometryViewMode.ELEVATION)

    assert any(
        dimension.label == "Feed offset below top junction" and dimension.text == "2.00 m"
        for dimension in scene.dimensions
    )


def test_trap_dipole_marks_both_traps_and_reports_the_center_section() -> None:
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    parameters = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=10e-6,
        height_m=12.0,
    )

    for mode in (GeometryViewMode.ELEVATION, GeometryViewMode.PLAN):
        scene = _scene(parameters, "trap_dipole", mode)
        loads = [marker for marker in scene.markers if marker.kind == "load"]
        assert len(loads) == 2
        assert "traps 2" in scene.summary
        assert "center 10.00 m" in scene.summary


def test_t2fd_marks_the_feed_and_the_termination_resistor() -> None:
    from antennadesk.domain.antennas.t2fd import T2FDParameters

    parameters = T2FDParameters(
        frequency_hz=3_500_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=26.0,
        spacing_m=0.9,
        height_m=10.0,
    )

    for mode in (GeometryViewMode.ELEVATION, GeometryViewMode.PLAN):
        scene = _scene(parameters, "t2fd", mode)
        loads = [marker for marker in scene.markers if marker.kind == "load"]
        feeds = [marker for marker in scene.markers if marker.kind == "feed"]
        assert len(loads) == 1
        assert len(feeds) == 1
        assert "element length 26.00 m" in scene.summary
        assert "conductor spacing 0.90 m" in scene.summary
        if mode is GeometryViewMode.PLAN:
            assert any(dimension.text == "0.90 m" for dimension in scene.dimensions)


def test_legacy_t2fd_generator_keeps_its_presentation_type() -> None:
    from antennadesk.domain.antennas.t2fd import T2FDParameters

    parameters = T2FDParameters(
        frequency_hz=3_500_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=26.0,
        spacing_m=0.9,
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

    assert effective_antenna_type("custom", custom) == "t2fd"
    assert scene.metadata["antenna_type"] == "t2fd"
    assert len(scene.polylines) == 4


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
    labels = {dimension.label for dimension in scene.dimensions}
    assert {"E1 leg", "E2 leg"} <= labels
    assert "included angle 120.0°, 90.0°" in scene.summary


def test_g5rv_custom_generator_uses_the_dipole_summary_and_dashed_line() -> None:
    from antennadesk.domain.antennas.g5rv import g5rv_parameters

    parameters = g5rv_parameters(frequency_hz=14_100_000.0)

    scene = build_scene(
        parameters.to_antenna(),
        antenna_type="custom",
        parameters=parameters,
        display_name=None,
        mode=GeometryViewMode.ELEVATION,
        translator=TRANSLATOR,
        unit_system=UnitSystem.METRIC,
    )

    assert "Wire dipole" in scene.summary
    assert "transmission lines: 1" in scene.summary
    assert any(polyline.role == "transmission-line" for polyline in scene.polylines)


def test_typed_g5rv_and_zs6bkw_use_their_own_summary_and_line() -> None:
    from antennadesk.domain.antennas.transmission_line_doublet import (
        DoubletPreset,
        doublet_starting_parameters,
    )

    for preset in (DoubletPreset.G5RV, DoubletPreset.ZS6BKW):
        parameters = doublet_starting_parameters(preset)
        scene = build_scene(
            parameters.to_antenna(),
            antenna_type=preset.antenna_type,
            parameters=parameters,
            display_name=None,
            mode=GeometryViewMode.ELEVATION,
            translator=TRANSLATOR,
            unit_system=UnitSystem.METRIC,
        )

        assert parameters.template_name in scene.summary
        assert "matching-line impedance" in scene.summary
        assert "transmission lines: 1" in scene.summary
        assert any(polyline.role == "transmission-line" for polyline in scene.polylines)
        assert len([line for line in scene.polylines if line.role == "wire"]) == 2


def test_zepp_custom_generator_draws_the_second_stub_conductor() -> None:
    from antennadesk.domain.antennas.zepp import zepp_parameters

    parameters = zepp_parameters()

    scene = build_scene(
        parameters.to_antenna(),
        antenna_type="custom",
        parameters=parameters,
        display_name=None,
        mode=GeometryViewMode.ELEVATION,
        translator=TRANSLATOR,
        unit_system=UnitSystem.METRIC,
    )

    assert "Zepp" in scene.summary
    assert "stub 10.03 m" in scene.summary
    assert "spacing 0.050 m" in scene.summary
    assert "transmission lines" not in scene.summary
    assert len([line for line in scene.polylines if line.role == "wire"]) == 4
    assert not any(polyline.role == "transmission-line" for polyline in scene.polylines)


def test_legacy_zepp_project_keeps_the_simplified_geometry_with_a_note() -> None:
    from antennadesk.domain.antennas.custom import CustomAntennaParameters
    from antennadesk.domain.antennas.feed import FeedPoint
    from antennadesk.domain.antennas.geometry import Point3D
    from antennadesk.domain.antennas.materials import COPPER
    from antennadesk.domain.antennas.wire import Wire

    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire("zepp-source", Point3D(0.0, 0.0, 1.0), Point3D(0.0, 0.0, 1.1), 0.001, COPPER),
            Wire(
                "zepp-radiator",
                Point3D(0.0, 0.0, 10.0),
                Point3D(20.0, 0.0, 10.0),
                0.001,
                COPPER,
            ),
        ),
        feed=FeedPoint("zepp-radiator", 0.0),
        generator_id="zepp",
        generator_name="Zepp",
    )

    assert effective_antenna_type("custom", parameters) == "zepp"
    scene = build_scene(
        parameters.to_antenna(),
        antenna_type="custom",
        parameters=parameters,
        display_name=None,
        mode=GeometryViewMode.ELEVATION,
        translator=TRANSLATOR,
        unit_system=UnitSystem.METRIC,
    )

    assert any("Legacy simplified Zepp model" in note for note in scene.notes)
    assert len([line for line in scene.polylines if line.role == "wire"]) == 2


def test_zs6bkw_custom_generator_uses_the_dipole_summary_and_dashed_line() -> None:
    from antennadesk.domain.antennas.zs6bkw import zs6bkw_parameters

    parameters = zs6bkw_parameters()

    scene = build_scene(
        parameters.to_antenna(),
        antenna_type="custom",
        parameters=parameters,
        display_name=None,
        mode=GeometryViewMode.ELEVATION,
        translator=TRANSLATOR,
        unit_system=UnitSystem.METRIC,
    )

    assert "Wire dipole" in scene.summary
    assert "transmission lines: 1" in scene.summary
    assert any(polyline.role == "transmission-line" for polyline in scene.polylines)


def test_beverage_construction_view_keeps_the_length_dimension() -> None:
    parameters = beverage_parameters()

    scene = _scene(parameters, "beverage", GeometryViewMode.ELEVATION)

    assert any(dimension.text.startswith("42.") for dimension in scene.dimensions)
    assert not any("vertical plane is edge-on" in note for note in scene.notes)


def test_hexbeam_dimensions_anchor_to_the_named_geometry() -> None:
    parameters = published_hexbeam_parameters()
    scene = _scene(parameters, "hexbeam", GeometryViewMode.PLAN)

    span = next(dimension for dimension in scene.dimensions if dimension.text == "9.03 m")
    assert span.start.distance_to(span.end) == pytest.approx(9.03, abs=1e-2)
    assert any("published tip-gap parameter" in note for note in scene.notes)


def test_magnetic_loop_does_not_label_a_chord_as_the_diameter() -> None:
    parameters = MagneticLoopParameters(
        frequency_hz=7_100_000.0,
        diameter_m=1.0,
        height_m=1.5,
        sides=8,
        gap_length_m=0.05,
    )
    scene = _scene(parameters, "magnetic_loop", GeometryViewMode.ELEVATION)

    assert not any(dimension.text == "1.00 m" for dimension in scene.dimensions)
    assert any("circumscribed loop diameter" in note for note in scene.notes)


def test_discone_plan_does_not_draw_vertical_heights() -> None:
    parameters = discone_parameters(
        frequency_hz=145_000_000.0,
        cone_height_m=0.5,
        cone_radius_m=0.3,
        disc_radius_m=0.5,
        base_height_m=0.5,
        wire_count=6,
    )
    scene = _scene(parameters, "discone", GeometryViewMode.PLAN)

    assert len(scene.dimensions) == 2
    assert {dimension.text for dimension in scene.dimensions} == {"0.30 m", "0.50 m"}


def test_yagi_plan_labels_elements_and_spacings() -> None:
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
            YagiElement(position_m=4.0, length_m=9.0, radius_m=0.001),
        ),
        height_m=10.0,
    )

    scene = _scene(parameters, "yagi", GeometryViewMode.PLAN)

    dimensions = {(dimension.label, dimension.text) for dimension in scene.dimensions}
    assert ("E1", "10.00 m") in dimensions
    assert ("E2", "9.50 m") in dimensions
    assert ("E3", "9.00 m") in dimensions
    assert ("1-2", "2.00 m") in dimensions
    assert ("2-3", "2.00 m") in dimensions


def test_moxon_plan_has_a_tip_detail_inset() -> None:
    parameters = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.0,
        depth_m=3.0,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
    )

    scene = _scene(parameters, "moxon", GeometryViewMode.PLAN)

    inset = next(inset for inset in scene.insets if inset.label.startswith("tip detail"))
    dimensions = {(dimension.label, dimension.text) for dimension in inset.dimensions}
    assert ("R tip", "1.00 m") in dimensions
    assert ("D tip", "1.00 m") in dimensions
    assert ("gap", "1.00 m") in dimensions


def test_hexbeam_plan_dimensions_the_half_and_spreader_angle() -> None:
    parameters = published_hexbeam_parameters()

    scene = _scene(parameters, "hexbeam", GeometryViewMode.PLAN)

    assert any(angle.text == "60.0°" for angle in scene.angular_dimensions)
    assert any(
        dimension.label == "Turning radius" and dimension.text == "3.30 m"
        for dimension in scene.dimensions
    )
    inset = next(inset for inset in scene.insets if inset.label.startswith("left half"))
    labels = {dimension.label for dimension in inset.dimensions}
    assert {"Di", "Do", "Ri", "Ro"} <= labels


def test_trap_yagi_plan_labels_elements_and_spacings() -> None:
    parameters = trap_yagi_parameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        element_count=3,
        driven_length_m=20.0,
        reflector_spacing_m=4.0,
        director_spacing_m=3.0,
        trap_inset_m=3.0,
        trap_frequency_hz=14_100_000.0,
    )

    scene = _scene(parameters, "trap_yagi", GeometryViewMode.PLAN)

    dimensions = {(dimension.label, dimension.text) for dimension in scene.dimensions}
    assert ("reflector", "21.00 m") in dimensions
    assert ("driven", "20.00 m") in dimensions
    assert ("director", "19.00 m") in dimensions
    assert ("reflector spacing", "4.00 m") in dimensions
    assert ("director spacing", "3.00 m") in dimensions
    inset = next(inset for inset in scene.insets if inset.label.startswith("trap detail"))
    assert any(
        dimension.label == "trap inset" and dimension.text == "3.00 m"
        for dimension in inset.dimensions
    )


def test_quad_beam_plan_labels_loops_and_spacings() -> None:
    parameters = quad_beam_parameters(
        frequency_hz=14_100_000.0,
        element_count=3,
        loop_side_m=5.0,
        reflector_spacing_m=4.0,
        director_spacing_m=3.0,
        height_m=2.5,
    )

    scene = _scene(parameters, "quad_beam", GeometryViewMode.PLAN)

    dimensions = {(dimension.label, dimension.text) for dimension in scene.dimensions}
    assert ("reflector", "5.25 m") in dimensions
    assert ("driven", "5.00 m") in dimensions
    assert ("director", "4.75 m") in dimensions
    assert ("director spacing", "3.00 m") in dimensions


def test_j_pole_construction_view_labels_the_feed_and_repeated_values() -> None:
    parameters = JPoleParameters(
        frequency_hz=220_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        base_height_m=0.25,
    )
    scene = _scene(parameters, "j_pole", GeometryViewMode.ELEVATION)

    labels = {dimension.label for dimension in scene.dimensions}
    assert "feed offset" in labels
    assert "Base height" in labels
    assert "Radiator" in labels
    assert "Stub" in labels
    assert "feed offset 0.10 m" in scene.summary
    assert "base 0.25 m" in scene.summary
