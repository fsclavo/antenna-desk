# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from main_window_support import FakeSolver
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
    assert parameters.feed_section_length_m == pytest.approx(0.5)
    assert parameters.installation_return_length_m == pytest.approx(0.1)
    assert parameters.installation_return_active is True
    assert dialog._form._counterpoise_enabled.isChecked() is False
    assert dialog._form._counterpoise_length.isEnabled() is False
    assert dialog._form._counterpoise_height.isEnabled() is False
    assert dialog._form._installation_return.isEnabled() is True
    assert "counterpoise none" in dialog._form._geometry.text()
    assert "feed section" in dialog._form._geometry.text()
    assert "installation return" in dialog._form._geometry.text()
    assert dialog._form._model_warning.text() == ""

    dialog._form._counterpoise_enabled.setChecked(True)
    assert dialog._form._counterpoise_length.isEnabled() is True
    assert dialog._form._counterpoise_height.isEnabled() is True
    assert dialog._form._installation_return.isEnabled() is False
    assert dialog._form._counterpoise_length.value() > 0.0
    dialog._form._counterpoise_length.setValue(2.0)
    assert "counterpoise 2.00 m" in dialog._form._geometry.text()
    assert dialog.parameters().counterpoise_length_m == 2.0

    dialog._form._counterpoise_enabled.setChecked(False)
    assert dialog.parameters().counterpoise_length_m == 0.0
    assert dialog._form._ground.currentText() == "Finite ground"


def test_endfed_dialog_checks_segment_convergence(qtbot: QtBot) -> None:
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        solver=FakeSolver(),
    )
    qtbot.addWidget(dialog)

    assert dialog._check_button.isEnabled() is True
    dialog._check_button.click()

    assert "Converged" in dialog._check_result.text()


def test_endfed_dialog_shortened_convergence_reports_the_matching_limitation(
    qtbot: QtBot,
) -> None:
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preset=EndFedPreset.SHORTENED_80_10,
        solver=FakeSolver(),
    )
    qtbot.addWidget(dialog)

    dialog._check_button.click()

    assert "matching capacitor" in dialog._check_result.text()


def test_endfed_dialog_warns_about_a_legacy_feed_model(qtbot: QtBot) -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=10.0,
        transformer_ratio=49.0,
    )
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=parameters,
    )
    qtbot.addWidget(dialog)

    assert dialog._form._model_warning.text()
    assert "No fixed feed section" in dialog._form._model_warning.text()
    assert "No counterpoise or installation return" in dialog._form._model_warning.text()


def test_endfed_dialog_loads_efhw_band_presets(qtbot: QtBot) -> None:
    dialog = EndFedDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    button = dialog._form._efhw_buttons["40m"]
    button.click()
    parameters = dialog.parameters()

    assert parameters.length_m == pytest.approx(66.0 * 0.3048, abs=1e-3)
    assert parameters.transformer_ratio == pytest.approx(49.0)
    assert parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert parameters.counterpoise_length_m > 0.0

    dialog._form._efhw_buttons["10m"].click()
    parameters = dialog.parameters()
    assert parameters.length_m == pytest.approx(16.0 * 0.3048, abs=1e-3)
    assert parameters.frequency_hz == pytest.approx(28_400_000.0)


def test_endfed_dialog_defaults_to_harmonic_analysis_bands(qtbot: QtBot) -> None:
    dialog = EndFedDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    plan = dialog._default_band_plan()

    assert [selection.band.name for selection in plan.selections] == [
        "40m",
        "20m",
        "10m",
    ]


def test_shortened_efhw_80_10_preset_loads_the_coil(qtbot: QtBot) -> None:
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preset=EndFedPreset.SHORTENED_80_10,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Shortened EFHW 80-10 m"
    assert parameters.preset is EndFedPreset.SHORTENED_80_10
    assert parameters.length_m == pytest.approx(22.74, abs=1e-3)
    assert parameters.loading_coil_enabled is True
    assert parameters.loading_coil_offset_m == pytest.approx(20.35, abs=1e-3)
    assert parameters.loading_coil_inductance_h == pytest.approx(110e-6)
    assert parameters.transformer_ratio == pytest.approx(49.0)
    assert dialog._form._loading_coil_group.isChecked() is True
    assert dialog._form._loading_coil_offset.isEnabled() is True
    assert "110.0 µH" in dialog._form._geometry.text()
    assert [selection.band.name for selection in dialog._default_band_plan().selections] == [
        "80m",
        "40m",
        "20m",
        "15m",
        "10m",
    ]


def test_shortened_efhw_40_10_preset_loads_the_coil(qtbot: QtBot) -> None:
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preset=EndFedPreset.SHORTENED_40_10,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Shortened EFHW 40-20-10 m"
    assert parameters.preset is EndFedPreset.SHORTENED_40_10
    assert parameters.length_m == pytest.approx(11.86, abs=1e-3)
    assert parameters.loading_coil_offset_m == pytest.approx(10.01, abs=1e-3)
    assert parameters.loading_coil_inductance_h == pytest.approx(23e-6)
    assert dialog._form._loading_coil_group.isChecked() is True
    assert [selection.band.name for selection in dialog._default_band_plan().selections] == [
        "40m",
        "20m",
        "10m",
    ]


def test_shortened_efhw_reference_buttons_switch_geometry(qtbot: QtBot) -> None:
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preset=EndFedPreset.SHORTENED_80_10,
    )
    qtbot.addWidget(dialog)

    dialog._form._shortened_buttons[EndFedPreset.SHORTENED_40_10].click()
    parameters = dialog.parameters()

    assert parameters.preset is EndFedPreset.SHORTENED_40_10
    assert parameters.length_m == pytest.approx(11.86, abs=1e-3)
    assert parameters.loading_coil_offset_m == pytest.approx(10.01, abs=1e-3)


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
