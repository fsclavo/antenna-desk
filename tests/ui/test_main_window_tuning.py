# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tuning assistant integration in the main window."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from PySide6.QtWidgets import QDialog, QMessageBox

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.domain.measurement import Measurement, MeasurementPoint
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


def _measurement() -> Measurement:
    return Measurement(
        id=uuid4(),
        name="Field sweep",
        created_at=datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(
            MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
            MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        ),
    )


def test_tuning_action_requires_measurements_and_retranslates(
    window: MainWindow,
) -> None:
    assert window._tuning_action in window._tools_menu.actions()
    assert window._tuning_action.isEnabled() is False

    assert window._project is not None
    window._project = window._project.with_measurement(
        _measurement(),
        updated_at=window._project.updated_at,
    )
    window._update_actions()

    assert window._tuning_action.isEnabled() is True
    assert window._tuning_action.text() == "Tuning Assistant..."

    window._set_language(Language.SPANISH)

    assert window._tuning_action.text() == "Asistente de ajuste..."
    window._set_language(Language.ENGLISH)


def test_tune_measurement_applies_and_undoes(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    measurement = _measurement()
    window._project = window._project.with_measurement(
        measurement,
        updated_at=window._project.updated_at,
    )
    proposed = replace(
        window._project.designs[0].parameters,
        total_length_m=19.95,
    )
    calls: list[str] = []

    class FakeTuningDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> object:
            return proposed

    monkeypatch.setattr(
        main_window_module,
        "TuningAssistantDialog",
        FakeTuningDialog,
    )
    monkeypatch.setattr(window, "simulate", lambda: calls.append("simulate"))

    window.tune_measurement(measurement)

    design = window._project.designs[0]
    assert isinstance(design.parameters, DipoleParameters)
    assert design.parameters.total_length_m == pytest.approx(19.95)
    assert window._dirty is True
    assert window._last_status_key == "status.tuning_applied"
    assert calls == ["simulate"]

    window._undo_stack.undo()

    design = window._project.designs[0]
    assert isinstance(design.parameters, DipoleParameters)
    assert design.parameters.total_length_m == pytest.approx(20.0)
    window._dirty = False


def test_tune_measurement_reports_an_unavailable_family(
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
    measurement = _measurement()
    project = project.with_measurement(
        measurement,
        updated_at=project.updated_at,
    )
    window._set_project(project, project.designs[0].id, path=None, dirty=False)
    errors: list[str] = []
    monkeypatch.setattr(window, "_show_error", lambda message: errors.append(message))

    window.tune_measurement(measurement)

    assert errors == [window._translator.t("tuning.unavailable_family")]


def test_tune_measurement_without_measurements_shows_a_message(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    messages: list[str] = []
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args, **kwargs: messages.append(args[2]),
    )

    window.tune_measurement()

    assert messages == [window._translator.t("tuning.need_measurement")]
