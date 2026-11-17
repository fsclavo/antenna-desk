# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

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


def test_quad_beam_dialog_sets_the_requested_frequency(qtbot: QtBot) -> None:
    dialog = QuadBeamDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=21_000_000.0,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters().frequency_hz == pytest.approx(21_000_000.0)


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
