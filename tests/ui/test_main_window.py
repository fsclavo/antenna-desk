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

        def selected_dimension_m(self) -> float:
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


def test_simulation_results_persist_across_save_and_open(
    window: MainWindow,
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    from antennadesk.application.use_cases.open_project import OpenProject

    window.simulate()
    qtbot.waitUntil(
        lambda: not window._simulating and window._thread is None,
        timeout=5_000,
    )
    assert window._project is not None
    assert len(window._project.simulation_runs) == 1

    path = tmp_path / "with-result.antennadesk"
    assert window._save_to(path) is True
    assert window._results._table.rowCount() == 1

    loaded = OpenProject(JsonProjectRepository()).execute(path)
    reopened = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(reopened)
    reopened._set_project(
        loaded,
        loaded.designs[0].id,
        path=path,
        dirty=False,
    )

    assert reopened._results._table.rowCount() == 1
    assert reopened._export_csv_action.isEnabled() is True
    window._dirty = False
    reopened._dirty = False


def test_switching_to_a_folded_dipole_updates_the_design_and_view(
    window: MainWindow,
) -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    window._form._type.setCurrentIndex(1)
    assert window._form.parameters().spacing_m > 0.0
    window._form._length.setValue(20.0)
    window._form._spacing.setValue(0.2)
    window.apply_design()

    assert window._project is not None
    parameters = window._project.designs[0].parameters
    assert isinstance(parameters, FoldedDipoleParameters)
    assert parameters.spacing_m == pytest.approx(0.2, abs=1e-6)
    assert len(window._project.designs[0].antenna.wires) == 4
    assert window._view_combo.currentData() == "plan"
    assert window._geometry._mode.value == "plan"
    assert window._optimize_action.isEnabled() is True
    window._dirty = False


def test_switching_to_a_loop_updates_the_design(window: MainWindow) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    window._form._type.setCurrentIndex(2)
    window._form._length.setValue(40.0)
    window._form._sides.setValue(8)
    window.apply_design()

    assert window._project is not None
    parameters = window._project.designs[0].parameters
    assert isinstance(parameters, LoopParameters)
    assert parameters.sides == 8
    assert len(window._project.designs[0].antenna.wires) == 8
    assert window._view_combo.currentData() == "plan"
    assert window._form._sides.isHidden() is False
    assert window._form._spacing.isHidden() is True
    window._dirty = False


def test_new_antenna_uses_the_current_antenna_type(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeWizard:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.update(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Rejected

    monkeypatch.setattr(main_window_module, "DipoleWizard", FakeWizard)
    window._form._type.setCurrentIndex(2)
    window._dirty = False

    window.new_antenna()

    assert captured["initial_antenna_type"] == "loop"
    assert window._new_action.text() == "New Antenna..."


def test_new_dipole_alias_still_opens_the_wizard(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[bool] = []

    def fake_new_antenna() -> None:
        called.append(True)

    monkeypatch.setattr(window, "new_antenna", fake_new_antenna)
    window.new_dipole()

    assert called == [True]


def test_optimize_loop_applies_circumference_and_simulates(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    class FakeOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_dimension_m(self) -> float:
            return 41.2

    monkeypatch.setattr(
        main_window_module,
        "OptimizationDialog",
        FakeOptimizationDialog,
    )
    window._form._type.setCurrentIndex(2)
    window._form._length.setValue(40.0)
    window._form._sides.setValue(4)
    window.apply_design()
    assert window._optimize_action.isEnabled() is True

    window.optimize_length()
    qtbot.waitUntil(
        lambda: not window._simulating and window._thread is None,
        timeout=5_000,
    )

    assert window._project is not None
    parameters = window._project.designs[0].parameters
    assert isinstance(parameters, LoopParameters)
    assert parameters.circumference_m == pytest.approx(41.2, abs=1e-6)
    assert window._results._table.rowCount() == 1
    window._dirty = False


def test_zoom_control_scales_the_geometry_view(window: MainWindow) -> None:
    assert window._geometry._zoom == pytest.approx(1.0)
    index = window._zoom_combo.findData(2.0)
    window._zoom_combo.setCurrentIndex(index)

    assert window._geometry._zoom == pytest.approx(2.0)

    index = window._zoom_combo.findData(1.0)
    window._zoom_combo.setCurrentIndex(index)
    assert window._geometry._zoom == pytest.approx(1.0)


def test_simulation_spec_uses_feed_aligned_per_wire_segmentation(
    window: MainWindow,
) -> None:
    spec = window._form.simulation_spec()
    overrides = dict(spec.segmentation.wire_segments)

    assert overrides["radiator"] % 2 == 1
    assert spec.segmentation.segments_per_wire is None


def test_loop_simulation_spec_has_connector_and_feed_overrides(
    window: MainWindow,
) -> None:
    window._form._type.setCurrentIndex(2)
    window._form._length.setValue(20.0)
    window._form._sides.setValue(16)
    spec = window._form.simulation_spec()
    overrides = dict(spec.segmentation.wire_segments)

    assert len(overrides) == 16
    assert all(segments >= 3 for segments in overrides.values())
    assert overrides["loop-0"] % 2 == 1
    window._dirty = False


def test_compacting_simulation_history_keeps_the_latest_run(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window.simulate()
    qtbot.waitUntil(lambda: not window._simulating and window._thread is None, timeout=5_000)
    window.simulate()
    qtbot.waitUntil(lambda: not window._simulating and window._thread is None, timeout=5_000)
    assert window._project is not None
    assert len(window._project.simulation_runs) == 2
    assert window._compact_history_action.isEnabled() is True

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    window.compact_simulation_history()

    assert len(window._project.simulation_runs) == 1
    assert window._dirty is True
    assert window._status_label.text() == "Simulation history compacted."
    window._dirty = False


def test_save_warns_and_can_cancel_a_large_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "large.antennadesk"
    monkeypatch.setattr(
        window._repository,
        "serialized_size",
        lambda project: 9 * 1024 * 1024,
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel,
    )

    assert window._save_to(path) is False
    assert path.exists() is False
    window._dirty = False


def test_edit_loads_applies_series_loads(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.load import SeriesLoad

    load = SeriesLoad("load-1", "radiator", 10.0, resistance_ohm=50.0)

    class FakeLoadsDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def loads(self) -> tuple[SeriesLoad, ...]:
            return (load,)

    monkeypatch.setattr(main_window_module, "LoadsDialog", FakeLoadsDialog)
    window.edit_loads()

    assert window._project is not None
    assert window._project.designs[0].antenna.loads == (load,)
    assert window._dirty is True
    window._dirty = False


def test_geometry_view_has_a_3d_option(window: MainWindow) -> None:
    assert window._view_combo.count() == 3
    assert window._view_combo.itemData(2) == "3d"


def test_new_custom_antenna_is_editable_and_simulatable(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.custom import CustomAntennaParameters
    from antennadesk.domain.antennas.feed import FeedPoint
    from antennadesk.domain.antennas.geometry import Point3D
    from antennadesk.domain.antennas.materials import COPPER
    from antennadesk.domain.antennas.wire import Wire

    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                id="wire-1",
                start=Point3D(-5.0, 0.0, 8.0),
                end=Point3D(5.0, 0.0, 8.0),
                radius_m=0.001,
                material=COPPER,
            ),
        ),
        feed=FeedPoint("wire-1", 5.0),
    )

    class FakeCustomDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> CustomAntennaParameters:
            return parameters

        def pattern_step_deg(self) -> float:
            return 10.0

    monkeypatch.setattr(main_window_module, "CustomAntennaDialog", FakeCustomDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Custom", True))

    window.new_custom_antenna()

    assert window._project is not None
    assert window._project.name == "Custom"
    assert window._project.designs[0].antenna_type == "custom"
    assert window._design_stack.currentWidget() is window._custom_panel

    window.simulate()
    qtbot.waitUntil(lambda: not window._simulating and window._thread is None, timeout=5_000)

    assert window._results._table.rowCount() == 1
    assert window._status_label.text() == "Simulation completed"
    window._dirty = False


def test_import_nec_deck_creates_a_custom_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "imported.nec"
    path.write_text(
        "GW 1 5 -5 0 8 5 0 8 0.001\nGN 0 0 0 0 13 0.005\nFR 0 1 0 0 7.1 0\nEX 0 1 3 0 1\nEN\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(path), ""),
    )

    window.import_nec_deck()

    assert window._project is not None
    assert window._project.name == "imported"
    assert window._project.designs[0].antenna_type == "custom"
    assert len(window._project.designs[0].antenna.wires) == 1
    assert window._design_stack.currentWidget() is window._custom_panel
    window._dirty = False


def test_import_mmana_file_creates_a_custom_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "imported.maa"
    path.write_text(
        "Test\n*\n7.1\n***Wires***\n1\n-5,0,8,5,0,8,0.001,-1\n*** Source ***\n1,1\nw1c,0,1\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(path), ""),
    )
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: None)

    window.import_mmana_file()

    assert window._project is not None
    assert window._project.name == "imported"
    assert window._project.designs[0].antenna_type == "custom"
    assert len(window._project.designs[0].antenna.wires) == 1
    window._dirty = False


def test_convert_to_custom_wires_preserves_geometry(window: MainWindow) -> None:
    original = window._project.designs[0].antenna if window._project is not None else None
    assert original is not None

    window.convert_to_custom_wires()

    assert window._project is not None
    design = window._project.designs[0]
    assert design.antenna_type == "custom"
    assert design.antenna.wires == original.wires
    assert design.antenna.feed == original.feed
    assert window._design_stack.currentWidget() is window._custom_panel
    assert window._optimize_action.isEnabled() is False
    window._dirty = False


def test_new_yagi_creates_an_editable_custom_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.custom import CustomAntennaParameters
    from antennadesk.domain.antennas.feed import FeedPoint
    from antennadesk.domain.antennas.geometry import Point3D
    from antennadesk.domain.antennas.materials import COPPER
    from antennadesk.domain.antennas.wire import Wire

    parameters = CustomAntennaParameters(
        frequency_hz=14_100_000.0,
        wires=(
            Wire(
                id="element-1",
                start=Point3D(0.0, -5.0, 12.0),
                end=Point3D(0.0, 5.0, 12.0),
                radius_m=0.001,
                material=COPPER,
            ),
            Wire(
                id="element-2",
                start=Point3D(2.0, -5.0, 12.0),
                end=Point3D(2.0, 5.0, 12.0),
                radius_m=0.001,
                material=COPPER,
            ),
        ),
        feed=FeedPoint("element-2", 5.0),
    )

    class FakeYagiDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> CustomAntennaParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "YagiDialog", FakeYagiDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Yagi", True))

    window.new_yagi_antenna()

    assert window._project is not None
    assert window._project.name == "Yagi"
    assert window._project.designs[0].antenna_type == "custom"
    assert window._project.designs[0].antenna.wires == parameters.wires
    window._dirty = False
