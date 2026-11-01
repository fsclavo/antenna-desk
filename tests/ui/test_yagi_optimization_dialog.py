# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.multi_variable import BoundedStatus
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import FrequencyResult, SimulationResult, SimulationStatus
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.yagi_optimization_dialog import YagiOptimizationDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


class AnalyticalYagiSolver:
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
        reflector, driven = model.wires[0].length_m, model.wires[1].length_m
        gap = model.wires[1].start.x_m - model.wires[0].start.x_m
        impedance = complex(
            50.0 + 10.0 * (reflector - 10.5),
            10.0 * (driven - 10.0) + 5.0 * (gap - 2.0),
        )
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=model.design_frequency_hz,
                    feed_tag=2,
                    feed_segment=1,
                    impedance_ohm=impedance,
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
        )


def test_yagi_optimization_dialog_applies_element_lengths(qtbot: QtBot) -> None:
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(0.0, 10.5, 0.002),
            YagiElement(2.0, 10.0, 0.002),
        ),
        height_m=12.0,
        driven_index=1,
    )
    dialog = YagiOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalYagiSolver(),
        parameters,
        SimulationSpec(frequency_plan=FrequencyPlan.single(14_100_000.0)),
    )
    qtbot.addWidget(dialog)
    dialog._target_r.setValue(50.0)
    dialog._target_x.setValue(0.0)
    dialog._max_evaluations.setValue(120)
    dialog._samples.setValue(5)
    dialog._passes.setValue(4)
    dialog.show()

    dialog._run.click()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=5_000)

    assert dialog._result is not None
    assert dialog._result.status is BoundedStatus.CONVERGED
    selected = dialog.selected_parameters()
    assert selected is not None
    assert selected.elements[0].length_m == pytest.approx(10.5, abs=0.05)
    assert selected.elements[1].length_m == pytest.approx(10.0, abs=0.05)
    assert selected.elements[1].position_m - selected.elements[0].position_m == pytest.approx(
        2.0, abs=0.05
    )
    assert dialog._evaluations.rowCount() > 0
    assert dialog._evaluations.item(0, 0).text() == "1"

    dialog._apply.click()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_yagi_optimization_respects_the_minimum_gap(qtbot: QtBot) -> None:
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(0.0, 10.5, 0.002),
            YagiElement(2.0, 10.0, 0.002),
        ),
        height_m=12.0,
        driven_index=1,
    )
    dialog = YagiOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalYagiSolver(),
        parameters,
        SimulationSpec(frequency_plan=FrequencyPlan.single(14_100_000.0)),
    )
    qtbot.addWidget(dialog)
    for row in range(dialog._table.rowCount()):
        length_item = dialog._table.item(row, 2)
        assert length_item is not None
        length_item.setCheckState(Qt.CheckState.Unchecked)
    dialog._min_gap.setValue(2.5)
    dialog._max_evaluations.setValue(40)
    dialog.show()

    dialog._run.click()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=5_000)

    selected = dialog.selected_parameters()
    assert selected is not None
    assert selected.elements[1].position_m - selected.elements[0].position_m >= 2.5 - 1e-6
