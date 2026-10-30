# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.custom_antenna_dialog import CustomAntennaDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_custom_dialog_builds_a_wire_model(qtbot: QtBot) -> None:
    dialog = CustomAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert len(parameters.wires) == 1
    assert parameters.feed.wire_id == "wire-1"
    assert parameters.wires[0].length_m > 0.0


def test_custom_dialog_adds_a_second_wire(qtbot: QtBot) -> None:
    dialog = CustomAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(dialog)

    dialog._add_wire()
    parameters = dialog.parameters()

    assert len(parameters.wires) == 2
    assert parameters.feed.wire_id == "wire-1"


def test_custom_dialog_adds_ground_radials(qtbot: QtBot) -> None:
    dialog = CustomAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(dialog)

    dialog._radial_count.setValue(4)
    dialog._add_radials.click()
    parameters = dialog.parameters()

    assert len(parameters.wires) == 5
    assert all(wire.id.startswith("radial-") for wire in parameters.wires[1:])
    assert all(wire.start.z_m == 0.0 for wire in parameters.wires[1:])
