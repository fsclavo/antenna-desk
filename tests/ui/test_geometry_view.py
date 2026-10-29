# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

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


def test_geometry_view_renders_a_sketch(qtbot: QtBot) -> None:
    view = _make_view(qtbot)
    pixmap = view.grab()

    assert not pixmap.isNull()
    assert _non_white_pixels(pixmap) > 50


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
