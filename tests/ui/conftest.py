# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fixtures shared by the main-window test modules."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from main_window_support import FakeSolver
from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.fonts import current_font_scale, set_current_font_scale
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem


@pytest.fixture(autouse=True)
def _restore_application_appearance(qtbot: QtBot) -> Iterator[None]:
    app = QApplication.instance()
    original_font = QFont(app.font()) if isinstance(app, QApplication) else None
    original_palette = QPalette(app.palette()) if isinstance(app, QApplication) else None
    original_style = app.style().name() if isinstance(app, QApplication) else None
    original_scale = current_font_scale()
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


@pytest.fixture(autouse=True)
def _close_top_level_widgets(qtbot: QtBot) -> Iterator[None]:
    """Close windows before pytest-qt schedules their deletion.

    Pending paint and resize events on a hidden-but-alive window can outlive the
    test and fire while a later test is processing events. On Windows that can
    abort the process inside pyqtgraph. Closing every top-level widget at the end
    of each UI test keeps Qt teardown inside the test that created it.
    """

    yield
    app = QApplication.instance()
    if isinstance(app, QApplication):
        for widget in app.topLevelWidgets():
            if widget.isVisible():
                widget.close()
        app.processEvents()


@pytest.fixture
def window(qtbot: QtBot, sample_project) -> Iterator[MainWindow]:
    main_window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
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
