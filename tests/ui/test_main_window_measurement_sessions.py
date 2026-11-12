# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measurement session and before/after integration in the main window."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from PySide6.QtWidgets import QDialog, QFileDialog

from antennadesk.domain.measurement import (
    Measurement,
    MeasurementPoint,
    MeasurementSession,
)
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


def _measurement(name: str, created_at: datetime) -> Measurement:
    return Measurement(
        id=uuid4(),
        name=name,
        created_at=created_at,
        reference_impedance_ohm=50.0,
        points=(MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),),
    )


def test_measurement_sessions_action_is_in_tools_and_retranslates(
    window: MainWindow,
) -> None:
    assert window._measurement_sessions_action in window._tools_menu.actions()
    assert window._measurement_sessions_action.isEnabled()
    assert window._measurement_sessions_action.text() == "Measurement Sessions..."

    window._set_language(Language.SPANISH)

    assert window._measurement_sessions_action.text() == "Sesiones de medición..."
    window._set_language(Language.ENGLISH)


def test_edit_measurement_sessions_applies_and_undoes(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    session = MeasurementSession(
        id=uuid4(),
        name="Field session",
        created_at=datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
    )
    updated = window._project.with_measurement_session(
        session,
        updated_at=window._project.updated_at + timedelta(hours=1),
    )

    class FakeSessionsDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_project(self) -> object:
            return updated

    monkeypatch.setattr(
        main_window_module,
        "MeasurementSessionsDialog",
        FakeSessionsDialog,
    )

    window.edit_measurement_sessions()

    assert window._project.measurement_sessions == (session,)
    assert window._dirty is True
    assert window._last_status_key == "status.measurement_sessions"

    window._undo_stack.undo()

    assert window._project.measurement_sessions == ()

    window._undo_stack.redo()

    assert window._project.measurement_sessions == (session,)
    window._dirty = False


def test_compare_measurements_uses_chronological_neighbors(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    first = _measurement("Before", datetime(2026, 11, 12, 14, 0, tzinfo=UTC))
    second = _measurement("After", datetime(2026, 11, 12, 16, 0, tzinfo=UTC))
    project = window._project.with_measurement(
        first,
        updated_at=window._project.updated_at,
    ).with_measurement(
        second,
        updated_at=window._project.updated_at,
    )
    window._project = project
    captured: dict[str, object] = {}

    class FakeComparisonDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured["args"] = args
            captured["kwargs"] = kwargs

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(
        main_window_module,
        "MeasurementComparisonDialog",
        FakeComparisonDialog,
    )

    window.compare_measurements(second)

    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["initial_before_id"] == first.id
    assert kwargs["initial_after_id"] == second.id


def test_import_vna_csv_assigns_the_selected_session(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    session = MeasurementSession(
        id=uuid4(),
        name="Field session",
        created_at=datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
    )
    window._project = window._project.with_measurement_session(
        session,
        updated_at=window._project.updated_at,
    )
    csv_path = tmp_path / "field.csv"
    csv_path.write_text(
        "frequency_hz,r_ohm,x_ohm\n7000000,50,0\n7100000,75,0\n",
        encoding="utf-8",
    )

    class FakeDetailsDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def name(self) -> str:
            return "Field measurement"

        def calibration(self) -> str:
            return "SOL"

        def reference_plane(self) -> str:
            return "antenna terminals"

        def feed_line(self) -> str:
            return "10 m RG-58"

        def notes(self) -> str:
            return "Dry ground"

        def session_id(self) -> object:
            return session.id

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(csv_path), ""),
    )
    monkeypatch.setattr(
        main_window_module,
        "MeasurementDetailsDialog",
        FakeDetailsDialog,
    )

    window.import_vna_csv()

    assert window._project.measurements[0].session_id == session.id
    window._dirty = False
