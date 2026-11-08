# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from main_window_support import FakeSolver
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.optimization.engine import BudgetProfile
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.family_optimization_dialog import FamilyOptimizationDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.pattern_resolution import far_field_request
from antennadesk.ui.units import UnitSystem


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


def test_family_dialog_runs_and_applies_best(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._budget.setCurrentIndex(dialog._budget.findData(BudgetProfile.FAST.value))

    dialog._start()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=15_000)

    result = dialog.selected_result()
    assert result is not None
    assert result.best_parameters is not None
    assert dialog.selected_parameters() is not None
    assert dialog._apply.isEnabled() is True

    dialog._apply_result()
    assert dialog.result() == QDialog.DialogCode.Accepted


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


def test_family_dialog_marks_locked_variables_as_partial(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog.show()

    item = dialog._table.item(0, 2)
    assert item is not None
    item.setCheckState(Qt.CheckState.Unchecked)

    assert dialog._locked_hint.isVisible() is True
