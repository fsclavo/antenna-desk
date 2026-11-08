# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.beverage_dialog import BeverageDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> BeverageDialog:
    return BeverageDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_beverage_dialog_builds_a_terminated_receiving_wire(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Beverage Generator"
    assert parameters.termination_enabled is True
    assert parameters.termination_resistance_ohm == pytest.approx(500.0)
    assert len(parameters.to_antenna().wires) == 2
    assert len(parameters.to_antenna().loads) == 1
    assert "termination" in dialog._form._geometry.text()


def test_beverage_dialog_can_disable_the_termination(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._termination_enabled.setChecked(False)

    parameters = dialog.parameters()

    assert parameters.termination_enabled is False
    assert len(parameters.to_antenna().wires) == 1
    assert parameters.to_antenna().loads == ()
    assert "off" in dialog._form._geometry.text()


def test_beverage_dialog_loads_the_one_wavelength_starting_length(
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.design.formulas import wavelength_m

    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form._length.setValue(10.0)

    form.load_starting_dimensions()

    assert form.parameters().length_m == pytest.approx(
        wavelength_m(form.parameters().frequency_hz),
        abs=1e-3,
    )


def test_beverage_dialog_scales_to_the_requested_frequency(qtbot: QtBot) -> None:
    from antennadesk.domain.design.formulas import wavelength_m

    dialog = BeverageDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=3_500_000.0,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.frequency_hz == pytest.approx(3_500_000.0)
    assert parameters.length_m == pytest.approx(
        wavelength_m(3_500_000.0),
        abs=1e-3,
    )
