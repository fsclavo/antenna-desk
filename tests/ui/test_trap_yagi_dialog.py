# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.trap_yagi_dialog import TrapYagiDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> TrapYagiDialog:
    return TrapYagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_trap_yagi_dialog_builds_the_default_traps(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Trapped Yagi Generator"
    assert parameters.element_count == 3
    assert len(parameters.to_antenna().wires) == 3
    assert len(parameters.to_antenna().loads) == 6
    assert "3 elements" in dialog._form._geometry.text()


def test_trap_yagi_dialog_updates_the_trap_position(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._element_count.setValue(2)
    dialog._form._trap_inset.setValue(3.0)
    dialog._form._trap_frequency.setValue(14.0)
    dialog._form._trap_inductance.setValue(6.0)

    parameters = dialog.parameters()

    assert parameters.element_count == 2
    assert parameters.trap_inset_m == pytest.approx(3.0, abs=1e-3)
    assert parameters.trap_frequency_hz == pytest.approx(14_000_000.0)
    assert parameters.trap_inductance_h == pytest.approx(6e-6)
    assert len(parameters.to_antenna().loads) == 4


def test_trap_yagi_dialog_sets_the_requested_frequency(qtbot: QtBot) -> None:
    dialog = TrapYagiDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=10_100_000.0,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    assert parameters.frequency_hz == pytest.approx(10_100_000.0)
    assert parameters.high_band_frequency_hz == pytest.approx(20_200_000.0)


def test_trap_yagi_form_preserves_lengths_when_switching_units(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._driven_length.setValue(20.0)
    dialog._form._trap_inset.setValue(3.0)

    dialog._form.set_unit_system(UnitSystem.IMPERIAL)

    parameters = dialog.parameters()
    assert parameters.driven_length_m == pytest.approx(20.0, rel=1e-3)
    assert parameters.trap_inset_m == pytest.approx(3.0, rel=1e-3)
    assert dialog._form._driven_length.suffix().strip() == "ft"
