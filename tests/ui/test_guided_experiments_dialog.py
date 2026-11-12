# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided experiment chooser behavior."""

from __future__ import annotations

from uuid import UUID

import pytest
from main_window_support import FakeSolver
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.optimization.descriptor import (
    AntennaOptimizerDescriptor,
    FamilyOptimizationObjective,
)
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.optimization.variables import OptimizationVariable
from antennadesk.domain.projects.project import DesignVariant
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs import guided_experiments_dialog as guided_module
from antennadesk.ui.dialogs.guided_experiments_dialog import GuidedExperimentsDialog
from antennadesk.ui.dialogs.parameter_sweep_dialog import SweepGuide
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _parameters() -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=10.0,
        height_m=8.0,
    )


def _design(parameters: DipoleParameters) -> DesignVariant:
    return DesignVariant(
        id=UUID("00000000-0000-0000-0000-000000000082"),
        name="40 m dipole",
        antenna_type="wire_dipole",
        parameters=parameters,
        antenna=parameters.to_antenna(name="40 m dipole"),
    )


def _dialog(
    qtbot: QtBot,
    *,
    language: Language = Language.ENGLISH,
    descriptor: AntennaOptimizerDescriptor | None = None,
) -> GuidedExperimentsDialog:
    parameters = _parameters()
    if descriptor is None:
        availability = optimizer_availability(parameters)
        assert availability.descriptor is not None
        descriptor = availability.descriptor
    dialog = GuidedExperimentsDialog(
        Translator(language),
        UnitSystem.METRIC,
        FakeSolver(),
        descriptor,
        _design(parameters),
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
    )
    qtbot.addWidget(dialog)
    return dialog


def _radius_only_descriptor(parameters: DipoleParameters) -> AntennaOptimizerDescriptor:
    return AntennaOptimizerDescriptor(
        key="test_radius_only",
        variables=(
            OptimizationVariable(
                "wire_radius_m",
                "field.wire_radius",
                "optimize.group.conductor",
                5e-4,
                2e-3,
                unit="radius",
                step=1e-4,
            ),
        ),
        initial_values={"wire_radius_m": 1e-3},
        build_parameters=lambda values: parameters,
        validate=lambda values: (),
        objectives=frozenset({FamilyOptimizationObjective.TARGET_IMPEDANCE}),
    )


def test_chooser_lists_three_experiments_for_a_dipole(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    assert dialog.windowTitle() == "Guided experiments"
    assert dialog._list.count() == 3
    assert dialog._list.currentRow() == 0
    assert dialog._start.isEnabled() is True
    assert "Resonance and match" in dialog._details.text()
    assert "Horizontal axis" in dialog._details.text()
    assert "What to look for" in dialog._details.text()
    assert "Limits" in dialog._details.text()


def test_chooser_describes_the_two_dimensional_experiment(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    dialog._list.setCurrentRow(2)

    text = dialog._details.text()
    assert "Two dimensions at once" in text
    assert "Horizontal axis" in text
    assert "Vertical axis" in text
    assert "63" not in text


def test_chooser_marks_unavailable_experiments(qtbot: QtBot) -> None:
    parameters = _parameters()
    dialog = _dialog(
        qtbot,
        descriptor=_radius_only_descriptor(parameters),
    )

    assert dialog._list.count() == 3
    assert all(dialog._list.item(row).flags() == Qt.ItemFlag.NoItemFlags for row in range(3))
    assert dialog._start.isEnabled() is False
    assert "Unavailable" in dialog._details.text()


def test_chooser_returns_the_selected_guided_point(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parameters = _parameters()
    dialog = _dialog(qtbot)
    opened: dict[str, object] = {}

    class FakeSweepDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            opened.update(kwargs)

        def exec(self) -> int:
            return QDialog.DialogCode.Accepted

        def selected_parameters(self) -> DipoleParameters:
            return parameters

    monkeypatch.setattr(guided_module, "ParameterSweepDialog", FakeSweepDialog)

    dialog._start_experiment()

    guide = opened["guide"]
    assert isinstance(guide, SweepGuide)

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.selected_parameters() == parameters
    assert opened["preset_plan"] is not None
    assert guide.title_key == "guided.resonance.title"


def test_chooser_retranslates(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot, language=Language.SPANISH)

    assert dialog.windowTitle() == "Experimentos guiados"
    assert dialog._list.item(0).text() == "Resonancia y adaptación"
    assert "Eje horizontal" in dialog._details.text()
