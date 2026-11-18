# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Canonical inputs stay stable when only the display units change."""

from __future__ import annotations

from dataclasses import fields

import pytest
from main_window_support import FakeSolver
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.moxon import MoxonParameters, moxon_20m_wire
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.design_from_frequency_dialog import (
    DesignFromFrequencyDialog,
)
from antennadesk.ui.dialogs.optimization_dialog import OptimizationDialog
from antennadesk.ui.dialogs.synthesis_dialog import SynthesisDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import DisplayUnits, LengthPolicy, UnitSystem
from antennadesk.ui.widgets.moxon_form import MoxonForm


def _lengths(parameters: object) -> dict[str, float]:
    values: dict[str, float] = {}
    for field in fields(parameters):
        value = getattr(parameters, field.name)
        if field.name.endswith("_m") and isinstance(value, (int, float)):
            values[field.name] = float(value)
    return values


def _assert_model_geometry_close(before: object, after: object) -> None:
    before_wires = before.wires
    after_wires = after.wires
    assert len(after_wires) == len(before_wires)
    for before_wire, after_wire in zip(before_wires, after_wires, strict=True):
        for point_name in ("start", "end"):
            before_point = getattr(before_wire, point_name)
            after_point = getattr(after_wire, point_name)
            assert after_point.x_m == pytest.approx(before_point.x_m, abs=2e-3)
            assert after_point.y_m == pytest.approx(before_point.y_m, abs=2e-3)
            assert after_point.z_m == pytest.approx(before_point.z_m, abs=2e-3)


def test_unit_switch_preserves_solver_input_geometry(qtbot: QtBot) -> None:
    parameters = moxon_20m_wire(frequency_hz=435_000_000.0, height_m=10.0)
    assert isinstance(parameters, MoxonParameters)
    form = MoxonForm(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        display_units=DisplayUnits(UnitSystem.METRIC, LengthPolicy.AUTO),
    )
    qtbot.addWidget(form)
    form.set_parameters(parameters)

    before = form.parameters()
    before_antenna = before.to_antenna(name="Moxon")
    form.set_unit_system(UnitSystem.IMPERIAL)
    after = form.parameters()
    after_antenna = after.to_antenna(name="Moxon")

    before_lengths = _lengths(before)
    after_lengths = _lengths(after)
    assert set(after_lengths) == set(before_lengths)
    for name, meters in before_lengths.items():
        assert after_lengths[name] == pytest.approx(meters, rel=1e-3, abs=2e-3)
    _assert_model_geometry_close(before_antenna, after_antenna)


def test_design_from_frequency_estimate_is_unit_independent(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=146_000_000.0,
        total_length_m=1.0,
        height_m=12.0,
    )
    estimates = []
    for display_units in (
        DisplayUnits(UnitSystem.METRIC, LengthPolicy.AUTO),
        DisplayUnits(UnitSystem.IMPERIAL, LengthPolicy.AUTO),
    ):
        dialog = DesignFromFrequencyDialog(
            Translator(Language.ENGLISH),
            display_units.system,
            initial_parameters=parameters,
            display_units=display_units,
        )
        qtbot.addWidget(dialog)
        dialog._run_estimate()
        estimate = dialog.estimated_parameters()
        assert isinstance(estimate, DipoleParameters)
        estimates.append(estimate)

    metric, imperial = estimates
    assert imperial.total_length_m == pytest.approx(metric.total_length_m, abs=2e-3)
    assert imperial.height_m == pytest.approx(metric.height_m, abs=2e-3)


def test_optimization_spec_is_unit_independent(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    base_spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))
    specs = []
    for display_units in (
        DisplayUnits(UnitSystem.METRIC, LengthPolicy.FIXED),
        DisplayUnits(UnitSystem.IMPERIAL, LengthPolicy.FIXED),
    ):
        dialog = OptimizationDialog(
            Translator(Language.ENGLISH),
            display_units.system,
            FakeSolver(),
            parameters,
            base_spec,
            display_units=display_units,
        )
        qtbot.addWidget(dialog)
        specs.append(dialog._optimization_spec())

    metric, imperial = specs
    assert imperial.min_length_m == pytest.approx(metric.min_length_m, abs=2e-4)
    assert imperial.max_length_m == pytest.approx(metric.max_length_m, abs=2e-4)
    assert imperial.max_evaluations == metric.max_evaluations
    assert imperial.objective is metric.objective


def test_synthesis_variables_are_unit_independent(qtbot: QtBot) -> None:
    parameters = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        folded=True,
    )
    base_spec = SimulationSpec(frequency_plan=FrequencyPlan.single(145_000_000.0))
    variables = []
    for display_units in (
        DisplayUnits(UnitSystem.METRIC, LengthPolicy.FIXED),
        DisplayUnits(UnitSystem.IMPERIAL, LengthPolicy.FIXED),
    ):
        dialog = SynthesisDialog(
            Translator(Language.ENGLISH),
            display_units.system,
            FakeSolver(),
            parameters,
            base_spec,
            display_units=display_units,
        )
        qtbot.addWidget(dialog)
        variables.append(dialog._variables())

    metric, imperial = variables
    assert len(imperial) == len(metric)
    for metric_variable, imperial_variable in zip(metric, imperial, strict=True):
        assert imperial_variable.name == metric_variable.name
        assert imperial_variable.minimum == pytest.approx(metric_variable.minimum, abs=2e-4)
        assert imperial_variable.maximum == pytest.approx(metric_variable.maximum, abs=2e-4)
