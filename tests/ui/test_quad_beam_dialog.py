# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.quad_beam import QuadBeamParameters
from antennadesk.ui.dialogs.quad_beam_dialog import QuadBeamDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> QuadBeamDialog:
    return QuadBeamDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_quad_beam_dialog_builds_the_default_beam(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Quad Beam Generator"
    assert parameters.element_count == 2
    assert parameters.transformer_ratio == pytest.approx(4.0)
    assert len(parameters.to_antenna().wires) == 8
    assert "2 loops" in dialog._form._geometry.text()
    assert dialog._form._director_spacing.isEnabled() is False


def test_quad_beam_dialog_switches_to_the_three_element_transformer(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    dialog._form._element_count.setValue(3)

    assert dialog.parameters().transformer_ratio == pytest.approx(2.0)


def test_quad_beam_dialog_preserves_a_custom_transformer(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._transformer.setValue(6.0)

    dialog._form._element_count.setValue(3)

    assert dialog.parameters().transformer_ratio == pytest.approx(6.0)


def test_quad_beam_dialog_can_show_the_raw_impedance(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._transformer.setValue(1.0)

    assert dialog.parameters().transformer_ratio == pytest.approx(1.0)


def test_quad_beam_form_load_starting_keeps_the_transformer(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form._transformer.setValue(6.0)
    form._loop_side.setValue(form._loop_side.value() * 1.2)

    form.load_starting_dimensions()

    assert form.parameters().transformer_ratio == pytest.approx(6.0)


def test_quad_beam_dialog_enables_the_director_fields(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._element_count.setValue(3)
    dialog._form._director_spacing.setValue(3.0)
    dialog._form._director_scale.setValue(0.92)

    parameters = dialog.parameters()

    assert parameters.element_count == 3
    assert parameters.director_spacing_m == pytest.approx(3.0)
    assert parameters.director_scale == pytest.approx(0.92, abs=1e-3)
    assert len(parameters.to_antenna().wires) == 12
    assert dialog._form._director_spacing.isEnabled() is True


def test_quad_beam_dialog_seeds_starting_dimensions_at_requested_frequency(
    qtbot: QtBot,
) -> None:
    dialog = QuadBeamDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=144_000_000.0,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.frequency_hz == pytest.approx(144_000_000.0)
    assert parameters.loop_side_m == pytest.approx(0.494, abs=0.002)
    assert parameters.reflector_spacing_m == pytest.approx(0.416, abs=0.002)


def test_quad_beam_form_load_starting_preserves_installation_fields(
    qtbot: QtBot,
) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form._frequency.setValue(144.0)
    form._height.setValue(3.2)
    form._transformer.setValue(6.0)
    form._reflector_scale.setValue(1.1)
    form._loop_side.setValue(5.0)

    form.load_starting_dimensions()

    parameters = form.parameters()
    assert parameters.loop_side_m == pytest.approx(0.494, abs=0.002)
    assert parameters.height_m == pytest.approx(3.2, abs=1e-6)
    assert parameters.transformer_ratio == pytest.approx(6.0)
    assert parameters.reflector_scale == pytest.approx(1.1, abs=1e-3)


def test_quad_beam_form_load_starting_action_updates_the_geometry(
    qtbot: QtBot,
) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form._frequency.setValue(144.0)
    form._loop_side.setValue(5.0)

    form._starting.click()

    assert dialog.parameters().loop_side_m == pytest.approx(0.494, abs=0.002)


def test_quad_beam_dialog_retranslates_the_starting_action(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    dialog = QuadBeamDialog(translator, UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert dialog._form._starting.text() == "Load starting dimensions"

    dialog._form._frequency.setValue(144.0)
    assert "Starting dimensions updated" in dialog._form._starting_note.text()

    translator.set_language(Language.SPANISH)
    dialog._form.retranslate()

    assert dialog._form._starting.text() == "Cargar dimensiones iniciales"
    assert "Dimensiones iniciales actualizadas" in dialog._form._starting_note.text()


def test_quad_beam_form_auto_resizes_pristine_geometry(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    form._frequency.setValue(144.0)

    assert form.parameters().loop_side_m == pytest.approx(0.494, abs=0.002)
    assert form._starting_note.isHidden() is False
    assert "updated" in form._starting_note.text().lower()

    form._height.setValue(12.0)
    form._frequency.setValue(145.0)

    parameters = form.parameters()
    assert parameters.loop_side_m == pytest.approx(0.491, abs=0.002)
    assert parameters.height_m == pytest.approx(12.0)


def test_quad_beam_form_does_not_resize_edited_geometry(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form._frequency.setValue(144.0)
    form._loop_side.setValue(0.6)

    form._frequency.setValue(145.0)

    assert form.parameters().loop_side_m == pytest.approx(0.6)
    assert "not resized" in form._starting_note.text().lower()

    form._starting.click()

    assert form.parameters().loop_side_m == pytest.approx(0.491, abs=0.002)


def test_quad_beam_form_loaded_parameters_are_not_pristine(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form.set_parameters(
        QuadBeamParameters(
            frequency_hz=14_100_000.0,
            loop_side_m=5.2,
            reflector_spacing_m=4.0,
            height_m=10.0,
        )
    )

    form._frequency.setValue(144.0)

    assert form.parameters().loop_side_m == pytest.approx(5.2)
    assert "not resized" in form._starting_note.text().lower()


def test_quad_beam_form_preserves_lengths_when_switching_units(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._loop_side.setValue(5.0)
    dialog._form._reflector_spacing.setValue(4.0)

    dialog._form.set_unit_system(UnitSystem.IMPERIAL)

    parameters = dialog.parameters()
    assert parameters.loop_side_m == pytest.approx(5.0, rel=1e-3)
    assert parameters.reflector_spacing_m == pytest.approx(4.0, rel=1e-3)
    assert dialog._form._loop_side.suffix().strip() == "ft"
