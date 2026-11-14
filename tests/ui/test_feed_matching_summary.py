# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed & matching summary visibility and translation."""

from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.balun import BalunLoss
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters
from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.antennas.matching_network import LNetwork
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.design.feed_connection import feed_connection_detail
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.feed_matching_summary import FeedMatchingSummary


def _project_network() -> LNetwork:
    return LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)


def test_summary_shows_override_and_the_project_chain(qtbot: QtBot) -> None:
    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    summary.set_state(
        shortened_efhw_80_10_parameters(),
        _project_network(),
        FeedLine(characteristic_impedance_ohm=50.0, length_m=5.0, velocity_factor=0.8),
        BalunLoss(reference_frequency_hz=7_000_000.0, reference_loss_db=0.5),
    )

    assert "retained, not applied" in summary._endfed_value.text()
    assert "100 pF" in summary._endfed_value.text()
    assert "0.198 µH" in summary._endfed_value.text()
    assert "L network" in summary._project_value.text()
    assert "active" in summary._project_value.text()
    assert "at feedpoint" in summary._project_value.text()
    assert "50 Ω" in summary._feed_line_value.text()
    assert "5.00 m" in summary._feed_line_value.text()
    assert "0.50 dB" in summary._balun_value.text()
    assert summary._warning_container.isHidden() is False


def test_summary_hides_the_override_warning_without_an_override(qtbot: QtBot) -> None:
    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    summary.set_state(shortened_efhw_80_10_parameters(), None, None, None)

    assert "(active)" in summary._endfed_value.text()
    assert summary._project_value.text() == "None"
    assert summary._feed_line_value.text() == "None"
    assert summary._balun_value.text() == "None"
    assert summary._warning_container.isHidden() is True


def test_summary_shows_the_design_specific_l_network(qtbot: QtBot) -> None:
    from dataclasses import replace

    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    parameters = replace(
        shortened_efhw_80_10_parameters(),
        design_matching_network=LNetwork(
            series_inductance_h=1.2e-6,
            shunt_capacitance_f=82e-12,
        ),
    )

    summary.set_state(parameters, None, None, None)

    text = summary._endfed_value.text()
    assert "L network" in text
    assert "1.2 µH" in text
    assert "82 pF" in text
    assert "active" in text


def test_summary_shows_a_pi_design_network(qtbot: QtBot) -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.matching_network import PiNetwork

    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    parameters = replace(
        shortened_efhw_80_10_parameters(),
        design_matching_network=PiNetwork(
            input_shunt_capacitance_f=120e-12,
            series_inductance_h=1.1e-6,
            output_shunt_capacitance_f=68e-12,
        ),
    )

    summary.set_state(parameters, None, None, None)

    text = summary._endfed_value.text()
    assert "Pi network" in text
    assert "120 pF" in text
    assert "1.1 µH" in text
    assert "68 pF" in text
    assert "active" in text


def test_summary_reports_not_applicable_for_non_endfed_designs(qtbot: QtBot) -> None:
    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    summary.set_state(
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        _project_network(),
        None,
        None,
    )

    assert summary._endfed_value.text() == "Not applicable"
    assert summary._warning_container.isHidden() is True


def test_summary_retranslates_its_rows_and_warning(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    summary = FeedMatchingSummary(translator, UnitSystem.IMPERIAL)
    qtbot.addWidget(summary)
    summary.set_state(
        shortened_efhw_80_10_parameters(),
        _project_network(),
        FeedLine(length_m=5.0),
        None,
    )

    assert summary.title() == "Feed && matching"
    assert "retained, not applied" in summary._endfed_value.text()

    translator.set_language(Language.SPANISH)
    summary.retranslate()

    assert summary.title() == "Alimentación y adaptación"
    assert "retenida, no aplicada" in summary._endfed_value.text()
    assert "Red L" in summary._project_value.text()
    assert "FV" in summary._feed_line_value.text()
    assert "reemplaza" in summary._warning.text()


def test_summary_shows_the_physical_feed_connection(qtbot: QtBot) -> None:
    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
    )
    detail = feed_connection_detail(parameters, parameters.to_antenna())

    summary.set_state(parameters, None, None, None, feed_detail=detail)

    assert summary._connection_label.text() == "Connection"
    assert "Direct coax" in summary._connection_value.text()
    assert summary._connection_button.isEnabled() is True
    with qtbot.waitSignal(summary.feed_connection_requested):
        summary._connection_button.click()


def test_summary_disables_the_connection_button_without_a_detail(qtbot: QtBot) -> None:
    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)

    summary.set_state(
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
        None,
        None,
        None,
    )

    assert summary._connection_value.text() == "Not available"
    assert summary._connection_button.isEnabled() is False


def test_summary_emits_edit_and_remove_actions(qtbot: QtBot) -> None:
    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    summary.set_state(shortened_efhw_80_10_parameters(), _project_network(), None, None)
    emitted: list[str] = []
    summary.edit_network_requested.connect(lambda: emitted.append("edit"))
    summary.remove_network_requested.connect(lambda: emitted.append("remove"))

    summary._edit_button.click()
    summary._remove_button.click()

    assert emitted == ["edit", "remove"]


def test_summary_flags_a_balanced_feed_without_a_current_balun(qtbot: QtBot) -> None:
    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    summary.set_state(
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
        None,
        None,
        None,
    )

    assert summary._current_balun.isChecked() is False
    assert "normally required" in summary._balance_note.text()
    assert summary._current_balun.isEnabled() is True


def test_summary_records_a_current_balun_and_emits_the_change(qtbot: QtBot) -> None:
    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    summary.set_state(
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
        None,
        None,
        None,
        current_balun=True,
    )
    changes: list[bool] = []
    summary.current_balun_changed.connect(changes.append)

    assert summary._current_balun.isChecked() is True
    assert "is recorded" in summary._balance_note.text()

    summary._current_balun.setChecked(False)

    assert changes == [False]


def test_summary_marks_an_unbalanced_feed_as_not_requiring_a_balun(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    summary.set_state(
        VerticalParameters(frequency_hz=14_100_000.0, height_m=5.0),
        None,
        None,
        None,
    )

    assert "not required" in summary._balance_note.text()


def test_summary_shows_an_inactive_project_network(qtbot: QtBot) -> None:
    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    summary.set_state(shortened_efhw_80_10_parameters(), LNetwork(), None, None)

    assert "inactive" in summary._project_value.text()
    assert "(active)" in summary._endfed_value.text()
    assert summary._warning_container.isHidden() is True
