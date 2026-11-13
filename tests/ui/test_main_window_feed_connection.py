# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed-connection action in the main window."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog

from antennadesk.domain.antennas.feed_connection import FeedConnectionDetail
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


class _FakeFeedConnectionDialog:
    captured: FeedConnectionDetail | None = None

    def __init__(
        self, translator: object, detail: FeedConnectionDetail, parent: object = None
    ) -> None:
        del translator, parent
        type(self).captured = detail

    def exec(self) -> QDialog.DialogCode:
        return QDialog.DialogCode.Accepted


def test_feed_connection_action_is_available_and_retranslates(window: MainWindow) -> None:
    assert window._feed_connection_action in window._design_menu.actions()
    assert window._feed_connection_action.isEnabled()
    assert window._feed_connection_action.text() == "Feed Connection Detail..."

    window._set_language(Language.SPANISH)

    assert window._feed_connection_action.text() == "Detalle de conexión de alimentación..."
    window._set_language(Language.ENGLISH)


def test_show_feed_connection_builds_the_detail(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        main_window_module,
        "FeedConnectionDialog",
        _FakeFeedConnectionDialog,
    )

    window.show_feed_connection()

    detail = _FakeFeedConnectionDialog.captured
    assert detail is not None
    assert detail.summary
    assert detail.connections
