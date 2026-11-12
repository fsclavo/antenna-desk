# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Simulation, results, sweep, pattern, and band-analysis wiring."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest
from helpers import wait_for_condition
from main_window_support import FakeSolver, use_parameters
from PySide6.QtWidgets import QDialog, QFileDialog, QInputDialog, QMessageBox
from pytestqt.qtbot import QtBot

from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.task_progress import TaskProgressState


class _BlockingSolver(FakeSolver):
    """Keep a worker busy until the test releases it."""

    def __init__(self) -> None:
        self.entered = threading.Event()
        self.release = threading.Event()

    def run(
        self,
        model: object,
        spec: object,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> object:
        self.entered.set()
        self.release.wait(timeout=10.0)
        return super().run(
            model,  # type: ignore[arg-type]
            spec,  # type: ignore[arg-type]
            progress_callback=progress_callback,  # type: ignore[arg-type]
            cancel_token=cancel_token,  # type: ignore[arg-type]
        )


class _FailingSolver(FakeSolver):
    def run(
        self,
        model: object,
        spec: object,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> object:
        del model, spec, progress_callback, cancel_token
        raise RuntimeError("boom")


def test_simulate_shows_indeterminate_progress_then_resets(window: MainWindow) -> None:
    solver = _BlockingSolver()
    window._solver = solver
    try:
        window.simulate()
        assert solver.entered.wait(2.0)
        wait_for_condition(
            lambda: window._task_progress.state is TaskProgressState.RUNNING,
            timeout_ms=2_000,
        )
        assert window._task_progress.isHidden() is False
        assert window._task_progress.is_indeterminate is True
        wait_for_condition(
            lambda: "Running NEC-2" in window._task_progress.text,
            timeout_ms=2_000,
        )
        window._progress_started_at = time.monotonic() - 5
        window._update_progress_elapsed()
        assert "5 s" in window._task_progress.text
    finally:
        solver.release.set()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=5_000,
    )
    assert window._task_progress.isHidden() is True
    window._dirty = False


def test_cancel_simulation_marks_progress_cancelling(window: MainWindow) -> None:
    solver = _BlockingSolver()
    window._solver = solver
    try:
        window.simulate()
        assert solver.entered.wait(2.0)
        wait_for_condition(
            lambda: window._task_progress.state is TaskProgressState.RUNNING,
            timeout_ms=2_000,
        )
        window.cancel_simulation()
        assert window._task_progress.state is TaskProgressState.CANCELLING
        assert window._task_progress.text == "Cancelling..."
        assert window._progress_timer.isActive() is False
    finally:
        solver.release.set()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=5_000,
    )
    assert window._task_progress.isHidden() is True
    window._dirty = False


def test_simulation_failure_resets_progress(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    errors: list[str] = []
    monkeypatch.setattr(window, "_show_error", errors.append)
    window._solver = _FailingSolver()

    window.simulate()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=5_000,
    )

    assert window._task_progress.isHidden() is True
    assert errors
    assert "boom" in errors[-1]
    window._dirty = False


def test_band_analysis_shows_a_determinate_progress_bar(window: MainWindow) -> None:
    from antennadesk.domain.design.band_plan import BandPlan, BandSelection
    from antennadesk.domain.simulation.bands import amateur_band_by_id

    bands = [
        amateur_band_by_id("40m"),
        amateur_band_by_id("20m"),
    ]
    assert all(band is not None for band in bands)
    plan = BandPlan(tuple(BandSelection(band, points=3) for band in bands if band is not None))
    assert window._project is not None
    design = window._project.designs[0]
    solver = _BlockingSolver()
    window._solver = solver
    try:
        window._start_band_analysis(design, plan)
        assert window._task_progress.isHidden() is False
        assert window._task_progress.progress_maximum == 2
        assert window._task_progress.progress_value == 0
        assert window._task_progress.state is TaskProgressState.RUNNING
        assert window._status_label.text() == "Analyzing bands..."
        assert solver.entered.wait(2.0)
    finally:
        solver.release.set()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=5_000,
    )
    assert window._task_progress.isHidden() is True
    window._dirty = False


