# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.zepp import ZEPP_RADIATOR_ID, zepp_starting_dimensions
from antennadesk.ui.dialogs.zepp_dialog import ZeppDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_zepp_dialog_builds_the_classic_starting_geometry(qtbot: QtBot) -> None:
    dialog = ZeppDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    radiator_m, line_m = zepp_starting_dimensions(7_100_000.0)
    radiator = next(wire for wire in parameters.wires if wire.id == ZEPP_RADIATOR_ID)
    line = parameters.transmission_lines[0]

    assert parameters.generator_id == "zepp"
    assert radiator.length_m == pytest.approx(radiator_m, abs=1e-3)
    assert line.length_m == pytest.approx(line_m, abs=1e-3)
    assert line.characteristic_impedance_ohm == pytest.approx(400.0)
    assert dialog.windowTitle() == "Zepp Generator"


def test_zepp_dialog_can_reset_starting_dimensions(qtbot: QtBot) -> None:
    dialog = ZeppDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._radiator_length.setValue(1.0)
    dialog._line_length.setValue(1.0)
    dialog._frequency.setValue(14.1)

    dialog._apply_starting_dimensions()

    radiator_m, line_m = zepp_starting_dimensions(14_100_000.0)
    assert dialog._radiator_length.value() == pytest.approx(radiator_m, abs=1e-3)
    assert dialog._line_length.value() == pytest.approx(line_m, abs=1e-3)
