# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main-window export actions and file naming."""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import wait_for_condition
from PySide6.QtWidgets import QApplication, QFileDialog
from pytestqt.qtbot import QtBot

from antennadesk.importers.touchstone import parse_touchstone_s1p
from antennadesk.ui import exporters as exporters_module
from antennadesk.ui.main_window import MainWindow

DATA_EXPORTS = (
    ("export_csv", ".csv"),
    ("export_touchstone", ".s1p"),
    ("export_nec_deck", ".nec"),
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
        lambda: not window._simulating and not window._runner.is_running,
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


def test_html_export_passes_the_3d_figure_preference(
    window: MainWindow,
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _simulate(window, qtbot)
    target = tmp_path / "report.html"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(target), ""),
    )
    captured: dict[str, object] = {}

    def fake_write(*args: object, **kwargs: object) -> None:
        captured.update(kwargs)
        target.write_text("ok", encoding="utf-8")

    monkeypatch.setattr(exporters_module, "write_html_report", fake_write)
    window._report_include_3d = False
    window._report_include_band_3d = True

    window.export_html_report()

    assert captured["include_pattern_lobe"] is False
    assert captured["include_band_pattern_lobes"] is True
    window._dirty = False


def test_export_touchstone_writes_a_parseable_one_port_file(
    window: MainWindow,
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _simulate(window, qtbot)
    target = tmp_path / "antenna.s1p"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(target), ""),
    )

    window.export_touchstone()

    assert target.is_file()
    parsed = parse_touchstone_s1p(target.read_text(encoding="utf-8"))
    result = window._simulation_results[window._design_id]
    assert parsed.reference_impedance_ohm == pytest.approx(result.spec.reference_impedance_ohm)
    assert len(parsed.points) == len(result.frequencies)
    assert parsed.points[0].frequency_hz == pytest.approx(result.frequencies[0].frequency_hz)
    window._dirty = False


def test_export_nec_deck_writes_a_deterministic_provenance_deck(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "antenna.nec"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(target), ""),
    )

    window.export_nec_deck()

    text = target.read_text(encoding="utf-8")
    assert text.startswith("CM AntennaDesk NEC-2 export\n")
    assert "CM Project:" in text
    assert "CM Design:" in text
    assert "CM Frequency plan:" in text
    assert "CM Ground:" in text
    assert "CM Segmentation:" in text
    assert "GW " in text
    assert text.rstrip().endswith("EN")
    window._dirty = False


def test_copy_nec_deck_puts_the_same_deck_on_the_clipboard(window: MainWindow) -> None:
    window.copy_nec_deck()

    text = QApplication.clipboard().text()
    assert text.startswith("CM AntennaDesk NEC-2 export\n")
    assert "GW " in text
    assert text.rstrip().endswith("EN")
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


@pytest.mark.parametrize("method_name", ["export_nec_deck", "copy_nec_deck"])
def test_nec_deck_actions_require_a_project(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    method_name: str,
) -> None:
    from main_window_support import FakeSolver

    from antennadesk.persistence.container import ProjectContainerRepository
    from antennadesk.ui.i18n import Language, Translator
    from antennadesk.ui.units import UnitSystem

    window = MainWindow(
        ProjectContainerRepository(),
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


@pytest.mark.parametrize("method_name", [case[0] for case in GEOMETRY_EXPORTS])
def test_geometry_exports_require_a_project(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    method_name: str,
) -> None:
    from main_window_support import FakeSolver

    from antennadesk.persistence.container import ProjectContainerRepository
    from antennadesk.ui.i18n import Language, Translator
    from antennadesk.ui.units import UnitSystem

    window = MainWindow(
        ProjectContainerRepository(),
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