def test_band_progress_updates_the_bar_text(window: MainWindow) -> None:
    window._task_progress.begin_determinate(4, "progress.analyzing_bands")

    window._on_band_analysis_progress(2, 4, "20m")

    assert window._task_progress.progress_maximum == 4
    assert window._task_progress.progress_value == 2
    assert window._task_progress.text.startswith("Band 2/4: 20m")
    assert window._task_progress.state is TaskProgressState.RUNNING
    window._task_progress.reset()


def test_project_matching_network_overrides_shortened_endfed(window: MainWindow) -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters
    from antennadesk.domain.antennas.matching_network import LNetwork
    from antennadesk.domain.simulation.frequency import FrequencyPlan

    parameters = shortened_efhw_80_10_parameters()
    project = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    base = SimulationSpec(frequency_plan=FrequencyPlan.single(parameters.frequency_hz))
    window._matching_network = project

    spec = window._with_project_chain(parameters, base)

    assert spec.matching_network is project
    assert spec.matching_network_override is True

    window._matching_network = None
    spec = window._with_project_chain(parameters, base)

    assert spec.matching_network is not None
    assert spec.matching_network_override is False
    window._dirty = False


def test_feed_matching_summary_reflects_the_project_override(window: MainWindow) -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters
    from antennadesk.domain.antennas.matching_network import LNetwork

    use_parameters(window, shortened_efhw_80_10_parameters())
    window._matching_network = LNetwork(
        series_inductance_h=1e-6,
        shunt_capacitance_f=100e-12,
    )
    window._refresh_feed_matching_summary()

    assert window._feed_matching_summary._warning_container.isHidden() is False
    assert "retained, not applied" in window._feed_matching_summary._endfed_value.text()
    assert "active" in window._feed_matching_summary._project_value.text()

    window._set_language(Language.SPANISH)

    assert "retenida, no aplicada" in window._feed_matching_summary._endfed_value.text()
    assert "reemplaza" in window._feed_matching_summary._warning.text()

    window._set_language(Language.ENGLISH)
    window._dirty = False


def test_remove_project_matching_network_restores_the_internal_network(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters
    from antennadesk.domain.antennas.matching_network import LNetwork

    use_parameters(window, shortened_efhw_80_10_parameters())
    network = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    window._matching_network = network
    assert window._project is not None
    window._project = window._project.with_matching_network(
        network,
        updated_at=window._project.updated_at,
    )
    window._refresh_feed_matching_summary()
    monkeypatch.setattr(
        main_window_module.QMessageBox,
        "question",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.Yes,
    )

    window.remove_matching_network()

    assert window._matching_network is None
    assert window._project.matching_network is None
    assert window._feed_matching_summary._warning_container.isHidden() is True
    assert "(active)" in window._feed_matching_summary._endfed_value.text()
    window._dirty = False


def test_simulate_updates_results(window: MainWindow, qtbot: QtBot) -> None:
    window.simulate()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )

    assert window._results._table.rowCount() == 1
    assert window._results._table.item(0, 0).text() == "7.100000"
    assert window._status_label.text() == "Simulation completed"
    window._dirty = False


def test_solver_timeout_defaults_to_180_and_accepts_an_override(
    window: MainWindow,
) -> None:
    assert window._solver_timeout.value() == 180
    assert window._project is not None

    design = window._project.designs[0]
    assert window._base_simulation_spec(design).timeout_s == 180.0

    window._solver_timeout.setValue(240)
    assert window._base_simulation_spec(design).timeout_s == 240.0


def test_simulate_saves_the_form_before_running(
    window: MainWindow,
    qtbot: QtBot,
) -> None:
    window._form._length.setValue(22.0)

    window.simulate()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )

    assert window._project is not None
    design = window._project.designs[0]
    assert design.parameters.total_length_m == pytest.approx(22.0)
    assert window._results._table.rowCount() == 1
    window._dirty = False


def test_export_csv_and_html_from_the_current_result(
    window: MainWindow,
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window.simulate()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )
    assert window._export_csv_action.isEnabled() is True
    assert window._export_sources_csv_action.isEnabled() is False
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


