# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.antenna_catalog_dialog import (
    CATALOG_TYPE_LOOP,
    CATALOG_TYPE_YAGI,
    AntennaCatalogDialog,
)
from antennadesk.ui.i18n import Language, Translator


def test_catalog_lists_antenna_types(qtbot: QtBot) -> None:
    dialog = AntennaCatalogDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)

    assert dialog._list.count() == 13
    assert dialog.selected_key() == "wire_dipole"


def test_catalog_selection_and_search(qtbot: QtBot) -> None:
    dialog = AntennaCatalogDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)
    dialog._search.setText("yagi")

    visible = [
        dialog._list.item(row).data(1)
        for row in range(dialog._list.count())
        if not dialog._list.item(row).isHidden()
    ]
    assert visible == [CATALOG_TYPE_YAGI]
    dialog._list.setCurrentRow(
        next(row for row in range(dialog._list.count()) if not dialog._list.item(row).isHidden())
    )
    assert dialog.selected_key() == CATALOG_TYPE_YAGI


def test_catalog_detail_and_loop_selection(qtbot: QtBot) -> None:
    dialog = AntennaCatalogDialog(Translator(Language.SPANISH))
    qtbot.addWidget(dialog)
    row = next(
        row
        for row in range(dialog._list.count())
        if dialog._list.item(row).data(1) == CATALOG_TYPE_LOOP
    )
    dialog._list.setCurrentRow(row)

    assert dialog.selected_key() == CATALOG_TYPE_LOOP
    assert "Evidencia" in dialog._detail.text()
