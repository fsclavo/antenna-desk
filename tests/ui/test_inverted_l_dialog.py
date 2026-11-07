# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.ui.dialogs.inverted_l_dialog import InvertedLDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_inverted_l_dialog_builds_parameters(qtbot: QtBot) -> None:
    dialog = InvertedLDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    assert parameters.vertical_height_m > 0.0
    assert parameters.horizontal_length_m > 0.0
    assert dialog._ground.currentText() == "Finite ground"
    assert dialog._form._soil.currentData() == "average"


def test_inverted_l_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    original = InvertedLParameters(
        frequency_hz=7_100_000.0,
        vertical_height_m=10.0,
        horizontal_length_m=20.0,
        base_height_m=1.0,
        azimuth_deg=35.0,
    )
    dialog = InvertedLDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
    assert "30.000" in dialog._geometry.text()
