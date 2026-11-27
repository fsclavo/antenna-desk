# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fixtures shared by the main-window test modules."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from main_window_support import FakeSolver, export_nec_deck
from PySide6.QtGui import QFont, QFontInfo, QPalette
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot
from qt_font_support import resolved_test_font

from antennadesk.persistence.container import ProjectContainerRepository
from antennadesk.simulation.preflight import run_preflight
from antennadesk.ui.fonts import current_font_scale, set_current_font_scale
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem

# UX58: the offscreen layout tests share one documented 9-10 pt baseline.
# The fixture normalizes only the test application; production keeps the
# platform font and the user's S/M/L preference.
LAYOUT_BASELINE_MIN_POINT_SIZE = 9.0
LAYOUT_BASELINE_MAX_POINT_SIZE = 10.0


def _pin_layout_baseline_font(app: QApplication) -> None:
    font = QFont(app.font())
    info = QFontInfo(font)
    if not info.family() or info.pointSizeF() <= 0:
        # The Windows offscreen platform can expose an unresolved application
        # font. Resolve a real system family before fixing the point size.
        font = resolved_test_font(LAYOUT_BASELINE_MIN_POINT_SIZE)
        info = QFontInfo(font)
    if not LAYOUT_BASELINE_MIN_POINT_SIZE <= info.pointSizeF() <= LAYOUT_BASELINE_MAX_POINT_SIZE:
        font.setPointSizeF(LAYOUT_BASELINE_MIN_POINT_SIZE)
    app.setFont(font)


@pytest.fixture(autouse=True)
def _restore_application_appearance(qtbot: QtBot) -> Iterator[None]:
    app = QApplication.instance()
    original_font = QFont(app.font()) if isinstance(app, QApplication) else None
    original_palette = QPalette(app.palette()) if isinstance(app, QApplication) else None
    original_style = app.style().name() if isinstance(app, QApplication) else None
    original_scale = current_font_scale()
    if isinstance(app, QApplication):
        _pin_layout_baseline_font(app)
    try:
        yield
    finally:
        if isinstance(app, QApplication):
            if original_style is not None and app.style().name() != original_style:
                app.setStyle(original_style)
            if original_palette is not None:
                app.setPalette(original_palette)
            if original_font is not None:
                app.setFont(original_font)
        set_current_font_scale(original_scale)


@pytest.fixture
def window(qtbot: QtBot, sample_project) -> Iterator[MainWindow]:
    main_window = MainWindow(
        ProjectContainerRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preflight_runner=run_preflight,
        nec_deck_exporter=export_nec_deck,
    )
    qtbot.addWidget(main_window)
    main_window._set_project(
        sample_project,
        sample_project.designs[0].id,
        path=None,
        dirty=False,
    )
    yield main_window
    main_window._dirty = False
    main_window.close()