def test_simulation_results_persist_across_save_and_open(
    window: MainWindow,
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    from antennadesk.application.use_cases.open_project import OpenProject

    window.simulate()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
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
    window._form.set_antenna_type("loop")
    window._form._length.setValue(20.0)
    window._form._sides.setValue(16)
    spec = window._form.simulation_spec()
    overrides = dict(spec.segmentation.wire_segments)

    assert len(overrides) == 16
    assert all(segments >= 3 for segments in overrides.values())
    assert overrides["loop-0"] % 2 == 1
    window._dirty = False


def test_dense_sweep_keeps_all_points_and_uses_band_snapshots(
    window: MainWindow,
) -> None:
    from antennadesk.domain.antennas.g5rv import g5rv_parameters
    from antennadesk.domain.environment.ground import GroundModel
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.segmentation import SegmentationPolicy
    from antennadesk.ui.pattern_resolution import far_field_request

    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    parameters = g5rv_parameters(frequency_hz=14_100_000.0, ground=ground)
    model = parameters.to_antenna()
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 200),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=far_field_request(5.0, ground),
    )

    fitted = window._fit_spec_to_budget(model, spec)

    assert fitted.frequency_plan.count == 200
    assert len(fitted.pattern_frequencies_hz) == 9
    assert fitted.far_field.theta_count == 91
    assert fitted.far_field.phi_count == 361
    assert "1°" in window._custom_pattern_status.text()
    assert "9 pattern frequencies" in window._custom_pattern_status.text()


def test_pattern_settings_apply_to_generated_designs(
    window: MainWindow,
) -> None:
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.segmentation import SegmentationPolicy
    from antennadesk.ui.pattern_resolution import far_field_request

    assert window._project is not None
    assert window._pattern_group.isHidden() is False
    model = window._project.designs[0].antenna
    window._custom_pattern_frequency_mode.setCurrentIndex(
        window._custom_pattern_frequency_mode.findData(13)
    )
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6_700_000.0, 7_500_000.0, 31),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=far_field_request(5.0, model.environment.ground),
    )

    fitted = window._fit_spec_to_budget(model, spec)

    assert len(fitted.pattern_frequencies_hz) == 13
    assert fitted.far_field.theta_count == 46
    assert fitted.far_field.phi_count == 181
    assert "13 pattern frequencies" in window._custom_pattern_status.text()


def test_vertical_spec_uses_performance_safe_defaults(window: MainWindow) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters
    from antennadesk.domain.environment.ground import GroundModel

    parameters = VerticalParameters(
        frequency_hz=146_000_000.0,
        height_m=2.0,
        base_height_m=0.25,
        radial_count=16,
        radial_length_m=5.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )

    spec = window._vertical_simulation_spec(parameters)
    model = parameters.to_antenna()
    segments = sum(
        spec.segmentation.segments_for(wire, parameters.frequency_hz * 1.05) for wire in model.wires
    )

    assert spec.frequency_plan.count == 31
    assert spec.segmentation.target_segment_length_wavelengths == pytest.approx(0.05)
    assert segments == 855


def test_endfed_simulation_spec_carries_transformer_and_counterpoise(
    window: MainWindow,
) -> None:
    from antennadesk.domain.antennas.endfed import EndFedParameters

    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=10.0,
        transformer_ratio=49.0,
        counterpoise_length_m=2.0,
        counterpoise_height_m=0.2,
    )

    spec = window._endfed_simulation_spec(parameters)

    assert spec.feed_transformer_ratio == pytest.approx(49.0)
    assert len(parameters.to_antenna().wires) == 3


def test_shortened_endfed_simulation_spec_carries_the_coil(
    window: MainWindow,
) -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters

    parameters = shortened_efhw_80_10_parameters()
    spec = window._endfed_simulation_spec(parameters)
    model = parameters.to_antenna()

    assert spec.feed_transformer_ratio == pytest.approx(49.0)
    assert spec.matching_network is not None
    assert [load.id for load in model.loads] == ["endfed-loading-coil"]
    assert model.loads[0].wire_id == "endfed-loading-coil-section"
    assert model.loads[0].offset_m == pytest.approx(0.05)


