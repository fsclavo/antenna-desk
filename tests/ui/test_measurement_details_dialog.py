# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

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
