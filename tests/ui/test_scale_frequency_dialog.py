# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.scale_frequency_dialog import ScaleFrequencyDialog
from antennadesk.ui.i18n import Language, Translator


def _dialog(qtbot: QtBot) -> ScaleFrequencyDialog:
    dialog = ScaleFrequencyDialog(
        Translator(Language.ENGLISH),
        144_000_000.0,
    )
    qtbot.addWidget(dialog)
    return dialog


def test_scale_frequency_dialog_prefills_the_current_frequency(
    qtbot: QtBot,
) -> None:
    dialog = _dialog(qtbot)

    assert "144.000000 MHz" in dialog._current.text()
    assert dialog._target.value() == pytest.approx(144.0)
    assert dialog._ok.isEnabled() is False


def test_scale_frequency_dialog_requires_a_different_target(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    dialog._target.setValue(432.0)

    assert dialog._ok.isEnabled() is True
    assert dialog.target_frequency_hz() == pytest.approx(432_000_000.0)


def test_scale_frequency_dialog_help_is_bilingual(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    dialog = ScaleFrequencyDialog(translator, 144_000_000.0)
    qtbot.addWidget(dialog)

    assert "Target design frequency" in dialog._target.toolTip()
    assert "Approximate scaling" in dialog._warning.toolTip()
