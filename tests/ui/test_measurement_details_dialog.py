# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pytestqt.qtbot import QtBot

from antennadesk.domain.measurement import MeasurementSession
from antennadesk.ui.dialogs.measurement_details_dialog import MeasurementDetailsDialog
from antennadesk.ui.i18n import Language, Translator


def test_measurement_details_dialog_returns_conditions(qtbot: QtBot) -> None:
    dialog = MeasurementDetailsDialog(Translator(Language.ENGLISH), "field.csv")
    qtbot.addWidget(dialog)
    dialog._name.setText("40 m field")
    dialog._calibration.setText("SOL")
    dialog._reference_plane.setText("antenna terminals")
    dialog._feed_line.setText("10 m RG-58")
    dialog._notes.setPlainText("Dry ground")

    assert dialog.name() == "40 m field"
    assert dialog.calibration() == "SOL"
    assert dialog.reference_plane() == "antenna terminals"
    assert dialog.feed_line() == "10 m RG-58"
    assert dialog.notes() == "Dry ground"
    assert dialog.session_id() is None


def test_measurement_details_dialog_selects_a_session(qtbot: QtBot) -> None:
    session = MeasurementSession(
        id=uuid4(),
        name="Before tuning",
        created_at=datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
    )
    dialog = MeasurementDetailsDialog(
        Translator(Language.ENGLISH),
        "field.csv",
        sessions=(session,),
        session_id=session.id,
    )
    qtbot.addWidget(dialog)

    assert dialog._session.count() == 2
    assert dialog.session_id() == session.id
    assert "Before tuning" in dialog._session.currentText()
