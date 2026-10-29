# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.load import SeriesLoad
from antennadesk.ui.dialogs.loads_dialog import LoadsDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_loads_dialog_adds_and_removes_series_loads(qtbot: QtBot) -> None:
    existing = SeriesLoad("load-1", "radiator", 5.0, resistance_ohm=10.0)
    dialog = LoadsDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        {"radiator": 20.0},
        (existing,),
    )
    qtbot.addWidget(dialog)

    dialog._resistance.setValue(50.0)
    dialog._inductance.setValue(12.0)
    dialog._add.click()

    assert len(dialog.loads()) == 2
    assert dialog.loads()[1].resistance_ohm == 50.0
    assert dialog.loads()[1].inductance_h == 12e-6

    dialog._kind.setCurrentIndex(1)
    dialog._capacitance.setValue(30.0)
    dialog._add.click()
    from antennadesk.domain.antennas.load import ParallelLoad

    assert isinstance(dialog.loads()[2], ParallelLoad)

    dialog._table.selectRow(0)
    dialog._remove.click()
    assert [load.id for load in dialog.loads()] == ["load-2", "load-3"]
