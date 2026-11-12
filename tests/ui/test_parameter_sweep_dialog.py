# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parameter sweep dialog behavior."""

from __future__ import annotations

from uuid import UUID

from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.projects.project import DesignVariant
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.parameter_sweep_dialog import ParameterSweepDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


class _SweepSolver:
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="analytical",
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
        del model, spec
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="analytical", version="1.0")

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> SimulationResult:
        del progress_callback, cancel_token
        length = model.wires[0].length_m
        resistance = 50.0 + (length - 10.0) * 5.0
        reactance = (length - 10.0) * 10.0
        impedance = complex(resistance, reactance)
        reflection = (impedance - 50.0) / (impedance + 50.0)
        magnitude = abs(reflection)
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=spec.frequency_plan.start_hz,
                    feed_tag=1,
                    feed_segment=1,
                    impedance_ohm=impedance,
                    swr=(1.0 + magnitude) / (1.0 - magnitude),
                    input_power_w=0.001,
                ),
            ),
            duration_s=0.0,
        )


def _dialog(
    qtbot: QtBot,
    *,
    language: Language = Language.ENGLISH,
) -> ParameterSweepDialog:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=10.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    design = DesignVariant(
        id=UUID("00000000-0000-0000-0000-000000000081"),
        name="40 m dipole",
        antenna_type="wire_dipole",
        parameters=parameters,
        antenna=parameters.to_antenna(name="40 m dipole"),
    )
    dialog = ParameterSweepDialog(
        Translator(language),
        UnitSystem.METRIC,
        _SweepSolver(),
        availability.descriptor,
        design,
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
    )
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_shows_the_default_budget(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    assert dialog.windowTitle() == "Parameter sweep"
    assert "11 solver runs" in dialog._budget.text()
    assert dialog._run.isEnabled()
    assert dialog._apply_selected.isEnabled() is False
    assert dialog._apply_best.isEnabled() is False


def test_dialog_runs_a_1d_sweep_and_applies_a_selected_point(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    dialog._start()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=15_000)

    result = dialog.sweep_result()
    assert result is not None
    assert result.completed_count == 11
    assert dialog._table.rowCount() == 11
    assert dialog._apply_best.isEnabled() is True
    dialog._table.setCurrentCell(5, 0)
    assert dialog._apply_selected.isEnabled() is True
    selected = dialog.selected_parameters()
    assert selected is not None
    dialog._apply_best_point()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_dialog_runs_a_2d_sweep_and_selects_a_cell(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    height_index = dialog._y_variable.findData("height_m")
    assert height_index >= 0
    dialog._y_variable.setCurrentIndex(height_index)
    dialog._x_count.setValue(3)
    dialog._y_count.setValue(3)

    dialog._start()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=15_000)

    result = dialog.sweep_result()
    assert result is not None
    assert result.completed_count == 9
    assert dialog._table.rowCount() == 3
    assert dialog._table.columnCount() == 3
    dialog._table.setCurrentCell(1, 1)
    assert dialog._apply_selected.isEnabled() is True
    dialog._apply_selected_point()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_dialog_warns_about_large_budgets_and_rejects_inverted_ranges(
    qtbot: QtBot,
) -> None:
    dialog = _dialog(qtbot)
    height_index = dialog._y_variable.findData("height_m")
    dialog._y_variable.setCurrentIndex(height_index)
    dialog._x_count.setValue(20)
    dialog._y_count.setValue(20)

    assert "Large sweep" in dialog._budget_warning.text()
    dialog._x_min.setValue(5.0)
    dialog._x_max.setValue(4.0)

    assert dialog._run.isEnabled() is False
    assert dialog._validation.isHidden() is False


def test_dialog_retranslates(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot, language=Language.SPANISH)

    assert dialog.windowTitle() == "Barrido de parámetros"
    assert dialog._run.text() == "Ejecutar barrido"
    assert dialog._metric.itemText(0) == "ROE"
    assert dialog._y_variable.itemText(0) == "Ninguna (barrido 1D)"
