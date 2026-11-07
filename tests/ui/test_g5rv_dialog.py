# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.g5rv import G5RV_DIPOLE_TOTAL_LENGTH_M
from antennadesk.ui.dialogs.g5rv_dialog import G5RVDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_g5rv_dialog_builds_the_default_450_ohm_preset(qtbot: QtBot) -> None:
    dialog = G5RVDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "G5RV Generator"
    assert parameters.generator_id == "g5rv"
    assert parameters.wires[1].length_m == pytest.approx(G5RV_DIPOLE_TOTAL_LENGTH_M)
    line = parameters.transmission_lines[0]
    assert line.characteristic_impedance_ohm == pytest.approx(450.0)
    assert line.length_m == pytest.approx(10.36)
    assert line.velocity_factor == pytest.approx(1.0)
    assert "450" in dialog._geometry.text()
    typed = dialog.typed_parameters()
    assert typed.preset.value == "g5rv"
    assert typed.dipole_total_length_m == pytest.approx(G5RV_DIPOLE_TOTAL_LENGTH_M)
    assert typed.line_impedance_ohm == pytest.approx(450.0)
    assert typed.line_length_m == pytest.approx(10.36)


def test_g5rv_dialog_can_select_the_300_ohm_line(qtbot: QtBot) -> None:
    dialog = G5RVDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._line_option.setCurrentIndex(0)
    dialog._velocity.setValue(0.9)

    line = dialog.parameters().transmission_lines[0]

    assert line.characteristic_impedance_ohm == pytest.approx(300.0)
    assert line.length_m == pytest.approx(8.84)
    assert line.velocity_factor == pytest.approx(0.9)
