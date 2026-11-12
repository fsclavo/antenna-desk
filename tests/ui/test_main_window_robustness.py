# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tolerance and robustness integration in the main window."""

from __future__ import annotations

import pytest

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


def test_robustness_action_is_available_and_retranslates(window: MainWindow) -> None:
    assert window._robustness_action in window._tools_menu.actions()
    assert window._robustness_action.isEnabled()
    assert window._robustness_action.text() == "Tolerance & Robustness..."

    window._set_language(Language.SPANISH)

    assert window._robustness_action.text() == "Tolerancia y robustez..."
    window._set_language(Language.ENGLISH)


def test_robustness_action_opens_the_dialog_without_changing_the_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    before = window._project

    class FakeRobustnessDialog:
        opened = False

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> int:
            type(self).opened = True
            return 0

    monkeypatch.setattr(
        main_window_module,
        "RobustnessDialog",
        FakeRobustnessDialog,
    )

    window.tolerance_robustness()

    assert FakeRobustnessDialog.opened is True
    assert window._project == before
    assert window._dirty is False


def test_robustness_is_unavailable_for_an_unsupported_family(
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

    assert window._robustness_action.isEnabled() is False
    window.tolerance_robustness()

    assert errors == [window._translator.t("robustness.unavailable_family")]
