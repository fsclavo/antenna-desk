# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QFont, QFontMetricsF
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.ui.geometry.builder import build_scene
from antennadesk.ui.geometry.layout import (
    SceneTransform,
    layout_angular_dimensions,
    layout_dimensions,
)
from antennadesk.ui.geometry.scene import Dimension, GeometryScene, ScenePoint
from antennadesk.ui.geometry.views import GeometryViewMode
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _build_scene(parameters: object, antenna_type: str) -> GeometryScene:
    return build_scene(
        parameters.to_antenna(),
        antenna_type=antenna_type,
        parameters=parameters,
        display_name=None,
        mode=GeometryViewMode.ELEVATION,
        translator=Translator(Language.ENGLISH),
        unit_system=UnitSystem.METRIC,
    )


def _placement(scene: GeometryScene, width: int, height: int):
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
    reserved = (QRectF(safe.left(), safe.bottom() - 34.0, 230.0, 34.0),)
    return safe, transform, geometry, reserved


def _layout(scene: GeometryScene, width: int, height: int):
    safe, transform, geometry, reserved = _placement(scene, width, height)
    placed = layout_dimensions(
        scene,
        transform,
        safe,
        geometry,
        reserved,
        QFontMetricsF(QFont("Sans Serif", 8)),
    )
    return safe, placed


def test_dimension_offset_scale_moves_labels_closer() -> None:
    scene = GeometryScene(
        dimensions=(
            Dimension(
                start=ScenePoint(0.0, 0.0),
                end=ScenePoint(10.0, 0.0),
                text="10.00 m",
                side="above",
                priority=90,
            ),
        )
    )
    safe = QRectF(0.0, 0.0, 200.0, 100.0)
    transform = SceneTransform(
        center_scene=ScenePoint(5.0, 0.0),
        center_screen=safe.center(),
        scale=10.0,
        pan=QRectF().topLeft(),
    )
    metrics = QFontMetricsF(QFont("Sans Serif", 8))

    normal = layout_dimensions(scene, transform, safe, safe, (), metrics)
    compact = layout_dimensions(
        scene,
        transform,
        safe,
        safe,
        (),
        metrics,
        offset_scale=0.5,
    )

    assert normal
    assert compact
    start = transform.to_screen(ScenePoint(0.0, 0.0))
    normal_offset = abs(normal[0].line_start.y() - start.y())
    compact_offset = abs(compact[0].line_start.y() - start.y())
    assert compact_offset < normal_offset


def test_loop_dimensions_stay_inside_the_safe_area(qtbot: QtBot) -> None:
    del qtbot
    scene = _build_scene(
        LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
            sides=3,
        ),
        "loop",
    )
    safe, placed = _layout(scene, 900, 450)

    assert placed
    assert all(safe.contains(item.text_rect) for item in placed)
    assert len({item.dimension.text for item in placed}) >= 2


def test_dimension_labels_do_not_overlap_each_other(qtbot: QtBot) -> None:
    del qtbot
    scene = _build_scene(
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
    )
    safe, placed = _layout(scene, 900, 450)

    assert placed
    for index, first in enumerate(placed):
        assert safe.contains(first.text_rect)
        for second in placed[index + 1 :]:
            assert not first.text_rect.intersects(second.text_rect)


def test_layout_degrades_without_overlapping_at_minimum_size(qtbot: QtBot) -> None:
    del qtbot
    scene = _build_scene(
        LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
            sides=4,
        ),
        "loop",
    )
    safe, placed = _layout(scene, 360, 240)

    for item in placed:
        assert safe.contains(item.text_rect)
    for index, first in enumerate(placed):
        for second in placed[index + 1 :]:
            assert not first.text_rect.intersects(second.text_rect)


def test_angular_dimension_labels_fit_without_overlap(qtbot: QtBot) -> None:
    del qtbot
    scene = _build_scene(
        InvertedVParameters(
            frequency_hz=7_100_000.0,
            leg_length_m=10.0,
            apex_height_m=12.0,
            included_angle_deg=120.0,
        ),
        "inverted_v",
    )
    safe, transform, _geometry, reserved = _placement(scene, 900, 450)
    placed = layout_angular_dimensions(
        scene,
        transform,
        safe,
        reserved,
        (),
        QFontMetricsF(QFont("Sans Serif", 8)),
    )

    assert placed
    for index, first in enumerate(placed):
        assert safe.contains(first.text_rect)
        for second in placed[index + 1 :]:
            assert not first.text_rect.intersects(second.text_rect)
