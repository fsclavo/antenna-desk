# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fixtures shared by the main-window test modules."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from main_window_support import FakeSolver
from pytestqt.qtbot import QtBot

from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem


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
