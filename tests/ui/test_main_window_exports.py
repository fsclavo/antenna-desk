# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main-window export actions and file naming."""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import wait_for_condition
from PySide6.QtWidgets import QFileDialog
from pytestqt.qtbot import QtBot

from antennadesk.ui.main_window import MainWindow

DATA_EXPORTS = (
    ("export_csv", ".csv"),
    ("export_sources_csv", ".csv"),
    ("export_wire_schedule_csv", ".csv"),
    ("export_bom_csv", ".csv"),
    ("export_pattern_csv", ".csv"),
    ("export_html_report", ".html"),
    ("export_pdf_report", ".pdf"),
    ("export_pattern_png", ".png"),
)

GEOMETRY_EXPORTS = (
    ("export_geometry_png", ".png"),
    ("export_geometry_svg", ".svg"),
    ("export_geometry_pdf", ".pdf"),
    ("export_geometry_dxf", ".dxf"),
)


def _simulate(window: MainWindow, qtbot: QtBot) -> None:
    del qtbot
    window.simulate()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )


@pytest.mark.parametrize(("method_name", "suffix"), DATA_EXPORTS)
def test_data_exports_write_the_requested_file(
    window: MainWindow,
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    method_name: str,
    suffix: str,
) -> None:
    _simulate(window, qtbot)
    target = tmp_path / f"export{suffix}"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(target), ""),
    )

    getattr(window, method_name)()

    assert target.is_file()
    assert target.stat().st_size > 0
    window._dirty = False


@pytest.mark.parametrize(("method_name", "suffix"), GEOMETRY_EXPORTS)
def test_geometry_exports_write_the_requested_file(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    method_name: str,
    suffix: str,
) -> None:
    window.resize(1000, 760)
    target = tmp_path / f"geometry{suffix}"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(target), ""),
    )

    getattr(window, method_name)()

    assert target.is_file()
    assert target.stat().st_size > 0


@pytest.mark.parametrize("method_name", [case[0] for case in GEOMETRY_EXPORTS])
def test_geometry_exports_require_a_project(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    method_name: str,
) -> None:
    from main_window_support import FakeSolver

    from antennadesk.persistence.json_repository import JsonProjectRepository
    from antennadesk.ui.i18n import Language, Translator
    from antennadesk.ui.units import UnitSystem

    window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(window)
    errors: list[str] = []
    monkeypatch.setattr(window, "_show_error", errors.append)

    getattr(window, method_name)()

    assert errors == [Translator(Language.ENGLISH).t("error.no_project")]
    window.close()
