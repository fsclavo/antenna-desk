# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.ui.dialogs.fan_dipole_dialog import FanDipoleDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_fan_dipole_dialog_builds_parameters(qtbot: QtBot) -> None:
    dialog = FanDipoleDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert len(parameters.elements) == 2
    assert dialog._table.rowCount() == 2
    assert dialog._form._ground.currentText() == "Finite ground"


def test_fan_dipole_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    original = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(
            FanElement(length_m=20.0, included_angle_deg=120.0),
            FanElement(length_m=10.0, included_angle_deg=90.0),
        ),
        apex_height_m=12.0,
    )
    dialog = FanDipoleDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
