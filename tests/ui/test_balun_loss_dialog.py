# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.balun import BalunLoss
from antennadesk.ui.dialogs.balun_loss_dialog import BalunLossDialog
from antennadesk.ui.i18n import Language, Translator


def test_balun_loss_dialog_returns_none_when_disabled(qtbot: QtBot) -> None:
    dialog = BalunLossDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)

    assert dialog.result_balun_loss() is None


def test_balun_loss_dialog_edits_frequency_fit(qtbot: QtBot) -> None:
    original = BalunLoss(
        reference_frequency_hz=14_000_000.0,
        reference_loss_db=0.8,
        exponent=0.4,
    )
    dialog = BalunLossDialog(
        Translator(Language.ENGLISH),
        balun_loss=original,
    )
    qtbot.addWidget(dialog)

    dialog._enabled.setChecked(True)
    dialog._reference_loss.setValue(1.0)
    dialog._reference_frequency.setValue(7.0)
    dialog._exponent.setValue(0.5)
    dialog._accept()

    result = dialog.result_balun_loss()
    assert result is not None
    assert result.reference_loss_db == 1.0
    assert result.reference_frequency_hz == 7_000_000.0
    assert result.exponent == 0.5
    assert "28 MHz" in dialog._preview.text()
