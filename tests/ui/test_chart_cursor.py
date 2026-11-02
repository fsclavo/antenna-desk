# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtGui import QColor
from pytestqt.qtbot import QtBot

from antennadesk.ui.widgets.chart_cursor import ChartCursor, CursorSeries, nearest_index


def test_nearest_index_handles_sorted_and_empty_data() -> None:
    assert nearest_index((), 1.0) is None
    assert nearest_index((1.0, 2.0, 3.0), 1.6) == 1
    assert nearest_index((3.0, 1.0, 2.0), 1.6) == 2


def test_nearest_index_handles_azimuth_wrap() -> None:
    assert nearest_index((0.0, 120.0, 240.0, 350.0), 351.0, wrap_period=360.0) == 3
    assert nearest_index((0.0, 120.0, 240.0, 350.0), 359.0, wrap_period=360.0) == 0


def test_chart_cursor_shows_nearest_values(qtbot: QtBot) -> None:
    plot = pg.PlotWidget()
    qtbot.addWidget(plot)
    plot.show()
    plot.plot([1.0, 2.0, 3.0], [10.0, 20.0, 30.0])
    cursor = ChartCursor(plot)
    cursor.set_series(
        (
            CursorSeries(
                "R",
                (1.0, 2.0, 3.0),
                (10.0, 20.0, 30.0),
                QColor("#1f5fa8"),
                "Ω",
            ),
        ),
        readout_builder=lambda x, values: f"x={x:.1f} R={values[0][1]:.1f}",
    )

    cursor.show_at_x(2.1)

    assert cursor._line.isVisible() is True
    assert cursor._label.isVisible() is True
    assert cursor._label.text() == "x=2.0 R=20.0"
    assert cursor._dots[0].isVisible() is True

    cursor.hide_cursor()
    assert cursor._line.isVisible() is False
    assert cursor._label.isVisible() is False


def test_chart_cursor_clears_when_series_disappear(qtbot: QtBot) -> None:
    plot = pg.PlotWidget()
    qtbot.addWidget(plot)
    cursor = ChartCursor(plot)
    cursor.set_series(
        (
            CursorSeries(
                "SWR",
                (7.0, 7.1),
                (2.0, 1.5),
                QColor("#2e8b57"),
            ),
        )
    )
    cursor.show_at_x(7.1)
    assert cursor._line.isVisible() is True

    cursor.set_series(())

    assert cursor._line.isVisible() is False
    assert cursor._label.isVisible() is False


def test_unifying_cursor_is_removed_when_plot_is_cleared(qtbot: QtBot) -> None:
    plot = pg.PlotWidget()
    qtbot.addWidget(plot)
    cursor = ChartCursor(plot)
    series = (CursorSeries("R", (1.0, 2.0), (10.0, 20.0), QColor("#1f5fa8")),)
    cursor.set_series(series)
    cursor.show_at_x(1.0)
    plot.clear()

    cursor.set_series(series)
    cursor.show_at_x(2.0)

    assert cursor._line.scene() is not None
    assert cursor._label.text()
