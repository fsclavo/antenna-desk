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

    dialog._evaluations.selectRow(1)
    assert dialog.selected_parameters() is not None
    assert "Selected candidate" in dialog._summary.text()

    dialog._apply.click()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_generic_element_dialog_supports_integer_variables(qtbot: QtBot) -> None:
    dialog = ElementOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
        title_key="element_optimize.loop_title",
        variables=(
            ElementOptimizationVariable(
                "sides",
                "Sides",
                4.0,
                integer=True,
            ),
        ),
        build_parameters=lambda values: DipoleParameters(
            frequency_hz=values["__frequency_hz"],
            total_length_m=20.0,
            height_m=8.0,
        ),
        objectives=(ElementOptimizationObjective.TARGET_IMPEDANCE,),
        default_frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(dialog)

    variables, starts = dialog._variables()

    assert variables[0].integer is True
    assert variables[0].minimum == pytest.approx(3.0)
    assert variables[0].maximum == pytest.approx(5.0)
    assert starts["sides"] == pytest.approx(4.0)
    assert dialog._table.item(0, 2).text() == "4"


def test_element_dialog_supports_explicit_integer_bounds(qtbot: QtBot) -> None:
    dialog = ElementOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
        title_key="element_optimize.yagi_title",
        variables=(
            ElementOptimizationVariable(
                "element_count",
                "Elements",
                5.0,
                integer=True,
                minimum=2.0,
                maximum=8.0,
            ),
        ),
        build_parameters=lambda values: DipoleParameters(
            frequency_hz=values["__frequency_hz"],
            total_length_m=20.0,
            height_m=8.0,
        ),
        objectives=(ElementOptimizationObjective.TARGET_IMPEDANCE,),
        default_frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(dialog)

    variables, starts = dialog._variables()

    assert variables[0].minimum == pytest.approx(2.0)
    assert variables[0].maximum == pytest.approx(8.0)
    assert variables[0].integer is True
    assert starts["element_count"] == pytest.approx(5.0)
    assert dialog._table.item(0, 3).text() == "2"
    assert dialog._table.item(0, 4).text() == "8"

    dialog._bound_percent.setValue(50.0)

    assert dialog._table.item(0, 3).text() == "2"
    assert dialog._table.item(0, 4).text() == "8"


def test_element_dialog_supports_a_minimum_only_bound(qtbot: QtBot) -> None:
    dialog = ElementOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
        title_key="element_optimize.yagi_title",
        variables=(
            ElementOptimizationVariable(
                "gap",
                "Gap",
                0.05,
                minimum=0.1,
            ),
        ),
        build_parameters=lambda values: DipoleParameters(
            frequency_hz=values["__frequency_hz"],
            total_length_m=20.0,
            height_m=8.0,
        ),
        objectives=(ElementOptimizationObjective.TARGET_IMPEDANCE,),
        default_frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(dialog)

    variables, _ = dialog._variables()

    assert variables[0].minimum == pytest.approx(0.1)
    assert variables[0].maximum > variables[0].minimum
    assert dialog._table.item(0, 3).text() == "0.100"


def test_element_dialog_rejects_maximum_without_minimum() -> None:
    with pytest.raises(ValueError, match="maximum requires a minimum"):
        ElementOptimizationVariable(
            "element_count",
            "Elements",
            5.0,
            integer=True,
            maximum=8.0,
        )


def test_element_dialog_labels_swr_against_the_target(qtbot: QtBot) -> None:
    dialog = ElementOptimizationDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalSolver(),
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
        title_key="element_optimize.loop_title",
        variables=(ElementOptimizationVariable("length_m", "Length", 20.0),),
        build_parameters=lambda values: DipoleParameters(
            frequency_hz=values["__frequency_hz"],
            total_length_m=values["length_m"],
            height_m=8.0,
        ),
        objectives=(
            ElementOptimizationObjective.TARGET_IMPEDANCE,
            ElementOptimizationObjective.MAX_GAIN,
        ),
        default_frequency_hz=7_100_000.0,
        default_target_resistance_ohm=100.0,
    )
    qtbot.addWidget(dialog)

    assert dialog._evaluations.horizontalHeaderItem(4).text() == "SWR (target)"
    assert dialog._target_r.value() == pytest.approx(100.0)
    assert dialog._target().resistance_ohm == pytest.approx(100.0)

    dialog._objective.setCurrentIndex(1)

    assert dialog._evaluations.horizontalHeaderItem(4).text() == "SWR"
    assert dialog._target().resistance_ohm == pytest.approx(50.0)
