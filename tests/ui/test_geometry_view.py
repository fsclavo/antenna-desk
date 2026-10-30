# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtGui import QPixmap
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.geometry_view import GeometryView, GeometryViewMode


def _make_view(qtbot: QtBot) -> GeometryView:
    model = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna()
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)
    view.resize(900, 340)
    view.set_model(model)
    view.show()
    return view


def _non_white_pixels(pixmap: QPixmap) -> int:
    image = pixmap.toImage()
    non_white = 0
    for y in range(0, image.height(), 6):
        for x in range(0, image.width(), 6):
            if image.pixelColor(x, y).name() != "#ffffff":
                non_white += 1
    return non_white


def test_geometry_view_renders_a_sketch(qtbot: QtBot, tmp_path: Path) -> None:
    view = _make_view(qtbot)
    pixmap = view.grab()

    assert not pixmap.isNull()
    assert _non_white_pixels(pixmap) > 50
    image_path = tmp_path / "geometry.png"
    view.save_image(image_path)
    assert image_path.read_bytes().startswith(b"\x89PNG")


def test_geometry_view_plan_renders(qtbot: QtBot) -> None:
    view = _make_view(qtbot)
    view.set_view_mode(GeometryViewMode.PLAN)
    pixmap = view.grab()

    assert _non_white_pixels(pixmap) > 50


def test_geometry_view_exaggerated_height_renders(qtbot: QtBot) -> None:
    view = _make_view(qtbot)
    view.set_height_exaggeration(2.0)
    pixmap = view.grab()

    assert _non_white_pixels(pixmap) > 50


def test_geometry_view_vertical_renders(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.dipole import DipoleOrientation, DipoleParameters

    model = DipoleParameters(
        frequency_hz=30_000_000.0,
        total_length_m=5.0,
        height_m=2.0,
        orientation=DipoleOrientation.VERTICAL,
        wire_radius_m=0.3,
    ).to_antenna()
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)
    view.resize(900, 340)
    view.set_model(model)
    view.show()

    pixmap = view.grab()

    assert _non_white_pixels(pixmap) > 50


def test_geometry_view_renders_multi_wire_plan(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    model = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    ).to_antenna()
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)
    view.resize(900, 340)
    view.set_model(model)
    view.set_view_mode(GeometryViewMode.PLAN)
    view.show()

    pixmap = view.grab()

    assert _non_white_pixels(pixmap) > 50


def test_geometry_view_renders_multi_wire_elevation(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    model = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=8,
    ).to_antenna()
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)
    view.resize(900, 340)
    view.set_model(model)
    view.show()

    pixmap = view.grab()

    assert _non_white_pixels(pixmap) > 50


def test_geometry_summaries_keep_construction_in_plan_and_installation_in_elevation(
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
    from antennadesk.domain.antennas.loop import LoopParameters

    folded = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    ).to_antenna()
    loop = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=8,
    ).to_antenna()

    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)

    view.set_model(folded)
    assert view._antenna_type == "folded_dipole"
    assert view._installation_summary(8.0, 8.0) == (
        "Folded dipole · height 8.00 m · feed height 8.00 m"
    )
    folded_summary = view._multi_wire_plan_summary(20.0, 0.2, "m")
    assert view._folded_spacing_m() == pytest.approx(0.2)
    assert "Folded dipole" in folded_summary
    assert "element 20.00 m" in folded_summary
    assert "spacing 0.20 m" in folded_summary
    assert "total conductor 40.40 m" in folded_summary

    view.set_model(loop)
    assert view._antenna_type == "loop"
    assert view._installation_summary(8.0, 8.0) == ("Loop · height 8.00 m · feed height 8.00 m")
    loop_summary = view._multi_wire_plan_summary(14.14, 14.14, "m")
    assert "Loop" in loop_summary
    assert "circumference 40.00 m" in loop_summary
    assert "diameter 13.07 m" in loop_summary
    assert "8 sides" in loop_summary


def test_geometry_view_infers_a_square_loop_from_equal_sides(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    model = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
    ).to_antenna()
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)

    view.set_model(model)

    assert view._antenna_type == "loop"


def test_geometry_view_pans_while_dragging(qtbot: QtBot) -> None:
    from PySide6.QtCore import QPoint, Qt

    view = _make_view(qtbot)
    view.set_zoom(2.0)

    qtbot.mousePress(view, Qt.MouseButton.LeftButton, pos=QPoint(100, 100))
    qtbot.mouseMove(view, QPoint(130, 125))
    qtbot.mouseRelease(view, Qt.MouseButton.LeftButton, pos=QPoint(130, 125))

    assert view._pan.x() == pytest.approx(30.0)
    assert view._pan.y() == pytest.approx(25.0)


def test_geometry_view_renders_three_d(qtbot: QtBot) -> None:
    view = _make_view(qtbot)
    view.set_view_mode(GeometryViewMode.THREE_D)
    pixmap = view.grab()

    assert _non_white_pixels(pixmap) > 50
