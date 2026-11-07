# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QLabel
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.zepp import (
    ZEPP_BASE_ID,
    ZEPP_DEFAULT_SPACING_M,
    ZEPP_MATCHING_FEED_ID,
    ZEPP_RADIATOR_ID,
    zepp_starting_dimensions,
)
from antennadesk.ui.dialogs.zepp_dialog import ZeppDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_zepp_dialog_builds_the_classic_starting_geometry(qtbot: QtBot) -> None:
    dialog = ZeppDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    radiator_m, matching_m = zepp_starting_dimensions(7_100_000.0)
    radiator = next(wire for wire in parameters.wires if wire.id == ZEPP_RADIATOR_ID)
    matching = next(wire for wire in parameters.wires if wire.id == ZEPP_MATCHING_FEED_ID)

    assert parameters.generator_id == "zepp"
    assert parameters.feed.wire_id == ZEPP_BASE_ID
    assert parameters.feed.offset_m == pytest.approx(ZEPP_DEFAULT_SPACING_M / 2.0)
    assert radiator.length_m == pytest.approx(radiator_m, abs=1e-3)
    assert matching.length_m == pytest.approx(matching_m, abs=1e-3)
    assert parameters.transmission_lines == ()
    assert "468.9" in dialog._impedance.text()
    assert dialog.windowTitle() == "Zepp Generator"
    typed = dialog.typed_parameters()
    assert typed.radiator_length_m == pytest.approx(radiator_m, abs=1e-3)
    assert typed.matching_section_length_m == pytest.approx(matching_m, abs=1e-3)
    assert typed.spacing_m == pytest.approx(ZEPP_DEFAULT_SPACING_M)


def test_zepp_dialog_can_reset_starting_dimensions(qtbot: QtBot) -> None:
    dialog = ZeppDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._radiator_length.setValue(1.0)
    dialog._matching_length.setValue(1.0)
    dialog._frequency.setValue(14.1)

    dialog._apply_starting_dimensions()

    radiator_m, matching_m = zepp_starting_dimensions(14_100_000.0)
    assert dialog._radiator_length.value() == pytest.approx(radiator_m, abs=1e-3)
    assert dialog._matching_length.value() == pytest.approx(matching_m, abs=1e-3)


def test_zepp_dialog_reports_the_second_conductor_and_choke(qtbot: QtBot) -> None:
    dialog = ZeppDialog(Translator(Language.SPANISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    hint = dialog.findChildren(QLabel)
    texts = [label.text() for label in hint]

    assert any("dos conductores reales" in text for text in texts)
    assert any("choque de modo común 1:1" in text for text in texts)
