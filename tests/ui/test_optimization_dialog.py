# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace

import pytest
from helpers import wait_for_condition
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.length import LengthOptimizationStatus
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    PowerBudget,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.optimization_dialog import OptimizationDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.task_progress import TaskProgressState


class AnalyticalSolver:
    def __init__(self, resonance_length_m: float = 20.3) -> None:
        self.resonance_length_m = resonance_length_m

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

    def validate(self, model: AntennaModel, spec: SimulationSpec) -> tuple[Diagnostic, ...]:
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
        length = model.wires[0].length_m
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=model.design_frequency_hz,
                    feed_tag=1,
                    feed_segment=11,
                    impedance_ohm=complex(70.0, 5.0 * (length - self.resonance_length_m)),
                    swr=1.0 + abs(length - self.resonance_length_m),
                    input_power_w=0.001,
                    power_budget=PowerBudget(
                        input_w=1.0,
                        radiated_w=0.9,
                        structure_loss_w=0.1,
                        network_loss_w=0.0,
                        efficiency_percent=95.0 - abs(length - self.resonance_length_m),
                    ),
                    far_field=(
                        FarFieldPoint(
                            theta_deg=90.0,
                            phi_deg=0.0,
                            gain_vertical_db=2.0 - abs(length - self.resonance_length_m),
                            gain_horizontal_db=None,
                            gain_total_db=2.0 - abs(length - self.resonance_length_m),
                            axial_ratio=None,
                            tilt_deg=None,
                            polarization="LINEAR",
                            e_theta_magnitude_v_per_m=None,
                            e_theta_phase_deg=None,
                            e_phi_magnitude_v_per_m=None,
                            e_phi_phase_deg=None,
                        ),
                    ),
                ),
            ),
        )


def test_optimization_dialog_runs_and_selects_length(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    base_spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        far_field=FarFieldRequest(enabled=True),
    )
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        parameters,
        base_spec,
    )
    qtbot.addWidget(dialog)
    dialog._min_length.setValue(18.0)
    dialog._max_length.setValue(22.0)
    dialog._target.setValue(0.0)
    dialog._max_evaluations.setValue(12)
    dialog._tolerance.setValue(0.1)
    dialog.show()

    dialog._run.click()

    assert dialog._task_progress.isHidden() is False
    assert dialog._task_progress.state is TaskProgressState.RUNNING
    assert dialog._task_progress.progress_maximum == dialog._run_estimated_evaluations

    wait_for_condition(lambda: dialog._thread is None, timeout_ms=5_000)

    assert dialog._task_progress.state is TaskProgressState.COMPLETED
    assert "Completed" in dialog._task_progress.text
    assert dialog._result is not None
    assert dialog._result.status is LengthOptimizationStatus.CONVERGED
    assert dialog.selected_length_m() == pytest.approx(20.3, abs=0.01)
    assert dialog._evaluations.rowCount() >= 3
    assert dialog._sensitivity.rowCount() == 4
    assert dialog._apply.isEnabled() is True

    dialog._apply.click()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_optimization_dialog_shows_the_matching_override_warning(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    base_spec = replace(
        SimulationSpec(
            frequency_plan=FrequencyPlan.single(7_100_000.0),
            far_field=FarFieldRequest(enabled=True),
        ),
        matching_network_override=True,
    )
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        parameters,
        base_spec,
    )
    qtbot.addWidget(dialog)

    assert dialog._matching_override_warning.isHidden() is False
    assert "not cascaded" in dialog._matching_override_warning.text()


def test_optimization_dialog_hides_the_matching_override_warning_by_default(
    qtbot: QtBot,
) -> None:
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        SimulationSpec(
            frequency_plan=FrequencyPlan.single(7_100_000.0),
            far_field=FarFieldRequest(enabled=True),
        ),
    )
    qtbot.addWidget(dialog)

    assert dialog._matching_override_warning.isHidden() is True


def test_optimization_dialog_handles_a_loop_circumference(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
    )
    base_spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        far_field=FarFieldRequest(enabled=True),
    )
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(resonance_length_m=10.3),
        parameters,
        base_spec,
    )
    qtbot.addWidget(dialog)
    dialog._min_length.setValue(36.0)
    dialog._max_length.setValue(44.0)
    dialog.show()

    dialog._run.click()
    wait_for_condition(lambda: dialog._thread is None, timeout_ms=5_000)

    assert dialog._result is not None
    assert dialog._result.status is LengthOptimizationStatus.CONVERGED
    assert dialog.selected_dimension_m() == pytest.approx(41.2, abs=0.02)
    assert dialog._apply.isEnabled() is True


def test_optimization_dialog_minimizes_swr(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    base_spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        far_field=FarFieldRequest(enabled=True),
    )
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        parameters,
        base_spec,
    )
    qtbot.addWidget(dialog)
    dialog._objective.setCurrentIndex(1)
    dialog._min_length.setValue(18.0)
    dialog._max_length.setValue(22.0)
    dialog.show()

    dialog._run.click()
    wait_for_condition(lambda: dialog._thread is None, timeout_ms=5_000)

    assert dialog._result is not None
    assert dialog._result.status is LengthOptimizationStatus.CONVERGED
    assert dialog.selected_dimension_m() == pytest.approx(20.3, abs=0.05)
    assert dialog._target.isVisible() is False
    assert dialog._evaluations.horizontalHeaderItem(6).text() == "SWR"


