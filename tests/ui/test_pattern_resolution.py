# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.environment.ground import GroundModel
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.pattern_resolution import far_field_request, pattern_counts
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.dipole_form import DipoleForm


def test_pattern_counts_follow_the_requested_step() -> None:
    free_space = GroundModel.free_space()
    ground = GroundModel.perfect()

    assert pattern_counts(10.0, free_space) == (19, 37)
    assert pattern_counts(5.0, free_space) == (37, 73)
    assert pattern_counts(2.0, ground) == (46, 181)
    assert pattern_counts(1.0, ground) == (91, 361)


def test_far_field_request_uses_ground_hemisphere() -> None:
    request = far_field_request(5.0, GroundModel.perfect())

    assert request.theta_start_deg == 0.0
    assert request.theta_stop_deg == 90.0
    assert request.theta_count == 19
    assert request.phi_count == 73
    assert request.theta_step_deg == pytest.approx(5.0)
    assert request.phi_step_deg == pytest.approx(5.0)


def test_form_defaults_to_100_sweep_points_and_5_degree_pattern(qtbot: QtBot) -> None:
    form = DipoleForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)

    assert form._sweep.isChecked() is True
    assert form._sweep_points.value() == 100
    spec = form.simulation_spec()
    assert spec.frequency_plan.count == 100
    assert spec.far_field.theta_count == 19
    assert spec.far_field.phi_count == 73


def test_form_changes_pattern_resolution(qtbot: QtBot) -> None:
    form = DipoleForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)

    index = form._pattern_resolution.findData(2.0)
    form._pattern_resolution.setCurrentIndex(index)
    spec = form.simulation_spec()

    assert spec.far_field.theta_count == 46
    assert spec.far_field.phi_count == 181
    assert spec.far_field.theta_step_deg == pytest.approx(2.0)
    assert "8,326" in form._pattern_points.text()


def test_custom_dialog_exposes_pattern_step(qtbot: QtBot) -> None:
    from antennadesk.ui.dialogs.custom_antenna_dialog import CustomAntennaDialog

    dialog = CustomAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        pattern_step_deg=5.0,
    )
    qtbot.addWidget(dialog)

    assert dialog.pattern_step_deg() == pytest.approx(5.0)
    assert "2,701" in dialog._pattern_points.text()
