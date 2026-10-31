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


def test_geometry_view_marks_series_loads(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.load import SeriesLoad

    model = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna()
    model = model.with_loads((SeriesLoad("load-1", "radiator", 10.0, resistance_ohm=50.0),))
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)
    view.resize(900, 340)
    view.set_model(model, antenna_type="wire_dipole")
    view.set_view_mode(GeometryViewMode.PLAN)
    view.show()

    assert len(view._load_marks()) == 1
    assert not view.grab().isNull()


def test_three_d_projection_places_positive_height_upward() -> None:
    from antennadesk.ui.widgets.geometry_view import GeometryView

    _, ground_y = GeometryView._project_3d(0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.5)
    _, raised_y = GeometryView._project_3d(0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.5)

    assert raised_y > ground_y


def test_j_pole_geometry_has_dedicated_plan_and_elevation(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.j_pole import JPoleParameters
    from antennadesk.ui.widgets.geometry_view import GeometryViewMode

    model = JPoleParameters(
        frequency_hz=220_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
    ).to_antenna()
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)
    view.set_model(model, antenna_type="j_pole")

    view.set_view_mode(GeometryViewMode.ELEVATION)
    assert view.grab().isNull() is False
    assert "radiator" in (view._last_summary or "")

    view.set_view_mode(GeometryViewMode.PLAN)
    assert view.grab().isNull() is False
    assert "spacing" in (view._last_summary or "")


def test_slim_jim_geometry_uses_the_j_pole_views(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.j_pole import JPoleParameters
    from antennadesk.ui.widgets.geometry_view import GeometryViewMode

    model = JPoleParameters(
        frequency_hz=220_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        base_height_m=0.25,
        folded=True,
    ).to_antenna(name="Initial")
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)
    view.set_model(model, antenna_type="j_pole", display_name="Slim Jim")

    view.set_view_mode(GeometryViewMode.ELEVATION)
    assert view.grab().isNull() is False
    assert "Slim Jim" in (view._last_summary or "")

    view.set_view_mode(GeometryViewMode.PLAN)
    assert view.grab().isNull() is False
    assert "Slim Jim top view" in (view._last_summary or "")


def test_set_model_resets_zoom_pan_and_exaggeration(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    view = _make_view(qtbot)
    view.set_zoom(8.0)
    view.set_height_exaggeration(2.0)
    view._pan = view._pan + view._pan
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=3,
    )

    view.set_model(
        parameters.to_antenna(),
        antenna_type="loop",
        parameters=parameters,
    )

    assert view._zoom == pytest.approx(1.0)
    assert view._pan.x() == pytest.approx(0.0)
    assert view._pan.y() == pytest.approx(0.0)
    assert view._height_exaggeration == pytest.approx(1.0)
    assert view._mode is GeometryViewMode.ELEVATION


def test_loop_view_uses_the_actual_polygon(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=3,
    )
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)
    view.resize(900, 340)
    view.set_model(
        parameters.to_antenna(),
        antenna_type="loop",
        parameters=parameters,
    )
    view.set_view_mode(GeometryViewMode.ELEVATION)
    view.grab()

    assert view.scene is not None
    assert len(view.scene.polylines) == 3
    assert "Delta loop" in (view._last_summary or "")
    assert "top view is edge-on" not in (view._last_summary or "")


def test_small_geometry_view_reports_hidden_dimensions(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=3,
    )
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)
    view.resize(360, 240)
    view.set_model(
        parameters.to_antenna(),
        antenna_type="loop",
        parameters=parameters,
    )
    view.grab()

    assert "hidden" in (view._last_summary or "")


def test_three_d_view_can_be_rotated_and_reset(qtbot: QtBot) -> None:
    from PySide6.QtCore import QPoint, Qt

    view = _make_view(qtbot)
    view.set_view_mode(GeometryViewMode.THREE_D)
    view.show()
    initial_yaw = view._three_d_yaw_deg
    initial_pitch = view._three_d_pitch_deg

    qtbot.mousePress(view, Qt.MouseButton.LeftButton, pos=QPoint(100, 100))
    qtbot.mouseMove(view, QPoint(150, 120))
    qtbot.mouseRelease(view, Qt.MouseButton.LeftButton, pos=QPoint(150, 120))

    assert view._three_d_yaw_deg != pytest.approx(initial_yaw)
    assert view._three_d_pitch_deg != pytest.approx(initial_pitch)

    qtbot.mouseDClick(view, Qt.MouseButton.LeftButton, pos=QPoint(100, 100))
    assert view._three_d_yaw_deg == pytest.approx(42.0)
    assert view._three_d_pitch_deg == pytest.approx(24.0)


def test_geometry_view_exports_vector_svg_pdf_and_dxf(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    import ezdxf

    view = _make_view(qtbot)
    svg_path = tmp_path / "geometry.svg"
    pdf_path = tmp_path / "geometry.pdf"
    dxf_path = tmp_path / "geometry.dxf"

    view.save_svg(svg_path)
    view.save_pdf(pdf_path)
    view.save_dxf(dxf_path)

    svg = svg_path.read_text(encoding="utf-8")
    assert "<svg" in svg
    assert "polyline" in svg
    assert pdf_path.read_bytes().startswith(b"%PDF")
    document = ezdxf.readfile(dxf_path)
    entity_types = [entity.dxftype() for entity in document.modelspace()]
    assert "LWPOLYLINE" in entity_types
    assert "DIMENSION" in entity_types
    assert "ANTENNA_WIRES" in document.layers
