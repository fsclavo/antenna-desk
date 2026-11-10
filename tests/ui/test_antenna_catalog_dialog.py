# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.antenna_catalog_dialog import (
    CATALOG_TYPE_HEXBEAM,
    CATALOG_TYPE_LOOP,
    CATALOG_TYPE_MOXON,
    CATALOG_TYPE_T2FD,
    CATALOG_TYPE_TRAP_YAGI,
    CATALOG_TYPE_YAGI,
    ENTRIES,
    KEY_ROLE,
    AntennaCatalogDialog,
)
from antennadesk.ui.i18n import Language, Translator


def test_catalog_lists_antenna_types(qtbot: QtBot) -> None:
    dialog = AntennaCatalogDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)

    assert dialog._list.count() == len(ENTRIES)
    assert dialog.selected_key() == "wire_dipole"
    assert dialog._list.item(0).text() == "Wire dipole"
    assert "catalog." not in dialog._list.item(0).text()


def test_catalog_detail_shows_family_and_evidence(qtbot: QtBot) -> None:
    dialog = AntennaCatalogDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)
    dialog._list.setCurrentRow(0)

    detail = dialog._detail.text()
    assert "Center-fed straight wire" in detail
    assert "Family: Dipole" in detail
    assert "Evidence:" in detail


def test_catalog_selection_and_search(qtbot: QtBot) -> None:
    dialog = AntennaCatalogDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)
    dialog._search.setText("yagi")

    visible = [
        dialog._list.item(row).data(KEY_ROLE)
        for row in range(dialog._list.count())
        if not dialog._list.item(row).isHidden()
    ]
    assert visible == [
        CATALOG_TYPE_TRAP_YAGI,
        CATALOG_TYPE_HEXBEAM,
        CATALOG_TYPE_MOXON,
        CATALOG_TYPE_YAGI,
    ]
    dialog._list.setCurrentRow(
        next(
            row
            for row in range(dialog._list.count())
            if dialog._list.item(row).data(KEY_ROLE) == CATALOG_TYPE_YAGI
        )
    )
    assert dialog.selected_key() == CATALOG_TYPE_YAGI


def test_catalog_finds_the_t2fd_entry(qtbot: QtBot) -> None:
    dialog = AntennaCatalogDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)
    dialog._search.setText("t2fd")

    visible = [
        dialog._list.item(row).data(KEY_ROLE)
        for row in range(dialog._list.count())
        if not dialog._list.item(row).isHidden()
    ]
    assert visible == [CATALOG_TYPE_T2FD]


def test_catalog_can_start_from_the_current_template(qtbot: QtBot) -> None:
    dialog = AntennaCatalogDialog(
        Translator(Language.ENGLISH),
        initial_key=CATALOG_TYPE_YAGI,
    )
    qtbot.addWidget(dialog)

    assert dialog.selected_key() == CATALOG_TYPE_YAGI


def test_catalog_detail_and_loop_selection(qtbot: QtBot) -> None:
    dialog = AntennaCatalogDialog(Translator(Language.SPANISH))
    qtbot.addWidget(dialog)
    row = next(
        row
        for row in range(dialog._list.count())
        if dialog._list.item(row).data(KEY_ROLE) == CATALOG_TYPE_LOOP
    )
    dialog._list.setCurrentRow(row)

    assert dialog.selected_key() == CATALOG_TYPE_LOOP
    assert "Evidencia" in dialog._detail.text()