def test_optimization_dialog_targets_a_complex_impedance(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    base_spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        far_field=FarFieldRequest(enabled=True),
    )
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        parameters,
        base_spec,
    )
    qtbot.addWidget(dialog)
    dialog._objective.setCurrentIndex(6)
    dialog._min_length.setValue(18.0)
    dialog._max_length.setValue(22.0)
    dialog._target_r.setValue(70.0)
    dialog._target.setValue(0.0)
    dialog._max_evaluations.setValue(41)
    dialog.show()

    dialog._run.click()
    wait_for_condition(lambda: dialog._thread is None, timeout_ms=5_000)

    assert dialog._result is not None
    assert dialog._result.status is LengthOptimizationStatus.CONVERGED
    assert dialog.selected_dimension_m() == pytest.approx(20.3, abs=0.01)
    assert dialog._result.best_impedance_error_ohm is not None
    assert dialog._result.best_impedance_error_ohm < 0.1
    assert dialog._target_r.isVisible() is True
    assert dialog._target.isVisible() is True
    assert dialog._evaluations.horizontalHeaderItem(6).text() == "SWR (target)"
    assert dialog._evaluations.columnCount() == 11
    assert dialog._evaluations.item(0, 0).text() == "1"
    assert dialog._evaluations.item(0, 2).text().startswith("20.300")


def test_optimization_dialog_maximizes_gain(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    base_spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        far_field=FarFieldRequest(enabled=True),
    )
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        parameters,
        base_spec,
    )
    qtbot.addWidget(dialog)
    dialog._objective.setCurrentIndex(3)
    dialog._min_length.setValue(18.0)
    dialog._max_length.setValue(22.0)
    dialog.show()

    dialog._run.click()
    wait_for_condition(lambda: dialog._thread is None, timeout_ms=5_000)

    assert dialog._result is not None
    assert dialog._result.status is LengthOptimizationStatus.CONVERGED
    assert dialog.selected_dimension_m() == pytest.approx(20.3, abs=0.1)
    assert dialog._target.isVisible() is False
    assert dialog._swr_limit.isVisible() is False


def test_optimization_dialog_maximizes_efficiency(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    base_spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        far_field=FarFieldRequest(enabled=False),
    )
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        parameters,
        base_spec,
    )
    qtbot.addWidget(dialog)
    dialog._objective.setCurrentIndex(4)
    dialog._min_length.setValue(18.0)
    dialog._max_length.setValue(22.0)
    dialog.show()

    dialog._run.click()
    wait_for_condition(lambda: dialog._thread is None, timeout_ms=5_000)

    assert dialog._result is not None
    assert dialog._result.status is LengthOptimizationStatus.CONVERGED
    assert dialog.selected_dimension_m() == pytest.approx(20.3, abs=0.15)
    assert dialog._result.best_efficiency_percent == pytest.approx(95.0, abs=0.2)
    assert dialog._evaluations.columnCount() == 11
    assert dialog._sensitivity.columnCount() == 8
    assert dialog._swr_weight.isVisible() is False


def test_optimization_dialog_balances_swr_and_gain(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    base_spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        far_field=FarFieldRequest(enabled=True),
    )
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        parameters,
        base_spec,
    )
    qtbot.addWidget(dialog)
    dialog._objective.setCurrentIndex(5)
    dialog._min_length.setValue(18.0)
    dialog._max_length.setValue(22.0)
    dialog.show()

    assert dialog._swr_weight.isVisible() is True
    assert dialog._gain_weight.isVisible() is True
    dialog._run.click()
    wait_for_condition(lambda: dialog._thread is None, timeout_ms=5_000)

    assert dialog._result is not None
    assert dialog._result.status is LengthOptimizationStatus.CONVERGED
    assert dialog.selected_dimension_m() == pytest.approx(20.3, abs=0.1)
    assert dialog._result.best_score is not None


def test_optimization_dialog_reports_estimated_evaluations(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        parameters,
        SimulationSpec(
            frequency_plan=FrequencyPlan.single(7_100_000.0),
            far_field=FarFieldRequest(enabled=False),
        ),
    )
    qtbot.addWidget(dialog)
    dialog._run_estimated_evaluations = 16
    dialog._last_progress_emit = 0.0
    dialog._task_progress.begin_determinate(16, "optimize.running")

    dialog._on_progress(5)

    assert dialog._task_progress.progress_value == 5
    assert "5 / ~16" in dialog._task_progress.text


def test_optimization_dialog_marks_progress_as_cancelling(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    dialog = OptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        parameters,
        SimulationSpec(
            frequency_plan=FrequencyPlan.single(7_100_000.0),
            far_field=FarFieldRequest(enabled=False),
        ),
    )
    qtbot.addWidget(dialog)
    dialog._task_progress.begin_determinate(10, "optimize.running")
    dialog._cancel_token = EventCancelToken()

    dialog._cancel_run()

    assert dialog._task_progress.state is TaskProgressState.CANCELLING
    assert dialog._task_progress.text == "Cancelling..."
