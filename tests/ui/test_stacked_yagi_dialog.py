# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Stacked-Yagi dialog and embedded form behavior."""

from __future__ import annotations

from dataclasses import replace

import pytest
from PySide6.QtWidgets import QDialog, QLabel
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.matching_network import design_l_network
from antennadesk.domain.antennas.polarization import Polarization
from antennadesk.domain.antennas.stacked_yagi import (
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from antennadesk.domain.antennas.yagi import YagiElement, YagiMatchType, YagiParameters
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


def test_phase_line_feed_derives_the_phase_and_applies_the_splitter_loss(
    qtbot: QtBot,
) -> None:
    dialog = _dialog(qtbot)
    form = dialog._form
    mode_index = form._feed_mode.findData(StackedYagiFeedMode.PHASE_LINES.value)
    assert mode_index >= 0
    form._feed_mode.setCurrentIndex(mode_index)
    form._reference_line_field.configure(2.0)
    form._line_increment_field.configure(2.5)
    form._velocity_factor.setValue(0.8)
    form._splitter_loss.setValue(0.4)
    form._line_loss.setValue(1.5)
    form._update_geometry()

    parameters = dialog.parameters()

    assert parameters.feed.mode is StackedYagiFeedMode.PHASE_LINES
    assert form._line_loss.isEnabled() is False
    assert parameters.feed.line_increment_m == pytest.approx(2.5, abs=1e-3)
    assert parameters.feed.splitter_loss_db == pytest.approx(0.4, abs=1e-6)
    assert parameters.effective_phase_step_deg < 0.0
    assert "Derived phase step" in form._phase_note.text()
    assert form._phase_step.isEnabled() is False
    assert form._line_increment.isEnabled() is True


def test_network_feed_mode_builds_lossless_phase_lines(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    form = dialog._form
    mode_index = form._feed_mode.findData(StackedYagiFeedMode.NETWORK.value)
    assert mode_index >= 0
    form._feed_mode.setCurrentIndex(mode_index)
    form._reference_line_field.configure(2.0)
    form._line_increment_field.configure(2.5)
    form._velocity_factor.setValue(0.8)
    form._splitter_loss.setValue(0.4)
    form._line_loss.setValue(1.5)
    form._update_geometry()

    parameters = dialog.parameters()
    model = parameters.to_antenna()

    assert parameters.feed.mode is StackedYagiFeedMode.NETWORK
    assert parameters.feed.line_loss_db_per_100m == pytest.approx(1.5, abs=1e-6)
    assert form._line_loss.isEnabled() is True
    assert model.sources == ()
    assert len(model.transmission_lines) == parameters.count
    assert form._phase_step.isEnabled() is False
    assert form._network_note.isVisibleTo(form) or form._network_note.text()
    assert "co-simulated" in form._network_note.text().lower()


def test_dialog_edits_one_shared_mast_for_every_level(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    form = dialog._form
    form._yagi._mast_diameter_field.configure(0.05)
    form._yagi._mast_offset_field.configure(1.5)
    form._yagi._guy_count.setCurrentIndex(form._yagi._guy_count.findData(3))
    form._yagi._guy_anchor_field.configure(4.0)
    form._yagi._guy_diameter_field.configure(0.004)
    form._update_geometry()

    parameters = dialog.parameters()
    model = parameters.to_antenna()

    assert parameters.yagi.mast_diameter_m == pytest.approx(0.05)
    assert parameters.yagi.guy_count == 3
    mast_wires = [wire for wire in model.wires if wire.id == "mast"]
    assert len(mast_wires) == 1
    assert mast_wires[0].end.z_m == pytest.approx(parameters.top_height_m)
    assert len([wire for wire in model.wires if wire.id.startswith("guy-")]) == 3
    assert not any(
        wire.id.startswith("level-") and ("mast" in wire.id or "guy" in wire.id)
        for wire in model.wires
    )


def test_loading_starting_dimensions_preserves_the_shared_mast(qtbot: QtBot) -> None:
    parameters = _parameters()
    parameters = replace(
        parameters,
        yagi=replace(
            parameters.yagi,
            mast_diameter_m=0.05,
            mast_offset_m=1.5,
            guy_count=3,
            guy_anchor_radius_m=4.0,
            guy_diameter_m=0.004,
        ),
    )
    dialog = _dialog(qtbot, parameters=parameters)

    dialog._form.load_starting_dimensions()
    restored = dialog.parameters()

    assert restored.yagi.mast_diameter_m == pytest.approx(0.05)
    assert restored.yagi.mast_offset_m == pytest.approx(1.5)
    assert restored.yagi.guy_count == 3
    assert restored.yagi.guy_anchor_radius_m == pytest.approx(4.0)
    assert restored.yagi.guy_diameter_m == pytest.approx(0.004)


def test_dialog_sets_a_beta_match_on_every_level(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    form = dialog._form
    index = form._yagi._match_type.findData(YagiMatchType.BETA_HAIRPIN.value)
    assert index >= 0
    form._yagi._match_type.setCurrentIndex(index)
    form._yagi._match_length_field.configure(0.3)
    form._yagi._match_spacing_field.configure(0.12)
    form._update_geometry()

    parameters = dialog.parameters()
    model = parameters.to_antenna()

    assert parameters.yagi.match_type is YagiMatchType.BETA_HAIRPIN
    assert parameters.yagi.match_length_m == pytest.approx(0.3)
    assert parameters.yagi.match_spacing_m == pytest.approx(0.12)
    assert model.feed.wire_id == "level-1-element-2-feed"
    assert model.sources[0].wire_id == "level-2-element-2-feed"


def test_loading_starting_dimensions_preserves_the_beta_match(qtbot: QtBot) -> None:
    parameters = _parameters()
    parameters = replace(
        parameters,
        yagi=replace(
            parameters.yagi,
            match_type=YagiMatchType.BETA_HAIRPIN,
            match_length_m=0.3,
            match_spacing_m=0.12,
        ),
    )
    dialog = _dialog(qtbot, parameters=parameters)

    dialog._form.load_starting_dimensions()
    restored = dialog.parameters()

    assert restored.yagi.match_type is YagiMatchType.BETA_HAIRPIN
    assert restored.yagi.match_length_m == pytest.approx(0.3)
    assert restored.yagi.match_spacing_m == pytest.approx(0.12)


def test_dialog_builds_a_wilkinson_feed(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    form = dialog._form
    index = form._feed_mode.findData(StackedYagiFeedMode.WILKINSON.value)
    assert index >= 0
    form._feed_mode.setCurrentIndex(index)
    form._reference_line_field.configure(2.0)
    form._line_increment_field.configure(0.0)
    form._velocity_factor.setValue(0.8)
    form._line_z0.setValue(50.0)
    form._splitter_loss.setValue(0.2)
    form._line_loss.setValue(1.5)
    form._splitter_design_frequency.setValue(14.1)
    form._update_geometry()

    parameters = dialog.parameters()

    assert parameters.feed.mode is StackedYagiFeedMode.WILKINSON
    assert parameters.feed.splitter_design_frequency_hz == pytest.approx(14.1e6)
    assert parameters.feed.line_loss_db_per_100m == pytest.approx(1.5)
    assert form._splitter_design_frequency.isEnabled() is True
    assert form._amplitude_ratio.isEnabled() is False
    assert "Wilkinson" in form._wilkinson_note.text()


def test_dialog_sets_individual_level_matching_networks(qtbot: QtBot) -> None:
    matching_100 = design_l_network(
        100.0 + 0.0j,
        14_100_000.0,
        source_impedance_ohm=50.0,
    )
    matching_25 = design_l_network(
        25.0 + 0.0j,
        14_100_000.0,
        source_impedance_ohm=50.0,
    )
    assert matching_100 is not None
    assert matching_25 is not None
    dialog = _dialog(qtbot)
    form = dialog._form
    index = form._feed_mode.findData(StackedYagiFeedMode.WILKINSON.value)
    form._feed_mode.setCurrentIndex(index)
    form._reference_line_field.configure(2.0)
    form._line_increment_field.configure(0.0)
    form.set_level_matching_network(0, matching_100)
    form.set_level_matching_network(1, matching_25)
    form._update_geometry()

    parameters = dialog.parameters()

    assert parameters.feed.level_matching_networks == (matching_100, matching_25)
    assert "L network" in form._level_matching_summaries[0].text()
    assert "L network" in form._level_matching_summaries[1].text()
    assert form._level_matching_buttons[0].isEnabled() is True
    assert form._level_matching_buttons[1].isEnabled() is True
    assert form._level_matching_rows[2].isHidden() is True
    phase_index = form._feed_mode.findData(StackedYagiFeedMode.PHASE_LINES.value)
    form._feed_mode.setCurrentIndex(phase_index)
    form._update_feed_controls()
    assert form._level_matching_buttons[0].isEnabled() is False
    assert form._level_matching_summaries[0].text() == "Wilkinson mode only"


def test_dialog_allows_folded_driven_elements_without_a_per_level_transformer(
    qtbot: QtBot,
) -> None:
    dialog = _dialog(qtbot)
    form = dialog._form
    yagi_form = form._yagi

    assert yagi_form._driven_folded.isHidden() is False
    assert yagi_form._transformer.isHidden() is True
    yagi_form._driven_folded.setChecked(True)
    form._update_geometry()
    parameters = dialog.parameters()

    assert parameters.yagi.driven_folded is True
    assert parameters.yagi.transformer_ratio == pytest.approx(1.0)
    assert "per-level transformer" in form._folded_note.text()
    assert form._folded_note.isHidden() is False


def test_dialog_sets_per_level_transformers_in_wilkinson_mode(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    form = dialog._form
    index = form._feed_mode.findData(StackedYagiFeedMode.WILKINSON.value)
    form._feed_mode.setCurrentIndex(index)
    form._reference_line_field.configure(2.0)
    form._line_increment_field.configure(0.0)

    form.set_level_transformer_ratio(0, 4.0)
    form.set_level_transformer_ratio(1, 1.5)

    parameters = dialog.parameters()

    assert parameters.feed.level_transformer_ratios == (4.0, 1.5)
    assert form._level_transformer_fields[0].isEnabled() is True
    assert form._level_transformer_rows[2].isHidden() is True
    phase_index = form._feed_mode.findData(StackedYagiFeedMode.PHASE_LINES.value)
    form._feed_mode.setCurrentIndex(phase_index)
    form._update_feed_controls()
    assert form._level_transformer_fields[0].isEnabled() is False
