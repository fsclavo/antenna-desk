# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.phased_vertical_dialog import PhasedVerticalDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> PhasedVerticalDialog:
    return PhasedVerticalDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_phased_vertical_dialog_builds_the_default_array(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Phased Vertical Array Generator"
    assert parameters.element_count == 2
    assert len(parameters.to_antenna().sources) == 1
    assert "2 verticals" in dialog._form._geometry.text()


def test_phased_vertical_dialog_warns_about_overlapping_radial_screens(
    qtbot: QtBot,
) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    assert dialog._form._overlap_warning.isHidden() is False
    assert "overlap" in dialog._form._overlap_warning.text().lower()

    dialog._form._radial_length.setValue(2.0)

    assert dialog._form._overlap_warning.isHidden() is True


def test_phased_vertical_dialog_updates_the_pattern_of_sources(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._element_count.setValue(3)
    dialog._form._phase_step.setValue(120.0)
    dialog._form._amplitude_taper.setValue(0.3)

    parameters = dialog.parameters()
    sources = parameters.to_antenna().sources

    assert parameters.element_count == 3
    assert [source.phase_deg for source in sources] == pytest.approx([120.0, 240.0])
    assert [source.amplitude for source in sources] == pytest.approx([0.85, 0.7])
    assert "3 verticals" in dialog._form._geometry.text()


def test_phased_vertical_dialog_seeds_the_array_at_the_requested_frequency(
    qtbot: QtBot,
) -> None:
    dialog = PhasedVerticalDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=3_500_000.0,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    assert parameters.frequency_hz == pytest.approx(3_500_000.0)
    assert parameters.height_m == pytest.approx(20.3431, abs=1e-3)
    assert parameters.spacing_m == pytest.approx(20.3431, abs=1e-3)
    assert parameters.radial_length_m == pytest.approx(20.3431, abs=1e-3)


def test_phased_vertical_form_load_starting_preserves_installation_fields(
    qtbot: QtBot,
) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form._frequency.setValue(3.5)
    form._base_height.setValue(1.0)
    form._phase_step.setValue(120.0)
    form._amplitude_taper.setValue(0.3)
    form._radial_count.setValue(8)
    form._radial_angle.setValue(45.0)
    form._azimuth.setValue(30.0)

    form._starting.click()

    parameters = form.parameters()
    assert parameters.height_m == pytest.approx(20.3431, abs=1e-3)
    assert parameters.spacing_m == pytest.approx(20.3431, abs=1e-3)
    assert parameters.radial_length_m == pytest.approx(20.3431, abs=1e-3)
    assert parameters.base_height_m == pytest.approx(1.0)
    assert parameters.phase_step_deg == pytest.approx(120.0)
    assert parameters.amplitude_taper == pytest.approx(0.3)
    assert parameters.radial_count == 8
    assert parameters.radial_angle_deg == pytest.approx(45.0)
    assert parameters.azimuth_deg == pytest.approx(30.0)


def test_phased_vertical_form_auto_resizes_pristine_geometry(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    form._frequency.setValue(3.5)

    assert form.parameters().height_m == pytest.approx(20.3431, abs=1e-3)

    form._base_height.setValue(1.0)
    form._frequency.setValue(7.0)

    assert form.parameters().base_height_m == pytest.approx(1.0)
    assert form.parameters().height_m < 11.0

    form._height.setValue(11.0)
    form._frequency.setValue(14.1)

    assert form.parameters().height_m == pytest.approx(11.0)
    assert "not resized" in form._starting_note.text().lower()


def test_phased_vertical_form_converts_units(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._height.setValue(5.0)
    dialog._form._spacing.setValue(6.0)

    dialog._form.set_unit_system(UnitSystem.IMPERIAL)
    parameters = dialog.parameters()

    assert parameters.height_m == pytest.approx(5.0, rel=1e-3)
    assert parameters.spacing_m == pytest.approx(6.0, rel=1e-3)
    assert dialog._form._height.suffix().strip() == "ft"


def test_phased_vertical_form_uses_per_field_units_when_auto(qtbot: QtBot) -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters
    from antennadesk.ui.units import DisplayUnits, LengthPolicy
    from antennadesk.ui.widgets.phased_vertical_form import PhasedVerticalForm

    form = PhasedVerticalForm(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        display_units=DisplayUnits(UnitSystem.METRIC, LengthPolicy.AUTO),
    )
    qtbot.addWidget(form)
    parameters = replace(
        phased_vertical_parameters(frequency_hz=14_100_000.0),
        base_height_m=0.25,
    )
    form.set_parameters(parameters)

    assert form._spacing_field.unit == "m"
    assert form._radial_length_field.unit == "m"
    assert form._height_field.unit == "m"
    assert form._base_height_field.unit == "cm"
