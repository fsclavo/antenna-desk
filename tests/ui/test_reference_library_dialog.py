# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reference design library dialog behavior."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.design.reference_library import REFERENCE_DESIGNS
from antennadesk.ui.dialogs.reference_library_dialog import ReferenceLibraryDialog
from antennadesk.ui.i18n import Language, Translator


def _dialog(
    qtbot: QtBot,
    *,
    language: Language = Language.ENGLISH,
) -> ReferenceLibraryDialog:
    dialog = ReferenceLibraryDialog(Translator(language))
    qtbot.addWidget(dialog)
    return dialog


def test_library_lists_every_curated_reference(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    assert dialog.windowTitle() == "Reference design library"
    assert dialog._list.count() == len(REFERENCE_DESIGNS) == 12
    assert dialog._list.currentRow() == 0
    assert dialog.selected_reference() == REFERENCE_DESIGNS[0]
    assert dialog._open.isEnabled() is True
    assert dialog._simulate.isChecked() is True


def test_library_details_show_published_and_modeled_scope(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    text = dialog._details.text()

    assert "40 m half-wave wire dipole" in text
    assert "Published reference" in text
    assert "Modeled here" in text
    assert "Source" in text
    assert "Published tolerance" in text
    assert "Limits" in text
    assert "A — reference-backed" in text


def test_library_search_filters_and_selects_a_match(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    dialog._search.setText("moxon")

    assert dialog._list.currentRow() == 1
    assert dialog.selected_reference() is not None
    assert dialog.selected_reference().key == "cebik_moxon_20m"
    assert "Moxon" in dialog._details.text()
    assert sum(not dialog._list.item(row).isHidden() for row in range(dialog._list.count())) == 1


def test_library_search_without_a_match_blocks_opening(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    dialog._search.setText("no such reference")

    assert dialog.selected_reference() is None
    assert dialog._open.isEnabled() is False
    assert "No reference design" in dialog._details.text()


def test_library_retranslates_items_and_details(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    dialog = ReferenceLibraryDialog(translator)
    qtbot.addWidget(dialog)

    translator.set_language(Language.SPANISH)
    dialog.retranslate()

    assert dialog.windowTitle() == "Biblioteca de diseños de referencia"
    assert dialog._list.item(0).text().startswith("Dipolo de hilo de media onda")
    assert "Referencia publicada" in dialog._details.text()
    assert "A — con referencia" in dialog._details.text()


def test_library_open_accepts_with_the_selected_design(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._list.setCurrentRow(3)

    dialog._open.click()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.selected_reference() is not None
    assert dialog.selected_reference().key == "w3dzz_trap_dipole"
