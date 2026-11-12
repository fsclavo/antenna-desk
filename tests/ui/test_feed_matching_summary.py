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


def test_summary_shows_an_inactive_project_network(qtbot: QtBot) -> None:
    summary = FeedMatchingSummary(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(summary)
    summary.set_state(shortened_efhw_80_10_parameters(), LNetwork(), None, None)

    assert "inactive" in summary._project_value.text()
    assert "(active)" in summary._endfed_value.text()
    assert summary._warning_container.isHidden() is True
