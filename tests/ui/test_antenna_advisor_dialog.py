# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided antenna advisor dialog behavior."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.antenna_advisor_dialog import AntennaAdvisorDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog(qtbot: QtBot, *, language: Language = Language.ENGLISH):
    dialog = AntennaAdvisorDialog(Translator(language), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    return dialog


def _set_band(dialog: AntennaAdvisorDialog, band: str, checked: bool) -> None:
    for row in range(dialog._bands.count()):
        item = dialog._bands.item(row)
        if item.data(Qt.ItemDataRole.UserRole) == band:
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            return
    raise AssertionError(f"band not found: {band}")


def test_defaults_have_no_results_until_the_user_searches(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    assert dialog._table.rowCount() == 0
    assert not dialog._buttons.button(QDialogButtonBox.Ok).isEnabled()


def test_find_populates_a_shortlist_and_selects_the_first_candidate(
    qtbot: QtBot,
) -> None:
    dialog = _dialog(qtbot)

    dialog._find_candidates()

    assert dialog._table.rowCount() > 0
    assert dialog._table.rowCount() <= 3
    assert dialog.selected_catalog_key() is not None
    assert dialog._buttons.button(QDialogButtonBox.Ok).isEnabled()
    assert "Why it fits" in dialog._details.text()


def test_accept_returns_the_selected_catalog_key(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._find_candidates()
    selected = dialog.selected_catalog_key()

    dialog.accept()

    assert selected is not None
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.selected_catalog_key() == selected


def test_no_match_explains_the_blockers(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    _set_band(dialog, "40m", False)
    _set_band(dialog, "20m", False)
    _set_band(dialog, "10m", False)
    _set_band(dialog, "80m", True)
    _set_band(dialog, "30m", True)
    _set_band(dialog, "17m", True)
    _set_band(dialog, "15m", True)
    _set_band(dialog, "12m", True)
    dialog._width.setValue(1.0)
    dialog._find_candidates()

    assert dialog._table.rowCount() == 0
    assert "No catalog antenna" in dialog._details.text()
    assert "available space" in dialog._details.text()


def test_no_bands_asks_for_a_selection(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    for row in range(dialog._bands.count()):
        dialog._bands.item(row).setCheckState(Qt.CheckState.Unchecked)

    dialog._find_candidates()

    assert dialog._table.rowCount() == 0
    assert "Select at least one band" in dialog._details.text()


def test_initial_profile_values_are_applied(qtbot: QtBot) -> None:
    dialog = AntennaAdvisorDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        initial_height_m=12.0,
        initial_width_m=30.0,
        portable=True,
    )
    qtbot.addWidget(dialog)

    assert dialog._height.value() == 12.0
    assert dialog._width.value() == 30.0
    assert dialog._installation.currentData() is True


def test_spanish_labels_are_translated(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot, language=Language.SPANISH)

    assert dialog.windowTitle() == "Asesor de antenas"
    assert dialog._find.text() == "Buscar antenas"
    assert dialog._buttons.button(QDialogButtonBox.Ok).text() == "Abrir diseño seleccionado"


def test_table_headers_are_localized(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._find_candidates()

    headers = [
        dialog._table.horizontalHeaderItem(column).text()
        for column in range(dialog._table.columnCount())
    ]
    assert headers[0] == "Antenna"
    assert headers[1] == "Fit"
    assert headers[-1] == "Build"
