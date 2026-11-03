# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Contract tests that every antenna family must satisfy."""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

import pytest
from PySide6.QtCore import QRectF
from PySide6.QtGui import QFont, QFontMetricsF
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.ui.geometry.builder import (
    SUPPORTED_PRESENTATION_TYPES,
    build_scene,
    effective_antenna_type,
)
from antennadesk.ui.geometry.layout import SceneTransform, layout_dimensions
from antennadesk.ui.geometry.scene import GeometryScene, ScenePoint
from antennadesk.ui.geometry.views import GeometryViewMode, recommended_view
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem

TRANSLATOR = Translator(Language.ENGLISH)


@dataclass(frozen=True, slots=True)
class FamilyCase:
    name: str
    parameters: object
    antenna_type: str
    wires: int
    default_view: GeometryViewMode
    summary_parts: tuple[str, ...]


def _cases() -> tuple[FamilyCase, ...]:
    return (
        FamilyCase(
            "dipole",
            DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
            "wire_dipole",
            1,
            GeometryViewMode.ELEVATION,
            ("Wire dipole", "length 20.00 m"),
        ),
        FamilyCase(
            "trap_dipole",
            TrapDipoleParameters(
                frequency_hz=7_100_000.0,
                high_band_frequency_hz=14_100_000.0,
                inner_length_m=10.0,
                outer_length_m=5.0,
                trap_frequency_hz=14_100_000.0,
                trap_inductance_h=10e-6,
                height_m=12.0,
            ),
            "trap_dipole",
            1,
            GeometryViewMode.ELEVATION,
            ("Trap dipole", "traps 2", "total length"),
        ),
        FamilyCase(
            "folded",
            FoldedDipoleParameters(
                frequency_hz=7_100_000.0,
                total_length_m=20.0,
                height_m=8.0,
                spacing_m=0.2,
            ),
            "folded_dipole",
            4,
            GeometryViewMode.PLAN,
            ("Folded dipole", "spacing 0.20 m"),
        ),
        FamilyCase(
            "delta",
            LoopParameters(
                frequency_hz=7_100_000.0,
                circumference_m=40.0,
                height_m=8.0,
                sides=3,
            ),
            "loop",
            3,
            GeometryViewMode.ELEVATION,
            ("Delta loop", "sides 3"),
        ),
        FamilyCase(
            "quad",
            LoopParameters(
                frequency_hz=7_100_000.0,
                circumference_m=40.0,
                height_m=8.0,
                sides=4,
            ),
            "loop",
            4,
            GeometryViewMode.ELEVATION,
            ("Quad loop", "sides 4"),
        ),
        FamilyCase(
            "ocfd",
            OCFDParameters(frequency_hz=7_100_000.0, total_length_m=40.0),
            "ocfd",
            1,
            GeometryViewMode.ELEVATION,
            ("Off-center-fed dipole", "feed offset"),
        ),
        FamilyCase(
            "vertical",
            VerticalParameters(
                frequency_hz=7_100_000.0,
                height_m=10.0,
                radial_count=4,
                radial_length_m=5.2,
            ),
            "vertical",
            5,
            GeometryViewMode.ELEVATION,
            ("Vertical", "radials 4"),
        ),
        FamilyCase(
            "inverted_v",
            InvertedVParameters(
                frequency_hz=7_100_000.0,
                leg_length_m=10.0,
                apex_height_m=12.0,
            ),
            "inverted_v",
            2,
            GeometryViewMode.ELEVATION,
            ("Inverted-V", "included angle"),
        ),
        FamilyCase(
            "yagi",
            YagiParameters(
                frequency_hz=14_100_000.0,
                elements=(
                    YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
                    YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
                ),
                height_m=10.0,
            ),
            "yagi",
            2,
            GeometryViewMode.PLAN,
            ("Yagi", "elements 2"),
        ),
        FamilyCase(
            "moxon",
            MoxonParameters(
                frequency_hz=14_100_000.0,
                width_m=10.0,
                depth_m=3.0,
                reflector_tip_m=1.0,
                driven_tip_m=1.0,
                height_m=10.0,
            ),
            "moxon",
            6,
            GeometryViewMode.PLAN,
            ("Moxon", "gap"),
        ),
        FamilyCase(
            "fan",
            FanDipoleParameters(
                frequency_hz=7_100_000.0,
                elements=(FanElement(20.0, 120.0), FanElement(10.0, 120.0)),
                apex_height_m=12.0,
            ),
            "fan_dipole",
            4,
            GeometryViewMode.ELEVATION,
            ("Fan dipole", "elements 2"),
        ),
        FamilyCase(
            "endfed",
            EndFedParameters(
                frequency_hz=7_100_000.0,
                length_m=20.0,
                feed_height_m=2.0,
                end_height_m=10.0,
            ),
            "endfed",
            1,
            GeometryViewMode.ELEVATION,
            ("End-fed wire", "wire length 20.00 m"),
        ),
        FamilyCase(
            "jpole",
            JPoleParameters(
                frequency_hz=220_000_000.0,
                radiator_height_m=1.0,
                stub_length_m=0.5,
                spacing_m=0.05,
                feed_offset_m=0.1,
                base_height_m=0.25,
                folded=True,
            ),
            "j_pole",
            5,
            GeometryViewMode.ELEVATION,
            ("Slim Jim",),
        ),
        FamilyCase(
            "ringo",
            RingoParameters(
                frequency_hz=29_000_000.0,
                radiator_height_m=5.0,
                ring_diameter_m=0.5,
                ring_height_m=0.25,
                ring_sides=16,
            ),
            "ringo",
            18,
            GeometryViewMode.ELEVATION,
            ("Ringo", "diameter 0.50 m"),
        ),
        FamilyCase(
            "custom",
            CustomAntennaParameters(
                frequency_hz=7_100_000.0,
                wires=(
                    Wire(
                        "w1",
                        Point3D(-3.0, 0.0, 5.0),
                        Point3D(3.0, 2.0, 9.0),
                        0.001,
                        COPPER,
                    ),
                ),
                feed=FeedPoint("w1", 2.0),
            ),
            "custom",
            1,
            GeometryViewMode.ELEVATION,
            ("Custom", "overall dimensions"),
        ),
    )


