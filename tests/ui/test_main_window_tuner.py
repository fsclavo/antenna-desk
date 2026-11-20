# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tuner matchability action in the main window."""

from __future__ import annotations

from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


def test_tuner_action_is_in_tools_and_retranslates(window: MainWindow) -> None:
    assert window._tuner_match_action in window._tools_menu.actions()
    assert window._tuner_match_action.text() == "Tuner Matchability..."

    window._set_language(Language.SPANISH)

    assert window._tuner_match_action.text() == "Compatibilidad del sintonizador..."
    window._set_language(Language.ENGLISH)
