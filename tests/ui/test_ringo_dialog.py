# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.ui.dialogs.ringo_dialog import RingoDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_ringo_dialog_builds_parameters(qtbot: QtBot) -> None:
    dialog = RingoDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.radiator_height_m > 0.0
    assert parameters.ring_diameter_m > 0.0
    assert dialog._form._ground.currentText() == "Finite ground"


def test_ringo_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    original = RingoParameters(
        frequency_hz=50_100_000.0,
        radiator_height_m=3.0,
        ring_diameter_m=0.33,
        ring_height_m=0.1,
        ring_sides=8,
    )
    dialog = RingoDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
