# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.multi_variable import BoundedStatus
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import FrequencyResult, SimulationResult, SimulationStatus
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.fan_dipole_optimization_dialog import (
    FanDipoleOptimizationDialog,
)
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


class AnalyticalFanSolver:
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
        first = 2.0 * model.wires[0].length_m
        second = 2.0 * model.wires[2].length_m
        impedance = complex(50.0 + 10.0 * (first - 10.0), 10.0 * (second - 20.0))
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=model.design_frequency_hz,
                    feed_tag=1,
                    feed_segment=1,
                    impedance_ohm=impedance,
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
        )


def test_fan_optimization_dialog_applies_element_lengths(qtbot: QtBot) -> None:
    parameters = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(FanElement(10.0), FanElement(20.0)),
        apex_height_m=10.0,
    )
    dialog = FanDipoleOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalFanSolver(),
        parameters,
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
    )
    qtbot.addWidget(dialog)
    dialog._target_r.setValue(50.0)
    dialog._target_x.setValue(0.0)
    dialog._max_evaluations.setValue(60)
    dialog.show()

    dialog._run.click()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=5_000)

    assert dialog._result is not None
    assert dialog._result.status is BoundedStatus.CONVERGED
    selected = dialog.selected_parameters()
    assert selected is not None
    assert selected.elements[0].length_m == pytest.approx(10.0, abs=0.05)
    assert selected.elements[1].length_m == pytest.approx(20.0, abs=0.05)
    assert dialog._evaluations.item(0, 0).text() == "1"

    dialog._apply.click()
    assert dialog.result() == QDialog.DialogCode.Accepted
