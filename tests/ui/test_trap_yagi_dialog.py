# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.trap_yagi_dialog import TrapYagiDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> TrapYagiDialog:
    return TrapYagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_trap_yagi_dialog_builds_the_default_traps(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Trapped Yagi Generator"
    assert parameters.element_count == 3
    assert len(parameters.to_antenna().wires) == 3
    assert len(parameters.to_antenna().loads) == 6
    assert "3 elements" in dialog._form._geometry.text()


def test_trap_yagi_dialog_updates_the_trap_position(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._element_count.setValue(2)
    dialog._form._trap_inset.setValue(3.0)
    dialog._form._trap_frequency.setValue(14.0)
    dialog._form._trap_inductance.setValue(6.0)

    parameters = dialog.parameters()

    assert parameters.element_count == 2
    assert parameters.trap_inset_m == pytest.approx(3.0, abs=1e-3)
    assert parameters.trap_frequency_hz == pytest.approx(14_000_000.0)
    assert parameters.trap_inductance_h == pytest.approx(6e-6)
    assert len(parameters.to_antenna().loads) == 4


def test_trap_yagi_dialog_seeds_the_elements_at_the_requested_frequency(
    qtbot: QtBot,
) -> None:
    dialog = TrapYagiDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=10_100_000.0,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    assert parameters.frequency_hz == pytest.approx(10_100_000.0)
    assert parameters.high_band_frequency_hz == pytest.approx(20_200_000.0)
    assert parameters.driven_length_m == pytest.approx(14.0992, abs=1e-3)
    assert parameters.reflector_spacing_m == pytest.approx(5.9365, abs=1e-3)
    assert parameters.trap_inset_m == pytest.approx(3.5248, abs=1e-3)


def test_trap_yagi_form_load_starting_preserves_installation_fields(
    qtbot: QtBot,
) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form._frequency.setValue(10.1)
    form._high_band_frequency.setValue(20.2)
    form._trap_frequency.setValue(20.2)
    form._element_count.setValue(2)
    form._trap_inductance.setValue(6.0)
    form._height.setValue(12.0)
    form._azimuth.setValue(30.0)
    form._reflector_scale.setValue(1.1)

    form._starting.click()

    parameters = form.parameters()
    assert parameters.driven_length_m == pytest.approx(14.0992, abs=1e-3)
    assert parameters.trap_inset_m == pytest.approx(3.5248, abs=1e-3)
    assert parameters.trap_inductance_h == pytest.approx(6e-6)
    assert parameters.element_count == 2
    assert parameters.height_m == pytest.approx(12.0)
    assert parameters.azimuth_deg == pytest.approx(30.0)
    assert parameters.reflector_scale == pytest.approx(1.1)


def test_trap_yagi_form_auto_resizes_pristine_geometry(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    form._frequency.setValue(10.1)

    assert form.parameters().driven_length_m == pytest.approx(14.099, abs=1e-3)

    form._height.setValue(12.0)
    form._frequency.setValue(7.05)

    parameters = form.parameters()
    assert parameters.height_m == pytest.approx(12.0)
    assert parameters.driven_length_m > 19.0
    assert parameters.high_band_frequency_hz == pytest.approx(14_100_000.0)

    form._driven_length.setValue(15.0)
    form._frequency.setValue(7.0)

    assert form.parameters().driven_length_m == pytest.approx(15.0)
    assert "not resized" in form._starting_note.text().lower()


def test_trap_yagi_form_preserves_lengths_when_switching_units(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._driven_length.setValue(20.0)
    dialog._form._trap_inset.setValue(3.0)

    dialog._form.set_unit_system(UnitSystem.IMPERIAL)

    parameters = dialog.parameters()
    assert parameters.driven_length_m == pytest.approx(20.0, rel=1e-3)
    assert parameters.trap_inset_m == pytest.approx(3.0, rel=1e-3)
    assert dialog._form._driven_length.suffix().strip() == "ft"
