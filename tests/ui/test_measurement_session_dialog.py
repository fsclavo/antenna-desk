# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measurement session editor."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from PySide6.QtCore import QDateTime, QTimeZone
from PySide6.QtWidgets import QDialog, QMessageBox
from pytestqt.qtbot import QtBot

from antennadesk.domain.measurement import MeasurementSession
from antennadesk.domain.projects.project import Project
from antennadesk.ui.dialogs.measurement_session_dialog import MeasurementSessionDialog
from antennadesk.ui.i18n import Language, Translator


def test_session_dialog_returns_the_entered_fields(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    dialog = MeasurementSessionDialog(
        Translator(Language.ENGLISH),
        sample_project,
    )
    qtbot.addWidget(dialog)
    dialog._name.setText("Back yard")
    dialog._design.setCurrentIndex(1)
    dialog._location.setText("Back yard")
    dialog._conditions.setPlainText("Dry ground, 8 m")
    dialog._notes.setPlainText("Before trimming")
    target = datetime(2026, 11, 12, 15, 0, tzinfo=UTC)
    dialog._date.setDateTime(QDateTime.fromSecsSinceEpoch(int(target.timestamp()), QTimeZone.utc()))

    assert dialog.name() == "Back yard"
    assert dialog.design_id() == sample_project.designs[0].id
    assert dialog.location() == "Back yard"
    assert dialog.conditions() == "Dry ground, 8 m"
    assert dialog.notes() == "Before trimming"
    assert dialog.created_at() == target


def test_session_dialog_requires_a_name(
    qtbot: QtBot,
    sample_project: Project,
    monkeypatch,
) -> None:
    dialog = MeasurementSessionDialog(
        Translator(Language.ENGLISH),
        sample_project,
    )
    qtbot.addWidget(dialog)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: None)

    dialog.accept()

    assert dialog.result() != QDialog.DialogCode.Accepted


def test_session_dialog_preloads_an_existing_session(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    session = MeasurementSession(
        id=uuid4(),
        name="After tuning",
        created_at=datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
        design_id=sample_project.designs[0].id,
        location="Roof",
        conditions="Cold",
        notes="Trimmed 10 cm",
    )
    dialog = MeasurementSessionDialog(
        Translator(Language.ENGLISH),
        sample_project,
        session=session,
    )
    qtbot.addWidget(dialog)

    assert dialog._name.text() == "After tuning"
    assert dialog.design_id() == session.design_id
    assert dialog._location.text() == "Roof"
    assert dialog._conditions.toPlainText() == "Cold"
    assert dialog._notes.toPlainText() == "Trimmed 10 cm"
    assert dialog.created_at() == session.created_at


def test_session_dialog_uses_spanish_labels(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    dialog = MeasurementSessionDialog(
        Translator(Language.SPANISH),
        sample_project,
    )
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Sesión de medición"
    assert dialog._design.itemText(0) == "Proyecto (todos los diseños)"
