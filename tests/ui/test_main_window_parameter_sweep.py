# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parameter sweep integration in the main window."""

from __future__ import annotations

from dataclasses import replace

import pytest
from PySide6.QtWidgets import QDialog

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


def test_sweep_action_is_available_and_retranslates(window: MainWindow) -> None:
    assert window._sweep_action in window._tools_menu.actions()
    assert window._sweep_action.isEnabled()
    assert window._sweep_action.text() == "Parameter Sweep..."

    window._set_language(Language.SPANISH)

    assert window._sweep_action.text() == "Barrido de parámetros..."
    window._set_language(Language.ENGLISH)


def test_parameter_sweep_applies_and_undoes(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    proposed = replace(
        window._project.designs[0].parameters,
        total_length_m=10.2,
    )
    calls: list[str] = []

    class FakeSweepDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_parameters(self) -> object:
            return proposed

    monkeypatch.setattr(
        main_window_module,
        "ParameterSweepDialog",
        FakeSweepDialog,
    )
    monkeypatch.setattr(window, "simulate", lambda: calls.append("simulate"))

    window.parameter_sweep()

    design = window._project.designs[0]
    assert isinstance(design.parameters, DipoleParameters)
    assert design.parameters.total_length_m == pytest.approx(10.2)
    assert window._dirty is True
    assert window._last_status_key == "status.parameter_sweep_applied"
    assert calls == ["simulate"]

    window._undo_stack.undo()

    design = window._project.designs[0]
    assert isinstance(design.parameters, DipoleParameters)
    assert design.parameters.total_length_m == pytest.approx(20.0)
    window._dirty = False


def test_parameter_sweep_is_unavailable_for_an_unsupported_family(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parameters = MagneticLoopParameters(frequency_hz=7_100_000.0, diameter_m=1.0)
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="Loop",
            variant_name="Loop",
            parameters=parameters,
        )
    )
    window._set_project(project, project.designs[0].id, path=None, dirty=False)
    errors: list[str] = []
    monkeypatch.setattr(window, "_show_error", lambda message: errors.append(message))

    assert window._sweep_action.isEnabled() is False
    window.parameter_sweep()

    assert errors == [window._translator.t("sweep.unavailable_family")]
