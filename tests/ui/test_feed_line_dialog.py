# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.design.materials_reference import COAX_REFERENCES, CoaxReference
from antennadesk.ui.dialogs.feed_line_dialog import FeedLineDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _select_catalog(dialog: FeedLineDialog, key: str) -> None:
    index = next(index for index, entry in enumerate(COAX_REFERENCES) if entry.key == key)
    dialog._catalog.setCurrentIndex(index + 1)


def test_feed_line_dialog_defaults_to_disabled(qtbot: QtBot) -> None:
    dialog = FeedLineDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert dialog.feed_line() is None
    assert dialog._impedance.isEnabled() is False


def test_feed_line_dialog_returns_configured_line(qtbot: QtBot) -> None:
    dialog = FeedLineDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._enabled.setChecked(True)
    dialog._impedance.setValue(75.0)
    dialog._length.setValue(30.0)
    dialog._velocity_factor.setValue(0.8)
    dialog._loss.setValue(1.5)

    line = dialog.feed_line()

    assert line == FeedLine(
        characteristic_impedance_ohm=75.0,
        length_m=30.0,
        velocity_factor=0.8,
        matched_loss_db_per_100m=1.5,
    )


def test_feed_line_dialog_restores_an_existing_line(qtbot: QtBot) -> None:
    existing = FeedLine(
        characteristic_impedance_ohm=75.0,
        length_m=30.0,
        velocity_factor=0.8,
        matched_loss_db_per_100m=1.5,
    )
    dialog = FeedLineDialog(
        Translator(Language.ENGLISH),
        UnitSystem.IMPERIAL,
        existing,
    )
    qtbot.addWidget(dialog)

    assert dialog._enabled.isChecked() is True
    restored = dialog.feed_line()
    assert restored is not None
    assert restored.characteristic_impedance_ohm == pytest.approx(75.0)
    assert restored.length_m == pytest.approx(30.0, abs=0.001)
    assert restored.velocity_factor == pytest.approx(0.8)
    assert restored.matched_loss_db_per_100m == pytest.approx(1.5)


def test_feed_line_dialog_catalog_fills_values(qtbot: QtBot) -> None:
    dialog = FeedLineDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    _select_catalog(dialog, "rg213")

    assert dialog._enabled.isChecked() is True
    assert dialog._impedance.value() == pytest.approx(50.0)
    assert dialog._velocity_factor.value() == pytest.approx(0.66)
    assert dialog._loss.value() == pytest.approx(6.23)
    assert dialog._length.value() == pytest.approx(10.0)
    assert "100 MHz" in dialog._catalog_hint.text()
    assert dialog._catalog.toolTip()
    assert dialog._catalog_hint.toolTip()
    assert dialog.feed_line() is not None


def test_feed_line_dialog_manual_edit_switches_to_custom(qtbot: QtBot) -> None:
    dialog = FeedLineDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    _select_catalog(dialog, "lmr400")

    dialog._impedance.setValue(75.0)

    assert dialog._catalog.currentData() is None
    assert "Custom values" in dialog._catalog_hint.text()


def test_feed_line_dialog_restores_a_unique_catalog_entry(qtbot: QtBot) -> None:
    existing = FeedLine(
        characteristic_impedance_ohm=50.0,
        length_m=20.0,
        velocity_factor=0.84,
        matched_loss_db_per_100m=5.0,
    )
    dialog = FeedLineDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        existing,
    )
    qtbot.addWidget(dialog)

    selected = dialog._catalog.currentData()
    assert isinstance(selected, CoaxReference)
    assert selected.key == "lmr400"
    assert "150 MHz" in dialog._catalog_hint.text()


def test_feed_line_dialog_duplicate_values_show_custom(qtbot: QtBot) -> None:
    existing = FeedLine(
        characteristic_impedance_ohm=50.0,
        length_m=20.0,
        velocity_factor=0.66,
        matched_loss_db_per_100m=6.23,
    )
    dialog = FeedLineDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        existing,
    )
    qtbot.addWidget(dialog)

    assert dialog._catalog.currentData() is None
    assert "Custom values" in dialog._catalog_hint.text()


def test_feed_line_dialog_catalog_keeps_length_editable(qtbot: QtBot) -> None:
    dialog = FeedLineDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    _select_catalog(dialog, "rg58a")
    dialog._length.setValue(25.0)

    selected = dialog._catalog.currentData()
    assert isinstance(selected, CoaxReference)
    assert selected.key == "rg58a"
    line = dialog.feed_line()
    assert line is not None
    assert line.length_m == pytest.approx(25.0)


def test_feed_line_dialog_catalog_is_translated(qtbot: QtBot) -> None:
    dialog = FeedLineDialog(Translator(Language.SPANISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    _select_catalog(dialog, "rg213")

    assert dialog._catalog.itemText(0) == "Personalizado"
    assert dialog._catalog.currentText() == "RG-213/U"
    assert "Punto de hoja de datos" in dialog._catalog_hint.text()
