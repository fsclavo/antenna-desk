# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.ui.dialogs.feed_line_dialog import FeedLineDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


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
