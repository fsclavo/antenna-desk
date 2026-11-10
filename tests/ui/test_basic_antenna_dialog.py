# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from antennadesk.domain.antennas.folded_dipole import (
    ANTENNA_TYPE_FOLDED_DIPOLE,
    FoldedDipoleParameters,
)
from antennadesk.domain.antennas.loop import (
    ANTENNA_TYPE_LOOP,
    LoopOrientation,
    LoopParameters,
)
from antennadesk.domain.design.formulas import half_wave_length_m
from antennadesk.ui.dialogs.basic_antenna_dialog import BasicAntennaDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_wire_dipole_dialog_opens_the_full_editor(qtbot: QtBot) -> None:
    dialog = BasicAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        antenna_type=ANTENNA_TYPE_WIRE_DIPOLE,
        frequency_hz=14_100_000.0,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Wire dipole"
    assert isinstance(parameters, DipoleParameters)
    assert parameters.frequency_hz == pytest.approx(14_100_000.0)
    assert parameters.total_length_m == pytest.approx(
        half_wave_length_m(14_100_000.0),
        abs=0.001,
    )
    assert parameters.height_m == pytest.approx(8.0)
    assert parameters.ground.kind.value == "finite"
    assert dialog._form._change_template.isHidden()


def test_folded_dipole_dialog_opens_the_full_editor(qtbot: QtBot) -> None:
    dialog = BasicAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        antenna_type=ANTENNA_TYPE_FOLDED_DIPOLE,
        frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(dialog)
    dialog.show()

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Folded dipole"
    assert isinstance(parameters, FoldedDipoleParameters)
    assert parameters.total_length_m > 19.0
    assert parameters.spacing_m > 0.0
    assert dialog._form._change_template.isHidden()


def test_loop_dialog_keeps_the_delta_and_quad_side_counts(qtbot: QtBot) -> None:
    for sides, title in ((3, "Delta loop"), (4, "Quad loop"), (16, "Loop")):
        dialog = BasicAntennaDialog(
            Translator(Language.ENGLISH),
            UnitSystem.METRIC,
            antenna_type=ANTENNA_TYPE_LOOP,
            frequency_hz=7_100_000.0,
            initial_sides=sides,
        )
        qtbot.addWidget(dialog)

        parameters = dialog.parameters()

        assert dialog.windowTitle() == title
        assert isinstance(parameters, LoopParameters)
        assert parameters.sides == sides
        assert parameters.orientation is LoopOrientation.VERTICAL


def test_dialog_restores_existing_parameters(qtbot: QtBot) -> None:
    source = LoopParameters(
        frequency_hz=10_100_000.0,
        circumference_m=31.0,
        height_m=4.0,
        sides=8,
        orientation=LoopOrientation.HORIZONTAL,
    )
    dialog = BasicAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        antenna_type=ANTENNA_TYPE_LOOP,
        parameters=source,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert isinstance(parameters, LoopParameters)
    assert parameters.frequency_hz == pytest.approx(source.frequency_hz)
    assert parameters.circumference_m == pytest.approx(source.circumference_m)
    assert parameters.sides == source.sides
    assert parameters.orientation is source.orientation


def test_dialog_follows_the_ui_language(qtbot: QtBot) -> None:
    dialog = BasicAntennaDialog(
        Translator(Language.SPANISH),
        UnitSystem.METRIC,
        antenna_type=ANTENNA_TYPE_WIRE_DIPOLE,
    )
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Dipolo de hilo"
    assert dialog._hint.text() == ("Hilo recto con alimentación central, horizontal o vertical.")


def test_result_parameters_requires_acceptance(qtbot: QtBot) -> None:
    dialog = BasicAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        antenna_type=ANTENNA_TYPE_WIRE_DIPOLE,
    )
    qtbot.addWidget(dialog)

    with pytest.raises(ValueError):
        dialog.result_parameters()
