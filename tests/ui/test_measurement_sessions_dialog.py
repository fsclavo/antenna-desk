# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measurement session timeline dialog."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from PySide6.QtWidgets import QDialog, QMessageBox
from pytestqt.qtbot import QtBot

from antennadesk.domain.measurement import (
    Measurement,
    MeasurementPoint,
    MeasurementSession,
)
from antennadesk.domain.projects.project import Project
from antennadesk.ui.dialogs import measurement_sessions_dialog as dialog_module
from antennadesk.ui.dialogs.measurement_sessions_dialog import MeasurementSessionsDialog
from antennadesk.ui.i18n import Language, Translator

_SESSION_A = UUID("00000000-0000-0000-0000-000000000031")
_SESSION_B = UUID("00000000-0000-0000-0000-000000000032")


def _measurement(
    name: str,
    created_at: datetime,
    session_id: UUID | None,
) -> Measurement:
    return Measurement(
        id=uuid4(),
        name=name,
        created_at=created_at,
        reference_impedance_ohm=50.0,
        points=(MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),),
        session_id=session_id,
    )


def _project(sample_project: Project) -> Project:
    first = MeasurementSession(
        id=_SESSION_A,
        name="Before tuning",
        created_at=datetime(2026, 11, 12, 14, 0, tzinfo=UTC),
        design_id=sample_project.designs[0].id,
        location="Back yard",
    )
    second = MeasurementSession(
        id=_SESSION_B,
        name="After tuning",
        created_at=datetime(2026, 11, 12, 16, 0, tzinfo=UTC),
        design_id=sample_project.designs[0].id,
        location="Roof",
    )
    project = sample_project.with_measurement_session(
        first,
        updated_at=sample_project.updated_at,
    ).with_measurement_session(
        second,
        updated_at=sample_project.updated_at,
    )
    for measurement in (
        _measurement("Before sweep", datetime(2026, 11, 12, 14, 5, tzinfo=UTC), _SESSION_A),
        _measurement("After sweep", datetime(2026, 11, 12, 16, 5, tzinfo=UTC), _SESSION_B),
        _measurement("Unassigned sweep", datetime(2026, 11, 12, 17, 0, tzinfo=UTC), None),
    ):
        project = project.with_measurement(
            measurement,
            updated_at=sample_project.updated_at,
        )
    return project


def test_timeline_lists_sessions_newest_first_and_unassigned(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    dialog = MeasurementSessionsDialog(
        Translator(Language.ENGLISH),
        _project(sample_project),
    )
    qtbot.addWidget(dialog)

    assert dialog._tree.topLevelItemCount() == 3
    assert dialog._tree.topLevelItem(0).text(1) == "After tuning"
    assert dialog._tree.topLevelItem(1).text(1) == "Before tuning"
    assert dialog._tree.topLevelItem(2).text(1) == "Unassigned measurements"

    dialog._tree.setCurrentItem(dialog._tree.topLevelItem(1))
    assert dialog._measurements_table.rowCount() == 1
    assert dialog._measurements_table.item(0, 0).text() == "Before sweep"

    dialog._tree.setCurrentItem(dialog._tree.topLevelItem(2))
    assert dialog._measurements_table.rowCount() == 1
    assert "without a session" in dialog._details.text().lower()


def test_new_and_edit_session_update_the_resulting_project(
    qtbot: QtBot,
    sample_project: Project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSessionDialog:
        name_value = "New session"

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def name(self) -> str:
            return type(self).name_value

        def created_at(self) -> datetime:
            return datetime(2026, 11, 12, 18, 0, tzinfo=UTC)

        def design_id(self) -> UUID | None:
            return None

        def location(self) -> str:
            return "Park"

        def conditions(self) -> str:
            return "Portable"

        def notes(self) -> str:
            return ""

    monkeypatch.setattr(dialog_module, "MeasurementSessionDialog", FakeSessionDialog)
    dialog = MeasurementSessionsDialog(
        Translator(Language.ENGLISH),
        _project(sample_project),
    )
    qtbot.addWidget(dialog)

    dialog._new.click()
    assert len(dialog.result_project().measurement_sessions) == 3

    dialog._tree.setCurrentItem(dialog._tree.topLevelItem(0))
    FakeSessionDialog.name_value = "New session revised"
    dialog._edit.click()
    assert dialog.result_project().measurement_sessions[-1].name == "New session revised"


def test_delete_session_keeps_measurements_unassigned(
    qtbot: QtBot,
    sample_project: Project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dialog = MeasurementSessionsDialog(
        Translator(Language.ENGLISH),
        _project(sample_project),
    )
    qtbot.addWidget(dialog)
    dialog._tree.setCurrentItem(dialog._tree.topLevelItem(0))
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    dialog._delete.click()

    project = dialog.result_project()
    assert [session.id for session in project.measurement_sessions] == [_SESSION_A]
    assert any(
        measurement.name == "After sweep" and measurement.session_id is None
        for measurement in project.measurements
    )


def test_edit_measurement_assigns_a_session(
    qtbot: QtBot,
    sample_project: Project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeDetailsDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def name(self) -> str:
            return "Unassigned sweep"

        def calibration(self) -> str:
            return ""

        def reference_plane(self) -> str:
            return ""

        def feed_line(self) -> str:
            return ""

        def notes(self) -> str:
            return ""

        def session_id(self) -> UUID:
            return _SESSION_A

    monkeypatch.setattr(dialog_module, "MeasurementDetailsDialog", FakeDetailsDialog)
    dialog = MeasurementSessionsDialog(
        Translator(Language.ENGLISH),
        _project(sample_project),
    )
    qtbot.addWidget(dialog)
    dialog._tree.setCurrentItem(dialog._tree.topLevelItem(2))
    dialog._measurements_table.setCurrentCell(0, 0)

    dialog._edit_measurement.click()

    project = dialog.result_project()
    assert "Unassigned sweep" in {
        measurement.name for measurement in project.measurements_for_session(_SESSION_A)
    }


def test_compare_opens_the_comparison_dialog(
    qtbot: QtBot,
    sample_project: Project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeComparisonDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured["args"] = args
            captured["kwargs"] = kwargs

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(
        dialog_module,
        "MeasurementComparisonDialog",
        FakeComparisonDialog,
    )
    dialog = MeasurementSessionsDialog(
        Translator(Language.ENGLISH),
        _project(sample_project),
    )
    qtbot.addWidget(dialog)

    dialog._compare.click()

    assert captured["args"]
    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["initial_before_id"] != kwargs["initial_after_id"]
