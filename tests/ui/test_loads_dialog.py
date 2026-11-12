# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QMessageBox
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


def test_loads_dialog_calculator_applies_a_trap_result(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from PySide6.QtWidgets import QDialog

    from antennadesk.domain.antennas.load import LoadKind
    from antennadesk.ui.dialogs import loads_dialog as loads_dialog_module
    from antennadesk.ui.dialogs.component_calculator_dialog import (
        CalculatorKind,
        CalculatorResult,
    )

    class FakeCalculator:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def calculator_result(self) -> CalculatorResult:
            return CalculatorResult(
                CalculatorKind.TRAP,
                inductance_h=5e-6,
                capacitance_f=100e-12,
                frequency_hz=7_100_000.0,
            )

    monkeypatch.setattr(loads_dialog_module, "ComponentCalculatorDialog", FakeCalculator)
    dialog = LoadsDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        {"radiator": 20.0},
        (),
    )
    qtbot.addWidget(dialog)

    dialog._calculator.click()

    assert dialog._kind.currentData() == LoadKind.PARALLEL.value
    assert dialog._inductance.value() == pytest.approx(5.0)
    assert dialog._capacitance.value() == pytest.approx(100.0)
    assert dialog._trap_frequency.value() == pytest.approx(7.1)


def test_loads_dialog_adds_a_parallel_trap(qtbot: QtBot) -> None:
    import math

    from antennadesk.domain.antennas.load import ParallelLoad

    dialog = LoadsDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        {"radiator": 20.0},
        (),
    )
    qtbot.addWidget(dialog)
    dialog._inductance.setValue(10.0)
    dialog._trap_frequency.setValue(14.1)

    dialog._add_trap.click()

    load = dialog.loads()[0]
    assert isinstance(load, ParallelLoad)
    expected_c = 1.0 / ((2.0 * math.pi * 14_100_000.0) ** 2 * 10e-6)
    assert load.capacitance_f == pytest.approx(expected_c)


def test_loads_dialog_protects_template_managed_loads(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    load = SeriesLoad("loading-coil", "radiator", 1.0, inductance_h=12e-6)
    dialog = LoadsDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        {"radiator": 2.0},
        (load,),
        protected_load_ids=frozenset({"loading-coil"}),
    )
    qtbot.addWidget(dialog)
    messages: list[str] = []
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args, **kwargs: messages.append(str(args[-1])) or QMessageBox.StandardButton.Ok,
    )

    dialog._table.selectRow(0)
    dialog._remove.click()

    assert dialog.loads() == (load,)
    assert messages
