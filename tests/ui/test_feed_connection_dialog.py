# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed-connection detail dialog."""

from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.design.feed_connection import feed_connection_detail
from antennadesk.ui.dialogs.feed_connection_dialog import FeedConnectionDialog
from antennadesk.ui.i18n import Language, Translator


def _detail():
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
    )
    return feed_connection_detail(parameters, parameters.to_antenna())


def test_dialog_shows_schematic_table_and_states(qtbot: QtBot) -> None:
    dialog = FeedConnectionDialog(Translator(Language.ENGLISH), _detail())
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Feed connection detail"
    assert dialog._table.rowCount() == 2
    assert dialog._table.columnCount() == 3
    assert dialog._table.horizontalHeaderItem(0).text() == "From"
    assert dialog._table.horizontalHeaderItem(1).text() == "To"
    assert dialog._table.item(0, 1).text() == "Coax center"
    assert dialog._schematic.renderer().isValid()
    assert "current balun/choke is recommended" in dialog._summary.text()
    assert "Common-mode current" in dialog._not_modeled.findChild(type(dialog._summary)).text()


def test_dialog_retranslates_to_spanish(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    dialog = FeedConnectionDialog(translator, _detail())
    qtbot.addWidget(dialog)

    translator.set_language(Language.SPANISH)
    dialog.retranslate()

    assert dialog.windowTitle() == "Detalle de conexión de alimentación"
    assert dialog._table.horizontalHeaderItem(0).text() == "Desde"
    assert dialog._table.item(0, 1).text() == "Centro del coaxil"
    assert "Coaxil directo" in dialog._summary.text()
    assert "modo común" in dialog._not_modeled.findChild(type(dialog._summary)).text()
