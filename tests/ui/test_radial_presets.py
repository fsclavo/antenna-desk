# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem, length_to_m
from antennadesk.ui.widgets.radial_presets import (
    CUSTOM_RADIAL_KEY,
    RADIAL_PRESETS,
    matching_radial_key,
    radial_length_m,
)
from antennadesk.ui.widgets.vertical_form import VerticalForm


def _form(qtbot: QtBot, translator: Translator | None = None) -> VerticalForm:
    form = VerticalForm(translator or Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    return form


def test_default_radial_fields_are_custom(qtbot: QtBot) -> None:
    form = _form(qtbot)

    assert form._radial_preset.currentData() == CUSTOM_RADIAL_KEY


def test_ground_radials_preset_updates_the_numeric_fields(qtbot: QtBot) -> None:
    form = _form(qtbot)
    form._radial_preset.setCurrentIndex(form._radial_preset.findData("ground"))

    parameters = form.parameters()
    frequency_hz = parameters.frequency_hz
    expected_length = radial_length_m(
        next(preset for preset in RADIAL_PRESETS if preset.key == "ground"),
        frequency_hz,
    )

    assert parameters.radial_count == 16
    assert parameters.base_height_m == pytest.approx(0.25)
    assert parameters.radial_length_m == pytest.approx(expected_length, abs=1e-3)
    assert form._radial_preset.currentData() == "ground"


def test_elevated_radials_preset_raises_the_radial_plane(qtbot: QtBot) -> None:
    form = _form(qtbot)
    form._radial_preset.setCurrentIndex(form._radial_preset.findData("elevated"))

    parameters = form.parameters()

    assert parameters.radial_count == 4
    assert parameters.base_height_m == pytest.approx(2.0)
    assert parameters.radial_length_m == pytest.approx(10.56, abs=0.02)


def test_ground_screen_preset_uses_a_dense_short_radial_field(qtbot: QtBot) -> None:
    form = _form(qtbot)
    form._radial_preset.setCurrentIndex(form._radial_preset.findData("screen"))

    parameters = form.parameters()

    assert parameters.radial_count == 32
    assert parameters.base_height_m == pytest.approx(0.25)
    assert parameters.radial_length_m == pytest.approx(4.22, abs=0.02)


def test_no_radials_preset_clears_the_radial_field(qtbot: QtBot) -> None:
    form = _form(qtbot)
    form._radial_preset.setCurrentIndex(form._radial_preset.findData("none"))

    parameters = form.parameters()

    assert parameters.radial_count == 0
    assert parameters.radial_length_m == 0.0


def test_frequency_change_recomputes_the_selected_preset_length(qtbot: QtBot) -> None:
    form = _form(qtbot)
    form._radial_preset.setCurrentIndex(form._radial_preset.findData("ground"))
    form._frequency.setValue(14.1)

    parameters = form.parameters()

    assert form._radial_preset.currentData() == "ground"
    assert parameters.radial_length_m == pytest.approx(5.32, abs=0.02)


def test_editing_a_radial_field_switches_to_custom(qtbot: QtBot) -> None:
    form = _form(qtbot)
    form._radial_preset.setCurrentIndex(form._radial_preset.findData("ground"))

    form._radial_length.setValue(3.0)

    assert form._radial_preset.currentData() == CUSTOM_RADIAL_KEY
    assert form.parameters().radial_length_m == pytest.approx(3.0)


def test_preset_labels_are_translated(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    form = _form(qtbot, translator)
    index = form._radial_preset.findData("elevated")
    assert form._radial_preset.itemText(index) == "Elevated radials (4 x 0.25λ)"

    translator.set_language(Language.SPANISH)
    form.retranslate()

    assert form._radial_preset.itemText(index) == "Radiales elevados (4 x 0,25λ)"


def test_matching_radial_key_uses_physical_values() -> None:
    frequency_hz = 7_100_000.0
    preset = next(item for item in RADIAL_PRESETS if item.key == "ground")
    expected_length = radial_length_m(preset, frequency_hz)

    assert matching_radial_key(frequency_hz, 0.25, 16, expected_length) == "ground"
    assert matching_radial_key(frequency_hz, 0.25, 16, expected_length + 0.1) == CUSTOM_RADIAL_KEY


def test_preset_controller_uses_the_active_unit_system(qtbot: QtBot) -> None:
    form = _form(qtbot)
    form.set_unit_system(UnitSystem.IMPERIAL)
    form._radial_preset.setCurrentIndex(form._radial_preset.findData("ground"))

    length_m = length_to_m(form._radial_length.value(), UnitSystem.IMPERIAL)

    assert length_m == pytest.approx(10.56, abs=0.02)
    assert form._radial_length.suffix().strip() == "ft"
