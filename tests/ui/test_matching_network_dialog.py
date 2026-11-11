# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.matching_network import LNetwork
from antennadesk.domain.design.matching_design import MatchingNetworkDesign
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


def test_matching_network_dialog_warns_when_it_overrides_internal_matching(
    qtbot: QtBot,
) -> None:
    dialog = MatchingNetworkDialog(
        Translator(Language.ENGLISH),
        internal_matching_active=True,
    )
    qtbot.addWidget(dialog)

    assert dialog._override_warning.isHidden() is True

    dialog._enabled.setChecked(True)

    assert dialog._override_warning.isHidden() is False
    assert "not cascaded" in dialog._override_warning.text()


def test_matching_network_dialog_hides_the_override_warning_without_internal_matching(
    qtbot: QtBot,
) -> None:
    existing = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    dialog = MatchingNetworkDialog(
        Translator(Language.ENGLISH),
        existing,
        internal_matching_active=False,
    )
    qtbot.addWidget(dialog)

    assert dialog._override_warning.isHidden() is True


def test_matching_network_dialog_preloads_the_stored_design_target(qtbot: QtBot) -> None:
    existing = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    design = MatchingNetworkDesign(
        frequency_hz=7_100_000.0,
        load_resistance_ohm=120.0,
        load_reactance_ohm=-35.0,
        source_impedance_ohm=75.0,
        origin="simulation",
    )

    dialog = MatchingNetworkDialog(
        Translator(Language.ENGLISH),
        existing,
        design=design,
    )
    qtbot.addWidget(dialog)

    assert dialog._frequency.value() == pytest.approx(7.1)
    assert dialog._load_r.value() == pytest.approx(120.0)
    assert dialog._load_x.value() == pytest.approx(-35.0)
    assert dialog._source_impedance.value() == pytest.approx(75.0)
    assert dialog._origin_value.text() == "Current simulation point"
    result = dialog.result_design()
    assert result.frequency_hz == pytest.approx(7_100_000.0)
    assert result.load_resistance_ohm == pytest.approx(120.0)
    assert result.load_reactance_ohm == pytest.approx(-35.0)
    assert result.source_impedance_ohm == pytest.approx(75.0)
    assert result.origin == "simulation"


def test_matching_network_dialog_uses_the_current_simulation_point(qtbot: QtBot) -> None:
    point = MatchingNetworkDesign(
        frequency_hz=14_200_000.0,
        load_resistance_ohm=85.0,
        load_reactance_ohm=12.0,
        source_impedance_ohm=50.0,
        origin="simulation",
    )
    dialog = MatchingNetworkDialog(
        Translator(Language.ENGLISH),
        current_point=point,
    )
    qtbot.addWidget(dialog)

    assert dialog._use_current_point.isEnabled() is True

    dialog._use_current_point.click()

    assert dialog._frequency.value() == pytest.approx(14.2)
    assert dialog._load_r.value() == pytest.approx(85.0)
    assert dialog._load_x.value() == pytest.approx(12.0)
    assert dialog._origin_value.text() == "Current simulation point"
    assert dialog.result_design().origin == "simulation"


def test_matching_network_dialog_disables_the_current_point_without_results(
    qtbot: QtBot,
) -> None:
    dialog = MatchingNetworkDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)

    assert dialog._use_current_point.isEnabled() is False


def test_matching_network_dialog_manual_editing_marks_the_origin(qtbot: QtBot) -> None:
    dialog = MatchingNetworkDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)

    dialog._load_r.setValue(80.0)

    assert dialog._origin_value.text() == "Manual entry"
    assert dialog.result_design().origin == "manual"


def test_matching_network_dialog_shows_only_the_fields_for_each_topology(
    qtbot: QtBot,
) -> None:
    dialog = MatchingNetworkDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)

    assert dialog._series_l.isHidden() is False
    assert dialog._shunt_c.isHidden() is False
    assert dialog._input_shunt_c.isHidden() is True
    assert dialog._input_series_c.isHidden() is True

    dialog._topology.setCurrentIndex(1)

    assert dialog._series_l.isHidden() is False
    assert dialog._shunt_c.isHidden() is True
    assert dialog._input_shunt_c.isHidden() is False
    assert dialog._input_series_c.isHidden() is True
    assert dialog._shunt_at_input.isHidden() is True

    dialog._topology.setCurrentIndex(2)

    assert dialog._series_l.isHidden() is True
    assert dialog._shunt_c.isHidden() is False
    assert dialog._input_shunt_c.isHidden() is True
    assert dialog._input_series_c.isHidden() is False


def test_matching_network_dialog_auto_design_uses_the_source_impedance(
    qtbot: QtBot,
) -> None:
    dialog = MatchingNetworkDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)
    dialog._load_r.setValue(200.0)
    dialog._load_x.setValue(0.0)
    dialog._source_impedance.setValue(100.0)
    dialog._frequency.setValue(10.0)

    dialog._auto.click()
    network = dialog.network()

    assert network is not None
    assert network.input_impedance(complex(200.0, 0.0), 10_000_000.0) == pytest.approx(
        complex(100.0, 0.0),
        abs=0.05,
    )
