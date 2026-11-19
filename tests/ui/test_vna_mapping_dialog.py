# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Manual VNA column-mapping fallback."""

from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.importers.vna_csv import VnaColumnMapping
from antennadesk.ui.dialogs.vna_mapping_dialog import VnaMappingDialog
from antennadesk.ui.i18n import Language, Translator


def test_mapping_dialog_returns_the_selected_columns(qtbot: QtBot) -> None:
    dialog = VnaMappingDialog(
        Translator(Language.ENGLISH),
        ("frequency_hz", "foo", "bar"),
        initial=VnaColumnMapping(
            frequency="frequency_hz",
            mode="rx",
            first="foo",
            second="bar",
        ),
    )
    qtbot.addWidget(dialog)

    mapping = dialog.mapping()

    assert mapping.frequency == "frequency_hz"
    assert mapping.first == "foo"
    assert mapping.second == "bar"
    assert mapping.mode == "rx"
    assert "columns" in dialog.windowTitle().lower()
