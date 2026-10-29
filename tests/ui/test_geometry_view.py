# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.geometry_view import GeometryView


def test_geometry_view_renders_a_sketch(qtbot: QtBot) -> None:
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

    pixmap = view.grab()
    image = pixmap.toImage()

    assert not pixmap.isNull()
    assert image.width() > 0
    assert image.height() > 0
    non_white = 0
    for y in range(0, image.height(), 6):
        for x in range(0, image.width(), 6):
            if image.pixelColor(x, y).name() != "#ffffff":
                non_white += 1
    assert non_white > 50
