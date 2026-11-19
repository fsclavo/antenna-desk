# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Smith-chart widget rendering and export tests."""

from __future__ import annotations

from pathlib import Path

from pytestqt.qtbot import QtBot

from antennadesk.domain.design.smith_chart import smith_locus
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.widgets.smith_chart_view import SmithChartView


def _points():
    return smith_locus(
        [14_000_000.0, 14_100_000.0, 14_200_000.0],
        [complex(50.0, 0.0), complex(75.0, 20.0), complex(30.0, -15.0)],
        50.0,
    )


def test_smith_chart_view_stores_loci_and_exports_images(qtbot: QtBot, tmp_path: Path) -> None:
    view = SmithChartView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.resize(620, 620)
    view.set_data(
        _points(),
        measured=_points(),
        reference_impedance_ohm=50.0,
        plane_label="As simulated",
    )
    view.set_selected_frequency(14_100_000.0)

    assert len(view.simulated_points()) == 3
    assert len(view.measured_points()) == 3

    pixmap = view.grab()
    assert not pixmap.isNull()

    png = tmp_path / "smith.png"
    svg = tmp_path / "smith.svg"
    view.save_image(png)
    view.save_image(svg)

    assert png.stat().st_size > 0
    assert svg.stat().st_size > 0
    assert b"<svg" in svg.read_bytes()


def test_smith_chart_view_empty_state_and_clear(qtbot: QtBot) -> None:
    view = SmithChartView(Translator(Language.SPANISH))
    qtbot.addWidget(view)
    view.resize(400, 400)

    assert view.simulated_points() == ()
    view.clear()
    assert not view.grab().isNull()

    view.set_data(_points(), reference_impedance_ohm=50.0, plane_label="Según simulación")
    assert view.simulated_points()
    view.clear()
    assert view.simulated_points() == ()
