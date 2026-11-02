# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.ui.dialogs.endfed_dialog import EndFedDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_endfed_dialog_builds_parameters(qtbot: QtBot) -> None:
    dialog = EndFedDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.length_m > 0.0
    assert parameters.feed_height_m == 10.0
    assert parameters.transformer_ratio == 49.0
    assert parameters.counterpoise_length_m == 0.0
    assert dialog._form._counterpoise_height.isEnabled() is False
    assert "counterpoise none" in dialog._form._geometry.text()
    dialog._form._counterpoise_length.setValue(2.0)
    assert dialog._form._counterpoise_height.isEnabled() is True
    assert "counterpoise 2.00 m" in dialog._form._geometry.text()
    assert dialog._form._ground.currentText() == "Finite ground"


def test_endfed_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    original = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=5.0,
        azimuth_deg=30.0,
        transformer_ratio=49.0,
        counterpoise_length_m=2.5,
        counterpoise_height_m=0.2,
        counterpoise_azimuth_deg=210.0,
    )
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