CASES = _cases()


def _scene(case: FamilyCase, mode: GeometryViewMode) -> GeometryScene:
    return build_scene(
        case.parameters.to_antenna(),
        antenna_type=case.antenna_type,
        parameters=case.parameters,
        display_name=None,
        mode=mode,
        translator=TRANSLATOR,
        unit_system=UnitSystem.METRIC,
    )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
@pytest.mark.parametrize("mode", (GeometryViewMode.ELEVATION, GeometryViewMode.PLAN))
def test_family_scene_preserves_wires_and_positive_dimensions(
    case: FamilyCase,
    mode: GeometryViewMode,
) -> None:
    model = case.parameters.to_antenna()
    scene = _scene(case, mode)

    assert len(scene.polylines) == case.wires
    assert len(model.wires) == case.wires
    assert scene.summary
    assert any(marker.kind == "feed" for marker in scene.markers)
    if scene.show_ground:
        assert scene.ground_y_m is not None
    for polyline in scene.polylines:
        assert len(polyline.points) >= 2
        assert all(
            math.isfinite(point.x_m) and math.isfinite(point.y_m) for point in polyline.points
        )
    for dimension in scene.dimensions:
        assert dimension.text
        assert dimension.start.distance_to(dimension.end) > 0.0
    for angular in scene.angular_dimensions:
        assert angular.text
        assert angular.center.distance_to(angular.first) > 0.0
        assert angular.center.distance_to(angular.second) > 0.0
    for expected in case.summary_parts:
        assert expected in scene.summary


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_family_default_view_matches_geometry_policy(case: FamilyCase) -> None:
    assert recommended_view(case.parameters.to_antenna()) is case.default_view


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_family_layout_is_inside_safe_area_without_label_overlap(
    qtbot: QtBot,
    case: FamilyCase,
) -> None:
    del qtbot
    scene = _scene(case, GeometryViewMode.ELEVATION)
    safe, placed = _layout(scene, 900, 450)

    for index, first in enumerate(placed):
        assert safe.contains(first.text_rect)
        for second in placed[index + 1 :]:
            assert not first.text_rect.intersects(second.text_rect)


def test_loop_shape_signature_tracks_the_side_count() -> None:
    for sides in (3, 4, 16):
        parameters = LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
            sides=sides,
        )
        scene = build_scene(
            parameters.to_antenna(),
            antenna_type="loop",
            parameters=parameters,
            display_name=None,
            mode=GeometryViewMode.ELEVATION,
            translator=TRANSLATOR,
            unit_system=UnitSystem.METRIC,
        )
        vertices = {
            (round(point.x_m, 6), round(point.y_m, 6))
            for polyline in scene.polylines
            for point in polyline.points
        }
        assert len(scene.polylines) == sides
        assert len(vertices) == sides


def test_every_domain_antenna_type_has_a_presentation_family() -> None:
    from antennadesk.domain.antennas import (
        custom,
        dipole,
        endfed,
        fan_dipole,
        folded_dipole,
        inverted_v,
        j_pole,
        loop,
        moxon,
        ocfd,
        ringo,
        vertical,
        yagi,
    )

    modules = (
        custom,
        dipole,
        endfed,
        fan_dipole,
        folded_dipole,
        inverted_v,
        j_pole,
        loop,
        moxon,
        ocfd,
        ringo,
        vertical,
        yagi,
    )
    domain_types = {
        value
        for module in modules
        for name, value in vars(module).items()
        if name.startswith("ANTENNA_TYPE_") and isinstance(value, str)
    }

    assert domain_types <= SUPPORTED_PRESENTATION_TYPES


