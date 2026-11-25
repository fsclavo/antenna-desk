# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Stacked-Yagi dialog and embedded form behavior."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog, QLabel
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.polarization import Polarization
from antennadesk.domain.antennas.stacked_yagi import StackedYagiParameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.ui.dialogs.stacked_yagi_dialog import StackedYagiDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _parameters() -> StackedYagiParameters:
    return StackedYagiParameters(
        yagi=YagiParameters(
            frequency_hz=14_100_000.0,
            elements=(
                YagiElement(position_m=0.0, length_m=10.2, radius_m=0.001),
                YagiElement(position_m=2.1, length_m=9.8, radius_m=0.001),
            ),
            height_m=10.0,
        ),
        count=2,
        spacing_m=10.6,
        phase_step_deg=180.0,
    )


def _dialog(qtbot: QtBot, **kwargs: object) -> StackedYagiDialog:
    dialog = StackedYagiDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        **kwargs,  # type: ignore[arg-type]
    )
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_builds_a_two_level_stack_with_an_ideal_second_source(
    qtbot: QtBot,
) -> None:
    dialog = _dialog(qtbot)

    parameters = dialog.parameters()
    model = parameters.to_antenna()

    assert dialog.windowTitle() == "Stacked Yagi Generator"
    assert parameters.count == 2
    assert parameters.spacing_m > 0.0
    assert len(model.sources) == 1
    assert model.sources[0].wire_id.startswith("level-2-")
    assert parameters.yagi.mast_diameter_m == 0.0
    assert parameters.yagi.guy_count == 0
    assert parameters.yagi.driven_folded is False


def test_dialog_seeds_the_current_frequency_and_starting_spacing(
    qtbot: QtBot,
) -> None:
    dialog = _dialog(qtbot, frequency_hz=14_100_000.0)

    parameters = dialog.parameters()

    assert parameters.frequency_hz == pytest.approx(14_100_000.0)
    assert parameters.spacing_m == pytest.approx(
        299_792_458.0 / 14_100_000.0 / 2.0,
        abs=1e-3,
    )


def test_dialog_restores_existing_stack_parameters(qtbot: QtBot) -> None:
    parameters = _parameters()
    dialog = _dialog(qtbot, parameters=parameters)

    restored = dialog.parameters()

    assert restored == parameters
    assert restored.to_antenna() == parameters.to_antenna()


def test_vertical_polarization_shows_the_overlap_warning(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    form = dialog._form
    form._spacing_field.configure(1.0)
    index = form._yagi._polarization.findData(Polarization.VERTICAL.value)
    assert index >= 0
    form._yagi._polarization.setCurrentIndex(index)
    form._update_geometry()

    assert form._overlap_warning.isVisibleTo(form) or form._overlap_warning.text()
    with pytest.raises(ValueError, match="overlap"):
        form.parameters()


def test_dialog_retranslates_and_switches_units(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    dialog = StackedYagiDialog(translator, UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    parameters = dialog.parameters()

    translator.set_language(Language.SPANISH)
    dialog._form.retranslate()

    assert any(
        label.text() == "Niveles" for label in dialog._form.findChildren(QLabel) if label.text()
    )
    dialog._form.set_unit_system(UnitSystem.IMPERIAL)
    restored = dialog.parameters()
    assert restored.spacing_m == pytest.approx(parameters.spacing_m, abs=1e-3)
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_envelope_limits_the_stack_top_height(qtbot: QtBot) -> None:
    parameters = _parameters()
    dialog = _dialog(qtbot, parameters=parameters)
    form = dialog._form
    form._max_top_height_field.configure(21.0)

    restored = dialog.parameters()
    assert restored.max_top_height_m == pytest.approx(21.0, abs=1e-3)
    assert restored.maximum_spacing_m == pytest.approx(11.0, abs=1e-3)

    form._max_top_height_field.configure(15.0)
    form._update_geometry()
    assert form._envelope_warning.text()
    with pytest.raises(ValueError, match="max_top_height_m"):
        form.parameters()
