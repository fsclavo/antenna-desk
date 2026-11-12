# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed-chain loss budget dialog."""

from __future__ import annotations

from dataclasses import replace

from helpers import make_completed_result
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.matching_network import (
    LNetwork,
    MatchingNetworkPosition,
)
from antennadesk.domain.projects.project import Project
from antennadesk.ui.dialogs.feed_chain_dialog import FeedChainDialog
from antennadesk.ui.i18n import Language, Translator


def _result_with_losses():
    base = make_completed_result()
    frequency = replace(
        base.frequencies[0],
        mismatch_loss_db=0.2,
        feed_line_loss_db=1.5,
        network_loss_db=0.3,
        balun_loss_db=0.5,
    )
    return replace(base, frequencies=(frequency,))


def test_feed_chain_dialog_shows_the_path_and_loss_table(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    project = replace(
        sample_project,
        matching_network=LNetwork(
            series_inductance_h=1e-6,
            shunt_capacitance_f=100e-12,
        ),
        matching_network_position=MatchingNetworkPosition.SHACK,
    )
    dialog = FeedChainDialog(
        Translator(Language.ENGLISH),
        project,
        project.designs[0],
        _result_with_losses(),
    )
    qtbot.addWidget(dialog)

    assert "matching network (shack)" in dialog._path.text()
    assert dialog._table.rowCount() == 1
    assert dialog._table.item(0, 3).text() == "1.50 dB"
    assert dialog._table.item(0, 8).text() == "Line"
    assert "56.23 W" in dialog._table.item(0, 6).text()


def test_feed_chain_dialog_uses_the_feedpoint_path(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    project = replace(
        sample_project,
        matching_network=LNetwork(
            series_inductance_h=1e-6,
            shunt_capacitance_f=100e-12,
        ),
        matching_network_position=MatchingNetworkPosition.FEEDPOINT,
    )
    dialog = FeedChainDialog(
        Translator(Language.ENGLISH),
        project,
        project.designs[0],
        _result_with_losses(),
    )
    qtbot.addWidget(dialog)

    assert "matching network (feedpoint)" in dialog._path.text()


def test_feed_chain_dialog_retranslates(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    dialog = FeedChainDialog(
        Translator(Language.SPANISH),
        sample_project,
        sample_project.designs[0],
        _result_with_losses(),
    )
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Presupuesto de pérdidas de la cadena"
    assert dialog._table.horizontalHeaderItem(3).text() == "Línea"
