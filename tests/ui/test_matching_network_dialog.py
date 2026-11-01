# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.matching_network import LNetwork
from antennadesk.ui.dialogs.matching_network_dialog import MatchingNetworkDialog
from antennadesk.ui.i18n import Language, Translator


def test_matching_network_dialog_builds_an_l_network(qtbot: QtBot) -> None:
    dialog = MatchingNetworkDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)
    dialog._enabled.setChecked(True)
    dialog._series_l.setValue(1.0)
    dialog._series_c.setValue(0.0)
    dialog._shunt_l.setValue(0.0)
    dialog._shunt_c.setValue(100.0)

    network = dialog.network()

    assert network is not None
    assert network.series_inductance_h == pytest.approx(1e-6)
    assert network.shunt_capacitance_f == pytest.approx(100e-12)


def test_matching_network_dialog_can_disable_the_network(qtbot: QtBot) -> None:
    existing = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    dialog = MatchingNetworkDialog(Translator(Language.ENGLISH), existing)
    qtbot.addWidget(dialog)
    dialog._enabled.setChecked(False)

    assert dialog.network() is None
