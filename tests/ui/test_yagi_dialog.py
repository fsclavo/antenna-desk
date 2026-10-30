# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.ui.dialogs.yagi_dialog import YagiDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_yagi_dialog_loads_the_nbs_preset(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert dialog._table.rowCount() == 5
    assert dialog._driven.currentData() == 1
    parameters = dialog.parameters()
    assert len(parameters.wires) == 5
    assert parameters.feed.wire_id == "element-2"


def test_yagi_dialog_can_add_and_remove_elements(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    dialog._add_element()
    assert dialog._table.rowCount() == 6
    parameters = dialog.parameters()
    assert len(parameters.wires) == 6

    dialog._table.selectRow(5)
    dialog._remove_element()
    assert dialog._table.rowCount() == 5


def test_yagi_dialog_rebuilds_geometry_from_edited_lengths(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._table.item(1, 2).setText("10.000")

    parameters = dialog.parameters()

    assert parameters.wires[1].length_m == pytest.approx(10.0, abs=0.001)


def test_yagi_dialog_driven_element_mapping_survives_reordering(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._table.item(0, 1).setText("2.000")

    parameters = dialog.parameters()
    yagi = YagiParameters(
        frequency_hz=parameters.frequency_hz,
        elements=tuple(
            YagiElement(
                position_m=float(dialog._table.item(row, 1).text()),
                length_m=float(dialog._table.item(row, 2).text()),
                radius_m=float(dialog._table.item(row, 3).text()) / 1_000.0,
            )
            for row in range(dialog._table.rowCount())
        ),
        height_m=12.0,
        driven_index=1,
    )

    assert yagi.elements[0].position_m == pytest.approx(2.0)
    assert parameters.feed.wire_id == "element-2"
