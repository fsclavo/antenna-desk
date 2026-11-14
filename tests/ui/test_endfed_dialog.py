# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from main_window_support import FakeSolver
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.endfed import EndFedParameters, EndFedPreset
from antennadesk.domain.antennas.matching_network import LNetwork
from antennadesk.domain.design.formulas import half_wave_length_m
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.endfed_dialog import EndFedDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


class _RecordingSolver(FakeSolver):
    def __init__(self) -> None:
        self.specs: list[SimulationSpec] = []

    def run(
        self,
        model,
        spec: SimulationSpec,
        *,
        progress_callback=None,
        cancel_token=None,
    ):
        self.specs.append(spec)
        return super().run(
            model,
            spec,
            progress_callback=progress_callback,
            cancel_token=cancel_token,
        )


def test_endfed_dialog_builds_parameters(qtbot: QtBot) -> None:
    dialog = EndFedDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.length_m > 0.0
    assert parameters.feed_height_m == 10.0
    assert parameters.transformer_ratio == 49.0
    assert parameters.matching_capacitance_f == 0.0
    assert parameters.transformer_leakage_inductance_h == 0.0
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


def test_endfed_matching_hints_name_the_preset_defaults(qtbot: QtBot) -> None:
    dialog = EndFedDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    capacitance_hint = dialog._form._matching_capacitance.toolTip()
    leakage_hint = dialog._form._transformer_leakage.toolTip()

    assert "shortened presets start at 100 pF" in capacitance_hint
    assert "standard EFHW starts at 0 pF" in capacitance_hint
    assert "0.198" in leakage_hint
    assert "standard EFHW starts at 0" in leakage_hint


def test_endfed_dialog_selects_the_measured_transformer_model(
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.antennas.endfed import (
        EndFedTransformerModel,
        shortened_efhw_40_10_parameters,
    )

    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=shortened_efhw_40_10_parameters(),
    )
    qtbot.addWidget(dialog)
    index = dialog._form._transformer_model.findData(
        EndFedTransformerModel.SQUASH_PRACTICE_49_1.value
    )
    assert index >= 0

    dialog._form._transformer_model.setCurrentIndex(index)

    assert dialog.parameters().transformer_model is EndFedTransformerModel.SQUASH_PRACTICE_49_1
    assert dialog.parameters().transformer_ratio == pytest.approx(49.0)
    assert dialog._form._transformer_leakage.isEnabled() is False


def test_endfed_dialog_selects_the_measured_transformer_loss(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.endfed import (
        EndFedTransformerLossModel,
        shortened_efhw_40_10_parameters,
    )

    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=shortened_efhw_40_10_parameters(),
    )
    qtbot.addWidget(dialog)
    index = dialog._form._transformer_loss_model.findData(
        EndFedTransformerLossModel.SQUASH_PRACTICE_49_1.value
    )
    assert index >= 0

    dialog._form._transformer_loss_model.setCurrentIndex(index)

    parameters = dialog.parameters()
    assert parameters.transformer_loss_model is EndFedTransformerLossModel.SQUASH_PRACTICE_49_1
    assert parameters.transformer_ratio == pytest.approx(49.0)
    assert parameters.transformer_loss is not None


def test_endfed_dialog_clears_the_measured_loss_when_the_ratio_changes(
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.antennas.endfed import (
        EndFedTransformerLossModel,
        shortened_efhw_40_10_parameters,
    )

    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=shortened_efhw_40_10_parameters(),
    )
    qtbot.addWidget(dialog)
    index = dialog._form._transformer_loss_model.findData(
        EndFedTransformerLossModel.SQUASH_PRACTICE_49_1.value
    )
    dialog._form._transformer_loss_model.setCurrentIndex(index)

    dialog._form._transformer.setValue(9.0)

    assert dialog._form._selected_transformer_loss_model() is EndFedTransformerLossModel.NONE
    assert dialog.parameters().transformer_loss is None


def test_endfed_dialog_sets_the_design_specific_l_network(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_40_10_parameters

    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=shortened_efhw_40_10_parameters(),
    )
    qtbot.addWidget(dialog)
    dialog._form._design_network_group.setChecked(True)
    dialog._form._design_series_l.setValue(1.2)
    dialog._form._design_shunt_c.setValue(82.0)
    dialog._form._design_shunt_at_input.setChecked(True)

    parameters = dialog.parameters()
    assert parameters.design_matching_network is not None
    assert parameters.design_matching_network.series_inductance_h == pytest.approx(1.2e-6)
    assert parameters.design_matching_network.shunt_capacitance_f == pytest.approx(82e-12)
    assert parameters.design_matching_network.shunt_at_input is True

    dialog._form._design_network_group.setChecked(False)
    assert dialog.parameters().design_matching_network is None


