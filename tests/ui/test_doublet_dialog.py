# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleOrientation, DipoleParameters
from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.design.formulas import half_wave_length_m
from antennadesk.ui.dialogs.doublet_dialog import DoubletDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_doublet_dialog_builds_starting_dimensions_and_line(qtbot: QtBot) -> None:
    dialog = DoubletDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    line = dialog.feed_line()

    assert parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert parameters.total_length_m == pytest.approx(half_wave_length_m(7_100_000.0), abs=0.001)
    assert parameters.orientation is DipoleOrientation.HORIZONTAL
    assert line.characteristic_impedance_ohm == pytest.approx(450.0)
    assert line.length_m == pytest.approx(10.0)
    assert line.velocity_factor == pytest.approx(0.9)
    assert line.matched_loss_db_per_100m == pytest.approx(0.2)
    assert "450.0" in dialog._geometry.text()


def test_doublet_dialog_restores_parameters_and_line(qtbot: QtBot) -> None:
    parameters = DipoleParameters(
        frequency_hz=14_100_000.0,
        total_length_m=30.0,
        height_m=12.0,
        orientation=DipoleOrientation.VERTICAL,
    )
    line = FeedLine(
        characteristic_impedance_ohm=300.0,
        length_m=20.0,
        velocity_factor=0.85,
        matched_loss_db_per_100m=0.5,
    )
    dialog = DoubletDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=parameters,
        feed_line=line,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == parameters
    assert dialog.feed_line() == line
    assert dialog._azimuth.isEnabled() is False
