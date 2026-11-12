# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided experiment integration in the main window."""

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


def test_guided_action_is_available_and_retranslates(window: MainWindow) -> None:
    assert window._guided_experiments_action in window._tools_menu.actions()
    assert window._guided_experiments_action.isEnabled()
    assert window._guided_experiments_action.text() == "Guided Experiments..."
    assert "resonance" in window._guided_experiments_action.toolTip().lower()

    window._set_language(Language.SPANISH)

    assert window._guided_experiments_action.text() == "Experimentos guiados..."
    assert "resonancia" in window._guided_experiments_action.toolTip().lower()
    window._set_language(Language.ENGLISH)


def test_guided_experiment_applies_and_undoes(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    proposed = replace(
        window._project.designs[0].parameters,
        total_length_m=10.3,
    )
    calls: list[str] = []

    class FakeGuidedDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_parameters(self) -> object:
            return proposed

    monkeypatch.setattr(
        main_window_module,
        "GuidedExperimentsDialog",
        FakeGuidedDialog,
    )
    monkeypatch.setattr(window, "simulate", lambda: calls.append("simulate"))

    window.guided_experiments()

    design = window._project.designs[0]
    assert isinstance(design.parameters, DipoleParameters)
    assert design.parameters.total_length_m == pytest.approx(10.3)
    assert window._dirty is True
    assert window._last_status_key == "status.guided_experiment_applied"
    assert calls == ["simulate"]

    window._undo_stack.undo()

    design = window._project.designs[0]
    assert isinstance(design.parameters, DipoleParameters)
    assert design.parameters.total_length_m == pytest.approx(20.0)
    window._dirty = False


def test_guided_experiments_are_unavailable_for_an_unsupported_family(
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

    assert window._guided_experiments_action.isEnabled() is False
    window.guided_experiments()

    assert errors == [window._translator.t("guided.unavailable_family")]
