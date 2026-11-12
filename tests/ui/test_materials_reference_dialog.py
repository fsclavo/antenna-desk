# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Materials reference dialog behavior."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.design.materials_reference import (
    COAX_REFERENCES,
    FERRITE_REFERENCES,
    INSULATOR_REFERENCES,
    WIRE_REFERENCES,
)
from antennadesk.ui.dialogs.materials_reference_dialog import MaterialsReferenceDialog
from antennadesk.ui.i18n import Language, Translator


def _dialog(
    qtbot: QtBot,
    *,
    feed_line: FeedLine | None = None,
    can_apply: bool = True,
    translator: Translator | None = None,
) -> MaterialsReferenceDialog:
    dialog = MaterialsReferenceDialog(
        translator or Translator(Language.ENGLISH),
        feed_line=feed_line,
        can_apply=can_apply,
    )
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_exposes_all_reference_tables(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    assert dialog._tabs.count() == 4
    assert dialog._tables["wire"].rowCount() == len(WIRE_REFERENCES)
    assert dialog._tables["coax"].rowCount() == len(COAX_REFERENCES)
    assert dialog._tables["ferrite"].rowCount() == len(FERRITE_REFERENCES)
    assert dialog._tables["insulator"].rowCount() == len(INSULATOR_REFERENCES)
    assert dialog._details.text()
    assert "Copper" in dialog._details.text()
    assert "https://" in dialog._details.text()
    assert "Revision" in dialog._details.text()
    assert dialog._details.toolTip()
    assert dialog._apply_button.toolTip()


def _coax_row(key: str) -> int:
    return next(index for index, entry in enumerate(COAX_REFERENCES) if entry.key == key)


def test_dialog_selection_updates_the_details(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._tabs.setCurrentIndex(1)
    dialog._tables["coax"].selectRow(_coax_row("lmr400"))

    assert "LMR-400" in dialog._details.text()
    assert "150 MHz" in dialog._details.text()
    assert "150 MHz" not in dialog._tables["coax"].item(0, 4).text()


def test_dialog_applies_a_coax_preset_and_preserves_length(qtbot: QtBot) -> None:
    existing = FeedLine(
        characteristic_impedance_ohm=75.0,
        length_m=23.0,
        velocity_factor=0.8,
        matched_loss_db_per_100m=1.5,
    )
    dialog = _dialog(qtbot, feed_line=existing)
    dialog._tabs.setCurrentIndex(1)
    dialog._tables["coax"].selectRow(_coax_row("rg213"))

    dialog._apply_button.click()

    result = dialog.result_feed_line()
    assert result is not None
    assert result.length_m == pytest.approx(23.0)
    assert result.characteristic_impedance_ohm == pytest.approx(50.0)
    assert result.velocity_factor == pytest.approx(0.66)
    assert result.matched_loss_db_per_100m == pytest.approx(6.23)


def test_dialog_apply_is_disabled_without_a_project(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot, can_apply=False)

    assert dialog._apply_button.isEnabled() is False
    assert "Open a project" in dialog._apply_hint.text()


def test_dialog_is_translated_to_spanish(qtbot: QtBot) -> None:
    translator = Translator(Language.SPANISH)
    dialog = _dialog(qtbot, translator=translator)
    dialog._tabs.setCurrentIndex(0)
    dialog._tables["wire"].selectRow(0)

    assert dialog.windowTitle() == "Referencia de materiales"
    assert dialog._tabs.tabText(0) == "Alambre"
    assert "Cobre" in dialog._details.text()
    assert "Fuente" in dialog._details.text()


def test_dialog_uses_the_default_length_for_a_new_line(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot, feed_line=None)
    dialog._tabs.setCurrentIndex(1)
    dialog._tables["coax"].selectRow(0)

    dialog._apply_button.click()

    result = dialog.result_feed_line()
    assert result is not None
    assert result.length_m == pytest.approx(10.0)
