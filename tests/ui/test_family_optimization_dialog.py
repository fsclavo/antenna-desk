# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

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


def _dialog() -> FamilyOptimizationDialog:
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
    )


def test_family_dialog_lists_the_family_variables(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    assert dialog._table.rowCount() == 3
    assert dialog._table.item(0, 0).text() == "Total length"
    assert dialog._objective.count() >= 4
    assert dialog._budget.count() == 3


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


def test_family_dialog_marks_locked_variables_as_partial(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog.show()

    item = dialog._table.item(0, 2)
    assert item is not None
    item.setCheckState(Qt.CheckState.Unchecked)

    assert dialog._locked_hint.isVisible() is True
