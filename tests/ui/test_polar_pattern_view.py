# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Paint-path tests for the polar far-field view."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QSize
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.widgets.polar_pattern_view import PolarPatternView


def _view(qtbot: QtBot) -> PolarPatternView:
    view = PolarPatternView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    return view


def test_polar_view_handles_small_and_empty_paints(qtbot: QtBot) -> None:
    view = _view(qtbot)
    assert view.sizeHint() == QSize(420, 320)

    view.resize(80, 60)
    assert not view.grab().isNull()

    view.resize(420, 320)
    assert not view.grab().isNull()


def test_polar_view_paints_a_closed_mirrored_pattern(qtbot: QtBot) -> None:
    view = _view(qtbot)
    view.resize(420, 320)
    view.set_points(((0.0, 2.0), (30.0, 4.0), (60.0, 1.0), (90.0, -1.0), (180.0, 0.0)))
    view.set_cut(45.0, symbol="θ")
    view.set_mirror(True)
    view.set_closed(True)
    view.set_antenna(30.0)
    view.set_title("Elevation cut")

    assert not view.grab().isNull()


def test_polar_view_paints_an_open_non_mirrored_vertical_pattern(qtbot: QtBot) -> None:
    view = _view(qtbot)
    view.resize(420, 320)
    view.set_points(((0.0, -2.0), (45.0, 1.5), (90.0, 3.0), (135.0, 1.0)))
    view.set_mirror(False)
    view.set_closed(False)
    view.set_antenna(None, vertical=True)

    assert not view.grab().isNull()


def test_polar_view_handles_equal_gains_and_palette_changes(qtbot: QtBot) -> None:
    view = _view(qtbot)
    view.resize(420, 320)
    view.set_points(((0.0, 0.0), (90.0, 0.0), (180.0, 0.0)))
    QApplication.sendEvent(view, QEvent(QEvent.Type.PaletteChange))
    QApplication.sendEvent(view, QEvent(QEvent.Type.EnabledChange))
    view._on_application_font_changed(view.font())

    assert not view.grab().isNull()
