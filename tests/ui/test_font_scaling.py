# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Font scaling for custom-painted views, start page, and plots."""

from __future__ import annotations

import pytest
from helpers import make_completed_result
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

import antennadesk.ui.widgets.geometry_view as geometry_module
import antennadesk.ui.widgets.polar_pattern_view as polar_module
import antennadesk.ui.widgets.radiation_pattern_3d_view as pattern_3d_module
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.dialogs.comparison_dialog import ComparisonDialog
from antennadesk.ui.dialogs.feed_line_dialog import FeedLineDialog
from antennadesk.ui.fonts import (
    scaled_dialog_size,
    scaled_font,
    scaled_pixel_font,
)
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.preferences import (
    FontSize,
    FontSizeController,
    InMemoryPreferencesStore,
)
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.geometry_view import GeometryView
from antennadesk.ui.widgets.polar_pattern_view import PolarPatternView
from antennadesk.ui.widgets.radiation_pattern_3d_view import RadiationPattern3DView
from antennadesk.ui.widgets.results_view import ResultsView
from antennadesk.ui.widgets.start_page import StartPage


def _application() -> QApplication:
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    return app


def _controller() -> FontSizeController:
    base = QFont("Sans Serif", 10)
    _application().setFont(base)
    return FontSizeController(base)


def test_scaled_fonts_follow_the_active_preset() -> None:
    controller = _controller()

    controller.apply(FontSize.LARGE)
    assert scaled_font(8.0).pointSizeF() == pytest.approx(9.6)
    assert scaled_pixel_font(22).pixelSize() == 26

    controller.apply(FontSize.SMALL)
    assert scaled_font(8.0).pointSizeF() == pytest.approx(7.2)
    assert scaled_pixel_font(22).pixelSize() == 20

    controller.apply(FontSize.MEDIUM)
    assert scaled_font(8.0).pointSizeF() == pytest.approx(8.0)
    assert scaled_pixel_font(22).pixelSize() == 22


def test_scaled_dialog_size_follows_the_preset() -> None:
    controller = _controller()

    controller.apply(FontSize.LARGE)
    assert scaled_dialog_size(440, 260) == (528, 312)

    controller.apply(FontSize.SMALL)
    assert scaled_dialog_size(440, 260) == (396, 240)

    controller.apply(FontSize.MEDIUM)
    assert scaled_dialog_size(440, 260) == (440, 260)


def test_feed_line_dialog_uses_the_scaled_initial_size(qtbot: QtBot) -> None:
    controller = _controller()
    controller.apply(FontSize.LARGE)
    dialog = FeedLineDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert dialog.width() == 528
    assert dialog.height() == 312


def test_main_window_renders_large_spanish(qtbot: QtBot) -> None:
    controller = _controller()
    controller.apply(FontSize.LARGE)
    window = MainWindow(
        JsonProjectRepository(),
        None,
        Translator(Language.SPANISH),
        UnitSystem.METRIC,
        preferences=InMemoryPreferencesStore(),
        font_size_controller=controller,
    )
    qtbot.addWidget(window)
    window.resize(1200, 800)
    window.show()
    qtbot.wait(20)

    assert window.grab().isNull() is False
    assert window._form_scroll.horizontalScrollBar().isVisible() is False

    for form, scroll, _base_max_width in window._form_panels:
        assert scroll.maximumWidth() >= form.minimumSizeHint().width() + 24


def test_form_panels_widen_for_large_spanish_forms(qtbot: QtBot) -> None:
    controller = _controller()
    controller.apply(FontSize.LARGE)
    window = MainWindow(
        JsonProjectRepository(),
        None,
        Translator(Language.SPANISH),
        UnitSystem.METRIC,
        preferences=InMemoryPreferencesStore(),
        font_size_controller=controller,
    )
    qtbot.addWidget(window)

    for form, scroll, _base_max_width in window._form_panels:
        assert scroll.maximumWidth() >= form.minimumSizeHint().width() + 24

    assert window._design_panel.minimumWidth() >= window._yagi_form.minimumSizeHint().width()
    assert window._yagi_scroll.maximumWidth() > 520


def test_start_page_title_tracks_the_preset(qtbot: QtBot) -> None:
    controller = _controller()
    controller.apply(FontSize.LARGE)
    page = StartPage(Translator(Language.ENGLISH))
    qtbot.addWidget(page)

    assert page._title.font().pixelSize() == 26

    controller.apply(FontSize.SMALL)
    assert page._title.font().pixelSize() == 20

    controller.apply(FontSize.MEDIUM)
    assert page._title.font().pixelSize() == 22


def test_results_view_plot_fonts_track_the_preset(qtbot: QtBot) -> None:
    controller = _controller()
    controller.apply(FontSize.LARGE)
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.set_result(make_completed_result())

    axis = view._impedance_plot.getAxis("left")
    assert axis.style["tickFont"].pointSizeF() == pytest.approx(10.8)
    assert axis.label.font().pointSizeF() == pytest.approx(10.8)
    assert view._impedance_plot.plotItem.titleLabel.opts["size"] == "13.2pt"
    assert view._impedance_plot.plotItem.legend.opts["labelTextSize"] == "10.8pt"

    controller.apply(FontSize.SMALL)

    assert axis.style["tickFont"].pointSizeF() == pytest.approx(8.1)
    assert axis.label.font().pointSizeF() == pytest.approx(8.1)
    assert view._impedance_plot.plotItem.titleLabel.opts["size"] == "9.9pt"
    assert view._impedance_plot.plotItem.legend.opts["labelTextSize"] == "8.1pt"


def test_comparison_dialog_plot_fonts_track_the_preset(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    controller = _controller()
    controller.apply(FontSize.LARGE)
    dialog = ComparisonDialog(
        Translator(Language.ENGLISH),
        sample_project,
        {},
    )
    qtbot.addWidget(dialog)

    axis = dialog._swr_plot.getAxis("bottom")
    assert axis.style["tickFont"].pointSizeF() == pytest.approx(10.8)

    controller.apply(FontSize.SMALL)
    assert axis.style["tickFont"].pointSizeF() == pytest.approx(8.1)


def test_geometry_view_uses_scaled_fonts(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[float] = []
    original = geometry_module.scaled_font

    def spy(point_size: float, *args: object, **kwargs: object) -> QFont:
        calls.append(point_size)
        return original(point_size, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(geometry_module, "scaled_font", spy)
    view = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(view)
    view.resize(900, 340)
    view.set_model(
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ).to_antenna()
    )

    view.grab()

    assert 10 in calls
    assert 8 in calls


def test_polar_view_uses_scaled_fonts(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[float] = []
    original = polar_module.scaled_font

    def spy(point_size: float, *args: object, **kwargs: object) -> QFont:
        calls.append(point_size)
        return original(point_size, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(polar_module, "scaled_font", spy)
    view = PolarPatternView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.resize(420, 320)

    view.grab()

    assert 9 in calls


def test_3d_pattern_view_uses_scaled_fonts(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[float] = []
    original = pattern_3d_module.scaled_font

    def spy(point_size: float, *args: object, **kwargs: object) -> QFont:
        calls.append(point_size)
        return original(point_size, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(pattern_3d_module, "scaled_font", spy)
    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.resize(640, 420)

    view.grab()

    assert 9 in calls
