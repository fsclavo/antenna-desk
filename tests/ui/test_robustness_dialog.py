# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tolerance and robustness dialog behavior."""

from __future__ import annotations

from uuid import UUID

import pyqtgraph as pg
from PySide6.QtCore import Qt
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
from antennadesk.ui.dialogs.robustness_dialog import RobustnessDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


class _Solver:
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
        height = min(point.z_m for wire in model.wires for point in (wire.start, wire.end))
        swr = 1.0 + abs(length - 10.0) * 2.0 + abs(height - 8.0) * 0.5
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
                    impedance_ohm=complex(50.0 * swr, 0.0),
                    swr=swr,
                    input_power_w=0.001,
                ),
            ),
            duration_s=0.0,
        )


def _dialog(
    qtbot: QtBot,
    *,
    language: Language = Language.ENGLISH,
) -> RobustnessDialog:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=10.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    design = DesignVariant(
        id=UUID("00000000-0000-0000-0000-000000000091"),
        name="40 m dipole",
        antenna_type="wire_dipole",
        parameters=parameters,
        antenna=parameters.to_antenna(name="40 m dipole"),
    )
    dialog = RobustnessDialog(
        Translator(language),
        UnitSystem.METRIC,
        _Solver(),
        availability.descriptor,
        design,
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
    )
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_lists_critical_dimensions_and_budget(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    assert dialog.windowTitle() == "Tolerance and robustness"
    assert dialog._variables_list.count() == 3
    assert "solver runs" in dialog._budget.text()
    assert dialog._run.isEnabled()


def test_dialog_runs_corners_and_monte_carlo(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._samples.setValue(5)
    dialog._variables_list.item(2).setCheckState(Qt.CheckState.Unchecked)

    dialog._start()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=15_000)

    result = dialog.robustness_result()
    assert result is not None
    assert len(result.scenarios) == 10
    assert result.nominal is not None
    assert result.worst_corner is not None
    assert result.statistics.count == 5
    assert dialog._table.rowCount() == 10
    assert "Nominal SWR" in dialog._summary.text()
    assert "Worst corner" in dialog._corner_summary.text()
    assert "Monte Carlo" in dialog._mc_summary.text()
    assert any(isinstance(item, pg.BarGraphItem) for item in dialog._plot.plotItem.items)


def test_dialog_can_run_nominal_only_and_retranslates(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot, language=Language.SPANISH)
    dialog._corners.setChecked(False)
    dialog._samples.setValue(0)

    assert dialog.windowTitle() == "Tolerancia y robustez"
    assert dialog._run.text() == "Ejecutar análisis"
    dialog._start()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=15_000)

    result = dialog.robustness_result()
    assert result is not None
    assert len(result.scenarios) == 1
    assert dialog._table.rowCount() == 1
    assert "no solicitado" in dialog._mc_summary.text()


def test_dialog_requires_at_least_one_dimension(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    for row in range(dialog._variables_list.count()):
        dialog._variables_list.item(row).setCheckState(Qt.CheckState.Unchecked)

    assert dialog._run.isEnabled() is False
    assert dialog._validation.isHidden() is False
