# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.theme import DARK, LIGHT, is_dark_palette, theme_colors
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.geometry_view import GeometryView
from antennadesk.ui.widgets.results_view import ResultsView


def _palette(window_color: str) -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(window_color))
    return palette


@pytest.fixture
def restore_app_palette() -> Iterator[None]:
    app = QApplication.instance()
    assert app is not None
    original = app.palette()
    try:
        yield
    finally:
        app.setPalette(original)


def test_palette_detection_and_palettes() -> None:
    assert is_dark_palette(_palette("#202020")) is True
    assert is_dark_palette(_palette("#f0f0f0")) is False
    assert theme_colors(_palette("#202020")) is DARK
    assert theme_colors(_palette("#f0f0f0")) is LIGHT


def test_geometry_view_uses_dark_and_light_backgrounds(
    qtbot: QtBot,
    restore_app_palette: None,
) -> None:
    app = QApplication.instance()
    assert app is not None
    model = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna()

    app.setPalette(_palette("#202020"))
    dark_view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dark_view)
    dark_view.resize(900, 340)
    dark_view.set_model(model)
    dark_view.show()
    qtbot.wait(10)

    assert dark_view._colors.background.name() == "#1e1e1e"
    assert dark_view.grab().toImage().pixelColor(5, 5).name() == "#1e1e1e"

    app.setPalette(_palette("#f0f0f0"))
    qtbot.wait(10)

    assert dark_view._colors.background.name() == "#ffffff"
    assert dark_view.grab().toImage().pixelColor(5, 5).name() == "#ffffff"


def test_results_view_uses_dark_plot_background(
    qtbot: QtBot,
    restore_app_palette: None,
) -> None:
    app = QApplication.instance()
    assert app is not None
    app.setPalette(_palette("#202020"))

    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    qtbot.wait(10)

    assert view._colors.plot_background.name() == "#1e1e1e"
    assert view._impedance_plot.backgroundBrush().color().name() == "#1e1e1e"
    assert view._swr_plot.backgroundBrush().color().name() == "#1e1e1e"
    assert view._impedance_plot.getAxis("left").pen().color().name() == "#c8c8c8"

    app.setPalette(_palette("#f0f0f0"))
    qtbot.wait(10)

    assert view._colors.plot_background.name() == "#ffffff"
    assert view._impedance_plot.backgroundBrush().color().name() == "#ffffff"
