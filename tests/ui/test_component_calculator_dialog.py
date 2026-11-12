# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Component calculator dialog behavior."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QTextBrowser
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.component_calculator_dialog import (
    CalculatorKind,
    CalculatorSeed,
    ComponentCalculatorDialog,
)
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog(qtbot: QtBot, *, language: Language = Language.ENGLISH):
    dialog = ComponentCalculatorDialog(Translator(language), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    return dialog


def test_coil_calculates_inductance_and_turns(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._coil_turns.setValue(10.0)
    dialog._coil_diameter.setValue(50.0)
    dialog._coil_length.setValue(50.0)

    dialog._coil_l_button.click()

    assert "µH" in dialog._coil_result.text()
    assert dialog._use_button.isEnabled()
    assert dialog.calculator_result() is not None
    assert dialog.calculator_result().kind is CalculatorKind.COIL

    dialog._coil_turns_button.click()

    assert dialog._coil_turns.value() == pytest.approx(10.0, rel=0.01)


def test_trap_solves_c_l_and_frequency(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._trap_frequency.setValue(14.1)
    dialog._trap_inductance.setValue(10.0)
    dialog._trap_solve_c.click()
    capacitance = dialog._trap_capacitance.value()
    assert capacitance > 0.0
    assert dialog.calculator_result().kind is CalculatorKind.TRAP

    dialog._trap_capacitance.setValue(100.0)
    dialog._trap_solve_l.click()
    assert dialog._trap_inductance.value() > 0.0

    dialog._trap_inductance.setValue(10.0)
    dialog._trap_capacitance.setValue(100.0)
    dialog._trap_solve_f.click()
    assert dialog._trap_frequency.value() == pytest.approx(5.033, abs=1e-3)
    assert "5.032921" in dialog._trap_result.text()
    assert "XL" in dialog._trap_result.text()


def test_balun_and_conductor_calculators(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._balun_turns.setValue(4.0)
    dialog._balun_turns_button.click()
    assert dialog._balun_impedance.value() == pytest.approx(16.0)

    dialog._balun_impedance.setValue(49.0)
    dialog._balun_impedance_button.click()
    assert dialog._balun_turns.value() == pytest.approx(7.0)

    dialog._conductor_button.click()
    assert "Ω/m" in dialog._conductor_result.text()


def test_choke_tab_contains_reference_notes(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    choke = dialog._tabs.widget(4)
    text = choke.findChild(QTextBrowser)

    assert dialog._tabs.tabText(4) == "Common-mode choke"
    assert text is not None
    assert "Zcm" in text.toPlainText()


def test_seed_prefills_trap_values(qtbot: QtBot) -> None:
    dialog = ComponentCalculatorDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        seed=CalculatorSeed(
            tab="trap",
            inductance_h=10e-6,
            capacitance_f=100e-12,
            frequency_hz=14_100_000.0,
        ),
    )
    qtbot.addWidget(dialog)

    assert dialog._tabs.currentIndex() == 1
    assert dialog._trap_frequency.value() == pytest.approx(14.1)
    assert dialog._trap_inductance.value() == pytest.approx(10.0)
    assert dialog._trap_capacitance.value() == pytest.approx(100.0)


def test_dialog_retranslates(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot, language=Language.SPANISH)

    assert dialog.windowTitle() == "Calculadoras de componentes"
    assert dialog._tabs.tabText(0) == "Bobina"
    assert dialog._use_button.text() == "Usar resultado"
