# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.transmission_line import TransmissionLine
from antennadesk.domain.antennas.wire import Wire
from antennadesk.ui.dialogs.transmission_lines_dialog import TransmissionLinesDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _wires() -> dict[str, Wire]:
    return {
        "left": Wire(
            "left",
            Point3D(-10.0, 0.0, 8.0),
            Point3D(0.0, 0.0, 8.0),
            0.001,
            COPPER,
        ),
        "right": Wire(
            "right",
            Point3D(0.0, 0.0, 8.0),
            Point3D(10.0, 0.0, 8.0),
            0.001,
            COPPER,
        ),
    }


def test_transmission_lines_dialog_adds_and_removes_lines(qtbot: QtBot) -> None:
    dialog = TransmissionLinesDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        _wires(),
        (),
    )
    qtbot.addWidget(dialog)

    dialog._start_wire.setCurrentIndex(dialog._start_wire.findData("left"))
    dialog._end_wire.setCurrentIndex(dialog._end_wire.findData("right"))
    dialog._start_offset.setValue(10.0)
    dialog._end_offset.setValue(0.0)
    dialog._z0.setValue(300.0)
    dialog._length.setValue(10.0)
    dialog._velocity.setValue(0.9)
    dialog._add.click()

    lines = dialog.transmission_lines()
    assert len(lines) == 1
    assert lines[0].start_wire_id == "left"
    assert lines[0].end_wire_id == "right"
    assert lines[0].characteristic_impedance_ohm == pytest.approx(300.0)
    assert lines[0].length_m == pytest.approx(10.0)
    assert lines[0].velocity_factor == pytest.approx(0.9)

    dialog._table.selectRow(0)
    dialog._remove.click()
    assert dialog.transmission_lines() == ()


def test_transmission_lines_dialog_uses_straight_line_distance(qtbot: QtBot) -> None:
    dialog = TransmissionLinesDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        _wires(),
        (),
    )
    qtbot.addWidget(dialog)

    dialog._start_wire.setCurrentIndex(dialog._start_wire.findData("left"))
    dialog._end_wire.setCurrentIndex(dialog._end_wire.findData("right"))
    dialog._start_offset.setValue(0.0)
    dialog._end_offset.setValue(0.0)
    dialog._use_distance.click()

    assert dialog._length.value() == pytest.approx(10.0, abs=0.001)


def test_transmission_lines_dialog_restores_existing_lines(qtbot: QtBot) -> None:
    line = TransmissionLine(
        id="line-1",
        start_wire_id="left",
        start_offset_m=10.0,
        end_wire_id="right",
        end_offset_m=0.0,
        characteristic_impedance_ohm=450.0,
        length_m=12.0,
        velocity_factor=0.85,
    )
    dialog = TransmissionLinesDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        _wires(),
        (line,),
    )
    qtbot.addWidget(dialog)

    assert dialog.transmission_lines() == (line,)
    assert dialog._table.rowCount() == 1
