# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.ui.dialogs.magnetic_loop_dialog import MagneticLoopDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_magnetic_loop_dialog_builds_parameters(qtbot: QtBot) -> None:
    dialog = MagneticLoopDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.diameter_m > 0.0
    assert parameters.tuning_capacitance_f > 0.0
    assert dialog._ground.currentText() == "Finite ground"
    assert "pF" in dialog._geometry.text()


def test_magnetic_loop_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    original = MagneticLoopParameters(
        frequency_hz=7_100_000.0,
        diameter_m=1.2,
        tuning_capacitance_f=180e-12,
        height_m=1.5,
        sides=24,
        gap_length_m=0.04,
        capacitor_esr_ohm=0.2,
        azimuth_deg=35.0,
        wire_radius_m=0.006,
    )
    dialog = MagneticLoopDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
    assert dialog._sides.value() == 24
    assert dialog._capacitance.value() == 180.0
