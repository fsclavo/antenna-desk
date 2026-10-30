# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.ui.dialogs.j_pole_dialog import JPoleDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_j_pole_dialog_builds_parameters(qtbot: QtBot) -> None:
    dialog = JPoleDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.radiator_height_m > parameters.stub_length_m
    assert parameters.folded is False
    assert dialog._form._ground.currentText() == "Finite ground"


def test_j_pole_dialog_restores_slim_jim(qtbot: QtBot) -> None:
    original = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        folded=True,
    )
    dialog = JPoleDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
    assert dialog.parameters().template_name == "Slim Jim"
