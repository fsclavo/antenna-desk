# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.zs6bkw import (
    ZS6BKW_DIPOLE_ID,
    ZS6BKW_VARIANTS,
)
from antennadesk.ui.dialogs.zs6bkw_dialog import ZS6BKWDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_zs6bkw_dialog_builds_the_reference_preset(qtbot: QtBot) -> None:
    dialog = ZS6BKWDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.generator_id == "zs6bkw"
    dipole = next(wire for wire in parameters.wires if wire.id == ZS6BKW_DIPOLE_ID)
    assert dipole.length_m == pytest.approx(28.4)
    line = parameters.transmission_lines[0]
    assert line.characteristic_impedance_ohm == pytest.approx(400.0)
    assert line.length_m == pytest.approx(13.6)
    assert dialog.windowTitle() == "ZS6BKW Generator"
    typed = dialog.typed_parameters()
    assert typed.preset.value == "zs6bkw"
    assert typed.dipole_total_length_m == pytest.approx(28.4)
    assert typed.line_impedance_ohm == pytest.approx(400.0)
    assert typed.line_length_m == pytest.approx(13.6)


def test_zs6bkw_dialog_can_select_the_commercial_variant(qtbot: QtBot) -> None:
    dialog = ZS6BKWDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    dialog._variant.setCurrentIndex(dialog._variant.findData(1))
    parameters = dialog.parameters()

    dipole = next(wire for wire in parameters.wires if wire.id == ZS6BKW_DIPOLE_ID)
    line = parameters.transmission_lines[0]
    assert dipole.length_m == pytest.approx(ZS6BKW_VARIANTS[1].dipole_total_length_m)
    assert line.characteristic_impedance_ohm == pytest.approx(
        ZS6BKW_VARIANTS[1].characteristic_impedance_ohm
    )
    assert line.length_m == pytest.approx(ZS6BKW_VARIANTS[1].line_length_m)
