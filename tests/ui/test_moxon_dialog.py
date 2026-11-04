# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.ui.dialogs.moxon_dialog import MoxonDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_moxon_dialog_builds_parameters(qtbot: QtBot) -> None:
    dialog = MoxonDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.width_m > 0.0
    assert parameters.gap_m > 0.0
    assert dialog._form._ground.currentText() == "Finite ground"
    assert dialog._form._polarization.currentText() == "Horizontal"
    assert dialog._form._polarization.itemText(1) == "Vertical"


def test_moxon_dialog_loads_the_reference_preset(qtbot: QtBot) -> None:
    dialog = MoxonDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    dialog._form._reference.click()

    parameters = dialog.parameters()
    assert parameters.frequency_hz == 14_170_000.0
    assert parameters.width_m == pytest.approx(25.00 * 0.3048)
    assert parameters.gap_m == pytest.approx(0.72 * 0.3048, abs=0.001)
    assert dialog._form._ground.currentText() == "Free space"


def test_moxon_dialog_restores_vertical_polarization(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.polarization import Polarization

    original = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.6,
        depth_m=2.5,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
        polarization=Polarization.VERTICAL,
    )
    dialog = MoxonDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
    assert dialog._form._polarization.currentData() == "vertical"


def test_moxon_dialog_warns_when_the_rectangle_reaches_the_ground(qtbot: QtBot) -> None:
    dialog = MoxonDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog.show()
    dialog._form._height.setValue(1.0)
    index = dialog._form._polarization.findData("vertical")
    dialog._form._polarization.setCurrentIndex(index)

    assert dialog._form._clearance_warning.isHidden() is False
    assert "greater than" in dialog._form._clearance_warning.text()
    with pytest.raises(ValueError, match="below ground"):
        dialog.parameters()


def test_moxon_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    original = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.6,
        depth_m=2.5,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
    )
    dialog = MoxonDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