def test_fit_spec_to_budget_uses_the_finest_pattern_that_fits(window: MainWindow) -> None:
    from antennadesk.domain.antennas.dipole import DipoleParameters
    from antennadesk.domain.environment.ground import GroundModel
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.segmentation import SegmentationPolicy
    from antennadesk.ui.pattern_resolution import far_field_request

    ground = GroundModel.finite(relative_permittivity=13.0, conductivity_s_per_m=0.005)
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        ground=ground,
    )
    model = parameters.to_antenna()
    wide = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6_700_000.0, 7_500_000.0, 31),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=far_field_request(1.0, ground),
    )

    fitted = window._fit_spec_to_budget(model, wide)

    assert len(fitted.pattern_frequencies_hz) == 5
    assert fitted.far_field.theta_count == 91
    assert fitted.far_field.phi_count == 361
    assert window._pending_pattern_diagnostic is None

    window._custom_run_pattern_step_deg = 2.0
    single = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=far_field_request(2.0, ground),
    )
    kept = window._fit_spec_to_budget(model, single)

    assert kept.far_field.theta_count == 46
    assert kept.far_field.phi_count == 181
    assert window._pending_pattern_diagnostic is None


def test_analyze_bands_runs_the_selected_band_set(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.design.band_plan import BandPlan, BandSelection
    from antennadesk.domain.simulation.bands import amateur_band_by_id

    selected = tuple(
        BandSelection(amateur_band_by_id(band_id), points=5)
        for band_id in ("40m", "20m", "10m")
        if amateur_band_by_id(band_id) is not None
    )
    plan = BandPlan(selected)

    class FakeBandDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def plan(self) -> BandPlan:
            return plan

        def workers(self) -> int:
            return 2

    monkeypatch.setattr(main_window_module, "BandAnalysisDialog", FakeBandDialog)

    window.analyze_bands()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=5_000,
    )

    assert window._project is not None
    assert window._design_id is not None
    analysis = window._band_analysis_results[window._design_id]
    assert [band.band.name for band in analysis.bands] == ["40m", "20m", "10m"]
    assert window._results._bands_tab_index >= 0
    assert window._results._bands_table.rowCount() == 3
    assert all(len(band.result.spec.pattern_frequencies_hz) == 5 for band in analysis.bands)
    assert all(band.result.spec.timeout_s == 180.0 for band in analysis.bands)
    band_runs = [run for run in window._project.simulation_runs if run.band_id is not None]
    assert {run.band_id for run in band_runs} == {"40m", "20m", "10m"}
    assert len({run.batch_id for run in band_runs}) == 1

    window._results._bands_table.selectRow(1)
    wait_for_condition(
        lambda: window._selected_band_ids.get(window._design_id) == "20m",
        timeout_ms=1_000,
    )
    window._dirty = False


def test_band_analysis_respects_the_pattern_frequency_count(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.design.band_plan import BandPlan, BandSelection
    from antennadesk.domain.simulation.bands import amateur_band_by_id

    band = amateur_band_by_id("40m")
    assert band is not None
    plan = BandPlan((BandSelection(band, points=15),))

    class FakeBandDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def plan(self) -> BandPlan:
            return plan

        def workers(self) -> int:
            return 1

    monkeypatch.setattr(main_window_module, "BandAnalysisDialog", FakeBandDialog)
    window._custom_pattern_frequency_mode.setCurrentIndex(
        window._custom_pattern_frequency_mode.findData(9)
    )

    window.analyze_bands()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=5_000,
    )

    assert window._design_id is not None
    analysis = window._band_analysis_results[window._design_id]
    assert len(analysis.bands[0].result.spec.pattern_frequencies_hz) == 9
    window._dirty = False


