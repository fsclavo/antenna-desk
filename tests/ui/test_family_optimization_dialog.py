# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from main_window_support import FakeSolver
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.optimization.engine import BudgetProfile
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.family_optimization_dialog import FamilyOptimizationDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.pattern_resolution import far_field_request
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.task_progress import TaskProgressState


def _dialog(**kwargs: object) -> FamilyOptimizationDialog:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    return FamilyOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        FakeSolver(),
        availability.descriptor,
        SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(6.7e6, 7.5e6, 11),
            far_field=far_field_request(5.0, parameters.ground),
        ),
        **kwargs,  # type: ignore[arg-type]
    )


def test_family_dialog_lists_the_family_variables(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    assert dialog._table.rowCount() == 3
    assert dialog._table.item(0, 0).text() == "Total length"
    assert dialog._objective.count() >= 4
    assert dialog._budget.count() == 3


def test_family_dialog_localizes_optimizer_constraints(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    key = "optimize.constraint.director_length_taper"

    assert dialog._localized_error(key) == Translator(Language.ENGLISH).t(key)
    assert dialog._localized_error("solver failed") == "solver failed"


def test_family_dialog_exposes_bounded_parallel_workers(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    assert 1 <= dialog._workers.value() <= 4
    assert "worker" in dialog._workers.toolTip().lower()


def test_family_dialog_runs_and_applies_best(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._budget.setCurrentIndex(dialog._budget.findData(BudgetProfile.FAST.value))

    dialog._start()

    assert dialog._task_progress.isHidden() is False
    assert dialog._task_progress.state is TaskProgressState.RUNNING
    assert dialog._task_progress.progress_maximum == dialog._run_estimated_evaluations

    qtbot.waitUntil(lambda: dialog._thread is None, timeout=15_000)

    assert dialog._task_progress.state is TaskProgressState.COMPLETED
    assert "Completed" in dialog._task_progress.text
    result = dialog.selected_result()
    assert result is not None
    assert result.best_parameters is not None
    assert dialog.selected_parameters() is not None
    assert dialog._apply.isEnabled() is True

    dialog._apply_result()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_family_dialog_reports_estimated_evaluations(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._run_estimated_evaluations = 100
    dialog._last_progress_emit = 0.0
    dialog._task_progress.begin_determinate(100, "optimize.running")

    dialog._on_progress(25, 0.75)

    assert dialog._task_progress.progress_value == 25
    assert "25 / ~100" in dialog._task_progress.text
    assert "0.75" in dialog._task_progress.text


def test_family_dialog_marks_progress_as_cancelling(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._task_progress.begin_determinate(10, "optimize.running")
    dialog._cancel_token = EventCancelToken()

    dialog._cancel_run()

    assert dialog._task_progress.state is TaskProgressState.CANCELLING
    assert dialog._task_progress.text == "Cancelling..."


def test_family_dialog_exposes_quality_modes(qtbot: QtBot) -> None:
    from antennadesk.domain.optimization.summary import OptimizationMode

    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog.show()

    assert dialog._mode.count() == 3
    assert dialog._mode_value() is OptimizationMode.SINGLE
    assert dialog._band_edges.isEnabled() is False
    assert dialog._robust_tolerance.isEnabled() is False

    dialog._mode.setCurrentIndex(dialog._mode.findData(OptimizationMode.BAND_AWARE.value))
    assert dialog._band_edges.isEnabled() is True
    assert dialog._robust_tolerance.isEnabled() is False
    assert "3" in dialog._budget_hint.text()

    dialog._mode.setCurrentIndex(dialog._mode.findData(OptimizationMode.ROBUST.value))
    assert dialog._robust_tolerance.isEnabled() is True
    assert "scenario" in dialog._budget_hint.text()


def test_family_dialog_shows_the_last_persisted_summary(qtbot: QtBot) -> None:
    from datetime import UTC, datetime

    from antennadesk.domain.optimization.summary import (
        OptimizationMode,
        OptimizationSummary,
    )

    summary = OptimizationSummary(
        mode=OptimizationMode.BAND_AWARE,
        objective="min_swr",
        status="converged",
        budget_profile="balanced",
        evaluations=180,
        seed=3,
        best_values={"total_length_m": 20.0},
        best_metrics={"swr": 1.2},
        completed_at=datetime(2026, 11, 7, 12, 0, tzinfo=UTC),
        band_edges_hz=(6.7e6, 7.1e6, 7.5e6),
    )

    dialog = _dialog(last_summary=summary)
    qtbot.addWidget(dialog)

    assert "2026-11-07" in dialog._last_summary_label.text()
    assert "Band-aware" in dialog._last_summary_label.text()
    assert "1.2" in dialog._last_summary_label.text()


def test_family_dialog_runs_band_aware_mode(qtbot: QtBot) -> None:
    from antennadesk.domain.optimization.summary import OptimizationMode

    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._budget.setCurrentIndex(dialog._budget.findData(BudgetProfile.FAST.value))
    dialog._mode.setCurrentIndex(dialog._mode.findData(OptimizationMode.BAND_AWARE.value))

    dialog._start()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=20_000)

    result = dialog.selected_result()
    assert result is not None
    assert result.summary is not None
    assert result.summary.mode is OptimizationMode.BAND_AWARE
    assert result.summary.band_edges_hz == (6.7e6, 7.1e6, 7.5e6)
    assert dialog.selected_parameters() is not None


def test_family_dialog_shows_space_limits(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    assert dialog._max_turning.isHidden() is False
    assert dialog._max_boom.isHidden() is True
    assert dialog._max_turning.minimum() == pytest.approx(0.0)

    from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters

    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    yagi_dialog = FamilyOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        FakeSolver(),
        availability.descriptor,
        SimulationSpec(
            frequency_plan=FrequencyPlan.single(14_100_000.0),
            far_field=far_field_request(5.0, parameters.ground),
        ),
    )
    qtbot.addWidget(yagi_dialog)

    assert yagi_dialog._max_boom.isHidden() is False
    assert yagi_dialog._descriptor.supports_boom_constraint is True


def test_family_dialog_exports_the_evaluation_csv(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    from antennadesk.application.use_cases.optimize_antenna import (
        OptimizeAntennaResult,
    )
    from antennadesk.domain.optimization.engine import (
        CandidateEvaluation,
        OptimizationStatus,
        budget_for,
    )

    dialog = _dialog()
    qtbot.addWidget(dialog)
    evaluation = CandidateEvaluation(
        index=1,
        values={"total_length_m": 20.0},
        score=1.2,
        feasible=True,
        metrics={"swr": 1.2},
    )
    dialog._result = OptimizeAntennaResult(
        status=OptimizationStatus.CONVERGED,
        best_parameters=None,
        best_values={"total_length_m": 20.0},
        best_score=1.2,
        best_metrics={"swr": 1.2},
        evaluations=(evaluation,),
        sensitivity=(),
        budget=budget_for(BudgetProfile.FAST, 3),
        seed=0,
    )
    path = tmp_path / "run.csv"
    monkeypatch.setattr(
        "antennadesk.ui.dialogs.family_optimization_dialog.QFileDialog.getSaveFileName",
        lambda *args, **kwargs: (str(path), ""),
    )

    dialog._export_csv()

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "rank,index,score" in text
    assert "value_total_length_m" in text


def test_family_dialog_locks_installation_context_by_default(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog.show()

    checked = {dialog._variables[row].name for row in dialog._selected_indices()}

    assert checked == {"total_length_m"}
    assert dialog._locked_hint.isVisible() is True
    for row, variable in enumerate(dialog._variables):
        item = dialog._table.item(row, 2)
        assert item is not None
        expected = Qt.CheckState.Unchecked if variable.locked_by_default else Qt.CheckState.Checked
        assert item.checkState() is expected


def test_family_dialog_shows_operating_frequencies_for_the_center_objective(
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.optimization.descriptor import FamilyOptimizationObjective

    dialog = _dialog(operating_frequencies_hz=(7_100_000.0, 14_200_000.0))
    qtbot.addWidget(dialog)
    dialog.show()
    dialog._objective.setCurrentIndex(
        dialog._objective.findData(FamilyOptimizationObjective.MIN_SWR_OPERATING.value)
    )
    dialog._mode.setCurrentIndex(dialog._mode.findData("band_aware"))

    assert dialog._operating_frequencies_label.isVisible() is True
    assert "7.1000 MHz" in dialog._operating_frequencies_label.text()
    assert "14.2000 MHz" in dialog._operating_frequencies_label.text()


def test_family_dialog_multi_seed_defaults_follow_the_budget_profile(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    assert dialog._seed_runs.value() == 1

    dialog._budget.setCurrentIndex(dialog._budget.findData(BudgetProfile.THOROUGH.value))
    assert dialog._seed_runs.value() == 3

    dialog._budget.setCurrentIndex(dialog._budget.findData(BudgetProfile.BALANCED.value))
    assert dialog._seed_runs.value() == 1

    dialog._seed_runs.setValue(4)
    dialog._budget.setCurrentIndex(dialog._budget.findData(BudgetProfile.THOROUGH.value))
    assert dialog._seed_runs.value() == 4


def test_family_dialog_budget_hint_multiplies_by_seed_runs(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._budget.setCurrentIndex(dialog._budget.findData(BudgetProfile.THOROUGH.value))

    assert "3 seeds" in dialog._budget_hint.text()

    dialog._seed_runs.setValue(4)

    assert "4 seeds" in dialog._budget_hint.text()


def test_family_dialog_reports_converged_and_diverged_seed_runs(qtbot: QtBot) -> None:
    from antennadesk.application.use_cases.optimize_antenna import OptimizeAntennaResult
    from antennadesk.domain.optimization.engine import (
        OptimizationStatus,
        budget_for,
    )

    dialog = _dialog()
    qtbot.addWidget(dialog)
    metrics = {
        "seed_requested": 3.0,
        "seed_scored_count": 3.0,
        "seed_score_spread": 0.01,
        "seed_parameter_spread": 0.004,
        "seed_converged": 1.0,
    }
    result = OptimizeAntennaResult(
        status=OptimizationStatus.CONVERGED,
        best_parameters=None,
        best_values=None,
        best_score=1.0,
        best_metrics=metrics,
        evaluations=(),
        sensitivity=(),
        budget=budget_for(BudgetProfile.FAST, 3),
        seed=10,
    )

    text = dialog._verification_text(result)
    assert "3/3" in text
    assert "Winning seed 10" in text

    diverged = OptimizeAntennaResult(
        status=OptimizationStatus.CONVERGED,
        best_parameters=None,
        best_values=None,
        best_score=1.0,
        best_metrics={**metrics, "seed_converged": 0.0, "seed_score_spread": 0.4},
        evaluations=(),
        sensitivity=(),
        budget=budget_for(BudgetProfile.FAST, 3),
        seed=10,
    )

    assert "warning" in dialog._verification_text(diverged).lower()


def test_family_dialog_marks_locked_variables_as_partial(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog.show()

    item = dialog._table.item(0, 2)
    assert item is not None
    item.setCheckState(Qt.CheckState.Unchecked)

    assert dialog._locked_hint.isVisible() is True


def test_family_dialog_shows_the_shortened_endfed_matching_context(
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters
    from antennadesk.domain.optimization.registry import optimizer_availability

    parameters = shortened_efhw_80_10_parameters()
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    dialog = FamilyOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        FakeSolver(),
        availability.descriptor,
        SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(3.5e6, 3.8e6, 11),
            far_field=far_field_request(5.0, parameters.ground),
        ),
    )
    qtbot.addWidget(dialog)

    assert dialog._context_note.isVisibleTo(dialog) is True
    assert "matching capacitor" in dialog._context_note.text()