def test_endfed_dialog_sets_the_measured_feedpoint_choke(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.endfed import (
        EndFedReturnPath,
        shortened_efhw_40_10_parameters,
    )

    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=shortened_efhw_40_10_parameters(),
    )
    qtbot.addWidget(dialog)
    index = dialog._form._return_path.findData(EndFedReturnPath.COAX_SHIELD.value)
    dialog._form._return_path.setCurrentIndex(index)
    dialog._form._counterpoise_length.setValue(5.0)

    assert not dialog._form._common_mode_choke_group.isHidden()

    dialog._form._common_mode_choke_group.setChecked(True)
    dialog._form._choke_resistance.setValue(120.0)
    dialog._form._choke_reactance.setValue(300.0)
    dialog._form._choke_frequency.setValue(7.1)
    dialog._form._choke_source.setText("VNA measurement")

    parameters = dialog.parameters()
    assert parameters.common_mode_choke is not None
    assert parameters.common_mode_choke.resistance_ohm == pytest.approx(120.0)
    assert parameters.common_mode_choke.reactance_ohm == pytest.approx(300.0)
    assert parameters.common_mode_choke.source == "VNA measurement"


def test_endfed_dialog_hides_the_choke_outside_the_coax_shield_path(
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.antennas.endfed import (
        EndFedReturnPath,
        shortened_efhw_40_10_parameters,
    )

    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=shortened_efhw_40_10_parameters(),
    )
    qtbot.addWidget(dialog)

    assert dialog._form._common_mode_choke_group.isHidden()

    index = dialog._form._return_path.findData(EndFedReturnPath.COUNTERPOISE.value)
    dialog._form._return_path.setCurrentIndex(index)
    assert dialog._form._common_mode_choke_group.isHidden()
    assert dialog.parameters().common_mode_choke is None


def test_endfed_dialog_selects_a_coax_shield_return_path(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.endfed import (
        EndFedReturnPath,
        shortened_efhw_40_10_parameters,
    )

    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=shortened_efhw_40_10_parameters(),
    )
    qtbot.addWidget(dialog)
    index = dialog._form._return_path.findData(EndFedReturnPath.COAX_SHIELD.value)
    assert index >= 0

    dialog._form._return_path.setCurrentIndex(index)
    dialog._form._counterpoise_length.setValue(5.0)

    assert not dialog._form._counterpoise_enabled.isEnabled()
    assert not dialog._form._counterpoise_height.isEnabled()
    assert not dialog._form._installation_return.isEnabled()

    parameters = dialog.parameters()
    assert parameters.return_path is EndFedReturnPath.COAX_SHIELD
    assert parameters.effective_return_length_m == pytest.approx(5.0)
    assert parameters.effective_return_height_m == pytest.approx(0.0)


def test_shortened_endfed_warns_about_the_installation_return_proxy(
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_40_10_parameters

    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=shortened_efhw_40_10_parameters(),
    )
    qtbot.addWidget(dialog)

    warning = dialog._form._model_warning.text()
    assert "installation-return proxy" in warning
    assert "Absolute SWR is informational" in warning
    assert "R/X-sensitive" in warning


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


def test_endfed_dialog_convergence_uses_roe_in_spanish(qtbot: QtBot) -> None:
    dialog = EndFedDialog(
        Translator(Language.SPANISH),
        UnitSystem.METRIC,
        solver=FakeSolver(),
    )
    qtbot.addWidget(dialog)

    dialog._check_button.click()

    text = dialog._check_result.text()
    assert "ROE" in text
    assert "SWR" not in text


def test_endfed_dialog_convergence_uses_the_project_matching_network(
    qtbot: QtBot,
) -> None:
    project = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    solver = _RecordingSolver()
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preset=EndFedPreset.SHORTENED_80_10,
        solver=solver,
        project_matching_network=project,
    )
    qtbot.addWidget(dialog)

    dialog._check_button.click()

    assert len(solver.specs) == 3
    for spec in solver.specs:
        assert spec.matching_network is project
        assert spec.matching_network_override is True


def test_shortened_dialog_exposes_the_primary_matching_network(qtbot: QtBot) -> None:
    dialog = EndFedDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preset=EndFedPreset.SHORTENED_80_10,
        solver=FakeSolver(),
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.matching_capacitance_f == pytest.approx(100e-12)
    assert parameters.transformer_leakage_inductance_h == pytest.approx(198e-9)
    assert dialog._form._matching_capacitance.value() == pytest.approx(100.0)
    assert dialog._form._transformer_leakage.value() == pytest.approx(0.198)
    assert "matching 100 pF" in dialog._form._geometry.text()


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

    assert "primary 100 pF shunt" in dialog._check_result.text()
    assert "SWR is informational" in dialog._check_result.text()
    assert "Impedance converged" in dialog._check_result.text()


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
    assert parameters.matching_capacitance_f == pytest.approx(100e-12)
    assert parameters.transformer_leakage_inductance_h == pytest.approx(198e-9)


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
