# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fixtures shared by the main-window test modules."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from main_window_support import FakeSolver
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.fonts import current_font_scale, set_current_font_scale
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem


@pytest.fixture(autouse=True)
def _restore_application_font(qtbot: QtBot) -> Iterator[None]:
    app = QApplication.instance()
    original = QFont(app.font()) if isinstance(app, QApplication) else None
    original_scale = current_font_scale()
    try:
        yield
    finally:
        if isinstance(app, QApplication) and original is not None:
            app.setFont(original)
        set_current_font_scale(original_scale)


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
