# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.yagi import YagiParameters
from antennadesk.domain.design import VerticalForm
from antennadesk.ui.dialogs.design_from_frequency_dialog import (
    DesignFromFrequencyDialog,
)
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog(qtbot: QtBot) -> DesignFromFrequencyDialog:
    dialog = DesignFromFrequencyDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        initial_frequency_hz=146_000_000.0,
    )
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_estimates_a_dipole(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._run_estimate()

    assert dialog._results.rowCount() >= 2
    assert dialog._apply.isEnabled()
    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, DipoleParameters)
    assert parameters.total_length_m > 0.0


def test_dialog_estimates_a_vertical_with_subtype(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._family.setCurrentIndex(dialog._family.findData("vertical"))
    dialog._vertical_form.setCurrentIndex(
        dialog._vertical_form.findData(VerticalForm.FIVE_EIGHTH_WAVE.value)
    )
    dialog._radial_count.setValue(8)
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, VerticalParameters)
    assert parameters.radial_count == 8
    assert parameters.height_m > 0.5


def test_dialog_estimates_a_delta_loop(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._family.setCurrentIndex(dialog._family.findData("loop"))
    dialog._loop_shape.setCurrentIndex(dialog._loop_shape.findData("delta"))
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, LoopParameters)
    assert parameters.sides == 3


def test_dialog_estimates_the_nbs_yagi(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._family.setCurrentIndex(dialog._family.findData("yagi"))
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, YagiParameters)
    assert len(parameters.elements) == 5


def test_dialog_shows_estimator_sources(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._family.setCurrentIndex(dialog._family.findData("moxon"))
    dialog._run_estimate()

    assert "Cebik" in dialog._sources.text()
    assert "Table 1" in dialog._sources.text()


def test_changing_an_input_invalidates_the_estimate(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._run_estimate()
    assert dialog._apply.isEnabled()

    dialog._frequency.setValue(dialog._frequency.value() * 1.01)

    assert dialog._apply.isEnabled() is False
    assert dialog._results.rowCount() == 0