def test_legacy_generator_ids_map_to_presentation_types() -> None:
    parameters = (
        JPoleParameters(
            frequency_hz=220_000_000.0,
            radiator_height_m=1.0,
            stub_length_m=0.5,
            spacing_m=0.05,
            folded=True,
        ),
        RingoParameters(
            frequency_hz=29_000_000.0,
            radiator_height_m=5.0,
            ring_diameter_m=0.5,
        ),
        VerticalParameters(frequency_hz=7_100_000.0, height_m=10.0),
        OCFDParameters(frequency_hz=7_100_000.0, total_length_m=40.0),
        EndFedParameters(frequency_hz=7_100_000.0, length_m=20.0),
    )

    for item in parameters:
        custom = item.to_custom_parameters()
        assert effective_antenna_type("custom", custom) is not None


def _layout(scene: GeometryScene, width: int, height: int):
    safe = QRectF(12.0, 54.0, width - 24.0, height - 108.0)
    bounds = scene.bounds()
    assert bounds is not None
    min_point, max_point = bounds
    span_x = max(max_point.x_m - min_point.x_m, 1e-6)
    span_y = max(max_point.y_m - min_point.y_m, 1e-6)
    margin = min(max(38.0, safe.width() * 0.10), 90.0)
    available = QRectF(
        safe.left() + margin,
        safe.top() + 12.0,
        safe.width() - 2.0 * margin,
        safe.height() - 54.0,
    )
    scale = min(available.width() / span_x, available.height() / span_y)
    transform = SceneTransform(
        center_scene=ScenePoint(
            (min_point.x_m + max_point.x_m) / 2.0,
            (min_point.y_m + max_point.y_m) / 2.0,
        ),
        center_screen=available.center(),
        scale=scale,
        pan=QRectF().topLeft(),
    )
    points = [transform.to_screen(point) for point in scene.points()]
    geometry = QRectF(
        min(point.x() for point in points),
        min(point.y() for point in points),
        max(point.x() for point in points) - min(point.x() for point in points),
        max(point.y() for point in points) - min(point.y() for point in points),
    )
    return safe, layout_dimensions(
        scene,
        transform,
        safe,
        geometry,
        (),
        QFontMetricsF(QFont("Sans Serif", 8)),
    )


GOLDEN_PATH = Path(__file__).with_name("golden_scenes.json")


def _rounded(value: float) -> float:
    rounded = round(value, 6)
    return 0.0 if rounded == 0.0 else rounded


def _snapshot(case: FamilyCase, mode: GeometryViewMode) -> str:
    scene = _scene(case, mode)
    data = {
        "polylines": [
            [[_rounded(point.x_m), _rounded(point.y_m)] for point in polyline.points]
            for polyline in scene.polylines
        ],
        "markers": sorted(
            [
                [marker.kind, _rounded(marker.point.x_m), _rounded(marker.point.y_m)]
                for marker in scene.markers
            ]
        ),
        "dimensions": sorted(
            [
                [
                    _rounded(dimension.start.x_m),
                    _rounded(dimension.start.y_m),
                    _rounded(dimension.end.x_m),
                    _rounded(dimension.end.y_m),
                    dimension.text,
                ]
                for dimension in scene.dimensions
            ]
        ),
        "angular": sorted(
            [
                [
                    _rounded(dimension.center.x_m),
                    _rounded(dimension.center.y_m),
                    _rounded(dimension.first.x_m),
                    _rounded(dimension.first.y_m),
                    _rounded(dimension.second.x_m),
                    _rounded(dimension.second.y_m),
                    dimension.text,
                ]
                for dimension in scene.angular_dimensions
            ]
        ),
        "show_ground": scene.show_ground,
        "ground_y_m": (_rounded(scene.ground_y_m) if scene.ground_y_m is not None else None),
        "is_plan": scene.is_plan,
        "insets": [
            {
                "label": inset.label,
                "polylines": [
                    [[_rounded(point.x_m), _rounded(point.y_m)] for point in polyline.points]
                    for polyline in inset.polylines
                ],
                "dimensions": [
                    [
                        _rounded(dimension.start.x_m),
                        _rounded(dimension.start.y_m),
                        _rounded(dimension.end.x_m),
                        _rounded(dimension.end.y_m),
                        dimension.text,
                    ]
                    for dimension in inset.dimensions
                ],
            }
            for inset in scene.insets
        ],
    }
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_scene_snapshots_are_stable() -> None:
    snapshots = {
        f"{case.name}:{mode.value}": _snapshot(case, mode)
        for case in CASES
        for mode in (GeometryViewMode.ELEVATION, GeometryViewMode.PLAN)
    }
    if os.environ.get("UPDATE_GEOMETRY_GOLDENS") == "1":
        GOLDEN_PATH.write_text(
            json.dumps(snapshots, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return
    assert GOLDEN_PATH.is_file(), (
        "geometry golden snapshots are missing; run with UPDATE_GEOMETRY_GOLDENS=1 to create them"
    )
    expected = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    assert snapshots == expected