def test_band_analysis_reopens_from_a_saved_project(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from antennadesk.domain.design.band_plan import BandPlan, BandSelection
    from antennadesk.domain.simulation.bands import amateur_band_by_id

    plan = BandPlan(
        tuple(
            BandSelection(amateur_band_by_id(band_id), points=5)
            for band_id in ("40m", "20m")
            if amateur_band_by_id(band_id) is not None
        )
    )

    class FakeBandDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def plan(self) -> BandPlan:
            return plan

        def workers(self) -> int:
            return 1

    monkeypatch.setattr(main_window_module, "BandAnalysisDialog", FakeBandDialog)
    window.analyze_bands()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=5_000,
    )
    path = tmp_path / "bands.antennadesk"
    assert window._save_to(path) is True

    loaded = JsonProjectRepository().load(path)
    second = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(second)
    second._set_project(
        loaded,
        loaded.designs[0].id,
        path=path,
        dirty=False,
    )

    assert second._design_id is not None
    assert second._project is not None
    assert second._project.designs[0].band_plan == plan
    analysis = second._band_analysis_results[second._design_id]
    assert [band.band.name for band in analysis.bands] == ["40m", "20m"]
    assert second._results._bands_tab_index >= 0
    assert second._results._bands_table.rowCount() == 2
    second._dirty = False
    second.close()
    window._dirty = False


def test_band_analysis_controls_are_centralized(window: MainWindow) -> None:
    assert window._band_group.title() == "Band analysis"
    assert window._analyze_bands_button.text() == "Analyze Bands..."
    assert window._analyze_bands_action.text() == "Analyze Bands..."
    assert window._analyze_bands_action.shortcut().toString() == "Ctrl+Shift+B"
    assert window._band_plan_label.text().startswith("Bands: 40m")


def test_simulation_controls_are_grouped_in_the_simulation_tab(window: MainWindow) -> None:
    assert window._sidebar_tabs.tabText(window._simulation_tab_index) == "Simulation"
    assert window._sidebar_tabs.currentWidget() is window._design_tab
    assert window._advanced_body.isAncestorOf(window._sweep_group) is True
    assert window._advanced_body.isAncestorOf(window._pattern_group) is True
    assert window._advanced_body.isAncestorOf(window._band_group) is True

    window._sidebar_tabs.setCurrentWidget(window._simulation_tab)

    assert window._sidebar_tabs.currentWidget() is window._simulation_tab


def test_custom_sweep_overrides_a_generated_template(
    window: MainWindow,
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.antennas.endfed import EndFedParameters

    use_parameters(
        window,
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.444,
            feed_height_m=6.0,
            end_height_m=6.0,
        ),
    )
    assert window._sweep_mode.currentData() is None
    assert window._sweep_start.isEnabled() is False

    window._sweep_mode.setCurrentIndex(window._sweep_mode.findData("custom"))
    window._sweep_start.setValue(7.0)
    window._sweep_stop.setValue(7.3)
    window._sweep_points.setValue(11)

    assert window._sweep_start.isEnabled() is True
    window.simulate()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )

    assert window._last_result is not None
    plan = window._last_result.spec.frequency_plan
    assert plan.start_hz == pytest.approx(7_000_000.0)
    assert plan.stop_hz == pytest.approx(7_300_000.0)
    assert plan.count == 11
    window._dirty = False


def test_ocfd_and_custom_specs_include_the_transformer_ratio(window: MainWindow) -> None:
    from antennadesk.domain.antennas.ocfd import OCFDParameters

    parameters = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.4,
        height_m=10.0,
        transformer_ratio=4.0,
    )

    ocfd_spec = window._ocfd_simulation_spec(parameters)
    custom_spec = window._custom_simulation_spec(parameters.to_custom_parameters())

    assert ocfd_spec.feed_transformer_ratio == pytest.approx(4.0)
    assert custom_spec.feed_transformer_ratio == pytest.approx(4.0)


def test_fan_dipole_simulate_covers_all_element_bands(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement

    parameters = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(
            FanElement(length_m=20.0, included_angle_deg=120.0),
            FanElement(length_m=5.0, included_angle_deg=100.0),
        ),
        apex_height_m=10.0,
    )

    class FakeFanDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> FanDipoleParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "FanDipoleDialog", FakeFanDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Fan", True))
    window.new_fan_dipole_antenna()

    window.simulate()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=5_000,
    )

    assert window._design_id is not None
    analysis = window._band_analysis_results[window._design_id]
    assert [band.band.name for band in analysis.bands] == ["40m", "10m"]
    assert window._results._bands_tab_index >= 0
    window._dirty = False
