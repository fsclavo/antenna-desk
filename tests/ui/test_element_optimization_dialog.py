# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.application.use_cases.optimize_elements import ElementOptimizationObjective
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.multi_variable import BoundedStatus
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import FrequencyResult, SimulationResult, SimulationStatus
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.element_optimization_dialog import (
    ElementOptimizationDialog,
    ElementOptimizationVariable,
)
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


class AnalyticalSolver:
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
        impedance = complex(50.0 + 10.0 * (length - 20.0), 0.0)
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


def test_generic_element_dialog_applies_optimized_parameters(qtbot: QtBot) -> None:
    base = DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0)

    def build(values: dict[str, float]) -> DipoleParameters:
        return DipoleParameters(
            frequency_hz=values["__frequency_hz"],
            total_length_m=values["length_m"],
            height_m=base.height_m,
        )

    dialog = ElementOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
        title_key="element_optimize.yagi_title",
        variables=(ElementOptimizationVariable("length_m", "Length", 20.0),),
        build_parameters=build,
        objectives=(ElementOptimizationObjective.TARGET_IMPEDANCE,),
        default_frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(dialog)
    dialog._max_evaluations.setValue(30)
    dialog.show()

    dialog._run.click()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=5_000)

    assert dialog._result is not None
    assert dialog._result.status is BoundedStatus.CONVERGED
    selected = dialog.selected_parameters()
    assert isinstance(selected, DipoleParameters)
    assert selected.total_length_m == pytest.approx(20.0, abs=0.05)

    dialog._apply.click()
    assert dialog.result() == QDialog.DialogCode.Accepted
