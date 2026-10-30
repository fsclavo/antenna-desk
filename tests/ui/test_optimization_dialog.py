# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.length import LengthOptimizationStatus
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.optimization_dialog import OptimizationDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


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
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=5_000)

    assert dialog._result is not None
    assert dialog._result.status is LengthOptimizationStatus.CONVERGED
    assert dialog.selected_length_m() == pytest.approx(20.3, abs=0.01)
    assert dialog._evaluations.rowCount() >= 3
    assert dialog._sensitivity.rowCount() == 4
    assert dialog._apply.isEnabled() is True

    dialog._apply.click()
    assert dialog.result() == QDialog.DialogCode.Accepted


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
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=5_000)

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
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=5_000)

    assert dialog._result is not None
    assert dialog._result.status is LengthOptimizationStatus.CONVERGED
    assert dialog.selected_dimension_m() == pytest.approx(20.3, abs=0.05)
    assert dialog._target.isVisible() is False


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
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=5_000)

    assert dialog._result is not None
    assert dialog._result.status is LengthOptimizationStatus.CONVERGED
    assert dialog.selected_dimension_m() == pytest.approx(20.3, abs=0.1)
    assert dialog._target.isVisible() is False
    assert dialog._swr_limit.isVisible() is False
