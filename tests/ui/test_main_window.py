# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtWidgets import QDialog, QFileDialog, QInputDialog, QMessageBox
from pytestqt.qtbot import QtBot

from antennadesk.application.ports.antenna_solver import ProgressCallback
from antennadesk.application.ports.cancellation import CancelToken
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem


class FakeSolver:
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="fake",
            supports_frequency_sweep=True,
            supports_currents=True,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )

    def validate(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
    ) -> tuple[Diagnostic, ...]:
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="fake", version="1.0")

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult:
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=7_100_000.0,
                    feed_tag=1,
                    feed_segment=11,
                    impedance_ohm=complex(50.0, 0.0),
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
            duration_s=0.01,
        )


@pytest.fixture
def window(qtbot: QtBot) -> Iterator[MainWindow]:
    main_window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(main_window)
    yield main_window
    main_window._dirty = False
    main_window.close()


def test_default_project_is_ready(window: MainWindow) -> None:
    assert window._project is not None
    assert window._project.name == "40 m dipole"
    parameters = window._form.parameters()
    assert parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert parameters.total_length_m == pytest.approx(20.0)
    assert parameters.height_m == pytest.approx(8.0)
    assert window._geometry._model is not None
    assert window._results._table.rowCount() == 0


def test_simulate_updates_results(window: MainWindow, qtbot: QtBot) -> None:
    window.simulate()
    qtbot.waitUntil(
        lambda: not window._simulating and window._thread is None,
        timeout=5_000,
    )

    assert window._results._table.rowCount() == 1
    assert window._results._table.item(0, 0).text() == "7.100000"
    assert window._status_label.text() == "Simulation completed"
    window._dirty = False


def test_save_project_writes_a_native_file(
    window: MainWindow,
    tmp_path: Path,
) -> None:
    path = tmp_path / "saved.antennadesk"

    assert window._save_to(path) is True

    assert path.is_file()
    assert window._dirty is False


def test_language_switch_updates_actions(window: MainWindow) -> None:
    window._set_language(Language.SPANISH)
    assert window._simulate_action.text() == "Simular"

    window._set_language(Language.ENGLISH)
    assert window._simulate_action.text() == "Simulate"


def test_unit_switch_preserves_physical_length(window: MainWindow) -> None:
    window._set_unit_system(UnitSystem.IMPERIAL)
    assert window._form.parameters().total_length_m == pytest.approx(20.0, abs=0.01)

    window._set_unit_system(UnitSystem.METRIC)
    assert window._form.parameters().total_length_m == pytest.approx(20.0, abs=0.001)


def test_editing_form_marks_project_dirty(window: MainWindow) -> None:
    window._dirty = False
    window._form._length.setValue(window._form._length.value() + 1.0)

    assert window._dirty is True
    window._dirty = False


def test_unit_switch_does_not_mark_project_dirty(window: MainWindow) -> None:
    window._dirty = False
    window._set_unit_system(UnitSystem.IMPERIAL)

    assert window._dirty is False


def test_geometry_view_mode_controls(window: MainWindow) -> None:
    assert window._view_combo.currentData() == "elevation"
    assert window._height_combo.isEnabled() is True

    window._view_combo.setCurrentIndex(1)
    assert window._geometry._mode.value == "plan"
    assert window._height_combo.isEnabled() is False

    window._view_combo.setCurrentIndex(0)
    assert window._geometry._mode.value == "elevation"
    assert window._height_combo.isEnabled() is True


def test_height_exaggeration_control(window: MainWindow) -> None:
    window._height_combo.setCurrentIndex(2)

    assert window._geometry._height_exaggeration == pytest.approx(2.0)


def test_new_variant_switches_to_the_copy(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Second", True))

    window.new_variant()

    assert window._project is not None
    assert len(window._project.designs) == 2
    assert window._variant_combo.count() == 2
    assert window._design_id == window._project.designs[-1].id
    window._dirty = False


def test_rename_variant_updates_the_selector(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Renamed", True))

    window.rename_variant()

    assert window._project is not None
    assert window._project.designs[0].name == "Renamed"
    assert window._variant_combo.itemText(0) == "Renamed"
    window._dirty = False


def test_delete_variant_keeps_one_design(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Second", True))
    window.new_variant()
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    window.delete_variant()

    assert window._project is not None
    assert len(window._project.designs) == 1
    assert window._variant_combo.count() == 1
    window._dirty = False


def test_export_csv_and_html_from_the_current_result(
    window: MainWindow,
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window.simulate()
    qtbot.waitUntil(
        lambda: not window._simulating and window._thread is None,
        timeout=5_000,
    )
    assert window._export_csv_action.isEnabled() is True
    assert window._export_html_action.isEnabled() is True

    csv_path = tmp_path / "result.csv"
    html_path = tmp_path / "report.html"
    paths = iter((str(csv_path), str(html_path)))
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (next(paths), ""),
    )

    window.export_csv()
    window.export_html_report()

    assert csv_path.is_file()
    assert csv_path.read_text(encoding="utf-8").startswith("frequency_hz,")
    assert html_path.is_file()
    assert "<!DOCTYPE html>" in html_path.read_text(encoding="utf-8")
    window._dirty = False


def test_variant_switch_restores_the_cached_result(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window.simulate()
    qtbot.waitUntil(
        lambda: not window._simulating and window._thread is None,
        timeout=5_000,
    )
    assert window._results._table.rowCount() == 1
    assert window._export_csv_action.isEnabled() is True

    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Second", True))
    window.new_variant()

    assert window._results._table.rowCount() == 0
    assert window._export_csv_action.isEnabled() is False

    window._variant_combo.setCurrentIndex(0)

    assert window._results._table.rowCount() == 1
    assert window._export_csv_action.isEnabled() is True
    window._dirty = False


def test_optimize_length_applies_and_simulates(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_length_m(self) -> float:
            return 19.8

    monkeypatch.setattr(
        main_window_module,
        "OptimizationDialog",
        FakeOptimizationDialog,
    )

    assert window._optimize_action.isEnabled() is True
    window.optimize_length()
    qtbot.waitUntil(
        lambda: not window._simulating and window._thread is None,
        timeout=5_000,
    )

    assert window._form.parameters().total_length_m == pytest.approx(19.8)
    assert window._project is not None
    assert window._project.designs[0].parameters.total_length_m == pytest.approx(19.8)
    assert window._results._table.rowCount() == 1
    window._dirty = False


def test_orientation_control_updates_parameters(window: MainWindow) -> None:
    from antennadesk.domain.antennas.dipole import DipoleOrientation

    window._form._orientation.setCurrentIndex(1)
    parameters = window._form.parameters()

    assert parameters.orientation is DipoleOrientation.VERTICAL
    assert window._form._azimuth.isEnabled() is False
    assert window._form._labels()["field.height"].text() == "Base height"

    window._form._orientation.setCurrentIndex(0)
    assert window._form.parameters().orientation is DipoleOrientation.HORIZONTAL
    assert window._form._azimuth.isEnabled() is True
    window._dirty = False
