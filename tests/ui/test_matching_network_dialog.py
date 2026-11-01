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


def test_matching_network_dialog_auto_designs_an_l_network(qtbot: QtBot) -> None:
    dialog = MatchingNetworkDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)
    dialog._load_r.setValue(100.0)
    dialog._load_x.setValue(0.0)
    dialog._frequency.setValue(10.0)

    dialog._auto.click()
    network = dialog.network()

    assert network is not None
    assert network.input_impedance(complex(100.0, 0.0), 10_000_000.0) == pytest.approx(
        complex(50.0, 0.0), abs=0.05
    )


def test_matching_network_dialog_builds_pi_and_t_topologies(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.matching_network import PiNetwork, TNetwork

    dialog = MatchingNetworkDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)
    dialog._enabled.setChecked(True)
    dialog._topology.setCurrentIndex(1)
    dialog._series_l.setValue(1.0)
    dialog._input_shunt_c.setValue(100.0)
    dialog._output_shunt_c.setValue(120.0)

    pi = dialog.network()
    assert isinstance(pi, PiNetwork)
    assert pi.input_shunt_capacitance_f == pytest.approx(100e-12)

    dialog._topology.setCurrentIndex(2)
    dialog._input_series_l.setValue(1.0)
    dialog._shunt_c.setValue(100.0)
    dialog._output_series_l.setValue(1.0)

    t = dialog.network()
    assert isinstance(t, TNetwork)
    assert t.shunt_capacitance_f == pytest.approx(100e-12)
