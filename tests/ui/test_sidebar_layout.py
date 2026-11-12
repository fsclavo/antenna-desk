# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Layout regression tests for the design and simulation sidebar tabs."""

from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.workflow import WorkflowMode


def test_sidebar_tabs_keep_their_content_above_minimum_height(
    window: MainWindow,
    qtbot: QtBot,
) -> None:
    window._set_workflow_mode(WorkflowMode.ADVANCED, save=False)
    window.resize(1_100, 800)
    window.show()
    qtbot.wait(20)

    assert window._sidebar_tabs.currentWidget() is window._simulation_tab
    assert window._advanced_body.height() >= window._advanced_body.minimumSizeHint().height()
    assert window._sweep_group.height() >= window._sweep_group.minimumSizeHint().height()

    for control in (
        window._sweep_mode,
        window._sweep_start,
        window._sweep_stop,
        window._sweep_points,
    ):
        assert control.height() > 0
        assert control.height() >= control.minimumSizeHint().height()

    window._sidebar_tabs.setCurrentWidget(window._design_tab)
    qtbot.wait(20)

    assert window._design_stack.height() >= window._design_stack.minimumSizeHint().height()
