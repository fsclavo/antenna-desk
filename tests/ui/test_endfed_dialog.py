# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.endfed import EndFedParameters, EndFedPreset
from antennadesk.domain.design.formulas import half_wave_length_m
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
    assert dialog._form._counterpoise_enabled.isChecked() is False
    assert dialog._form._counterpoise_length.isEnabled() is False
    assert dialog._form._counterpoise_height.isEnabled() is False
    assert "counterpoise none" in dialog._form._geometry.text()

    dialog._form._counterpoise_enabled.setChecked(True)
    assert dialog._form._counterpoise_length.isEnabled() is True
    assert dialog._form._counterpoise_height.isEnabled() is True
    assert dialog._form._counterpoise_length.value() > 0.0
    dialog._form._counterpoise_length.setValue(2.0)
    assert "counterpoise 2.00 m" in dialog._form._geometry.text()
    assert dialog.parameters().counterpoise_length_m == 2.0

    dialog._form._counterpoise_enabled.setChecked(False)
    assert dialog.parameters().counterpoise_length_m == 0.0
    assert dialog._form._ground.currentText() == "Finite ground"


def test_endfed_dialog_defaults_to_harmonic_analysis_bands(qtbot: QtBot) -> None:
    dialog = EndFedDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    plan = dialog._default_band_plan()

    assert [selection.band.name for selection in plan.selections] == [
        "40m",
        "20m",
        "10m",
    ]


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


def test_sloper_preset_uses_a_half_wave_sloping_wire(qtbot: QtBot) -> None:
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preset=EndFedPreset.SLOPER,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Sloper Generator"
    assert parameters.preset is EndFedPreset.SLOPER
    assert parameters.length_m == pytest.approx(half_wave_length_m(7_100_000.0), abs=0.001)
    assert parameters.feed_height_m == pytest.approx(10.0)
    assert parameters.end_height_m < parameters.feed_height_m
    assert parameters.transformer_ratio == pytest.approx(49.0)
    assert parameters.counterpoise_length_m > 0.0
    assert dialog._form._preset_label.text() == "Sloper"


def test_random_wire_preset_uses_a_9_to_1_transformer(qtbot: QtBot) -> None:
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preset=EndFedPreset.RANDOM_WIRE,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Random Wire Generator"
    assert parameters.preset is EndFedPreset.RANDOM_WIRE
    assert parameters.length_m == pytest.approx(17.0)
    assert parameters.transformer_ratio == pytest.approx(9.0)
    assert parameters.counterpoise_length_m > 0.0
    assert dialog._form._preset_label.text() == "Random wire"


def test_sloper_preset_tracks_the_selected_frequency(qtbot: QtBot) -> None:
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preset=EndFedPreset.SLOPER,
    )
    qtbot.addWidget(dialog)

    dialog._form.set_frequency_hz(28_500_000.0)
    parameters = dialog.parameters()

    assert parameters.preset is EndFedPreset.SLOPER
    assert parameters.frequency_hz == pytest.approx(28_500_000.0)
    assert parameters.length_m == pytest.approx(half_wave_length_m(28_500_000.0), abs=0.001)
    assert parameters.end_height_m < parameters.feed_height_m
