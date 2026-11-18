# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.hexbeam_dialog import HexbeamDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> HexbeamDialog:
    return HexbeamDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_hexbeam_dialog_builds_the_published_reference(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Hexbeam Generator"
    assert parameters.driver_half_length_m == pytest.approx(5.5626, abs=1e-3)
    assert parameters.reflector_half_length_m == pytest.approx(5.2578, abs=1e-3)
    assert parameters.turning_radius_m == pytest.approx(3.302, abs=1e-3)
    assert parameters.tip_gap_m == pytest.approx(0.6096, abs=1e-3)
    assert len(parameters.to_antenna().wires) == 10
    assert "driver 5.563 m half" in dialog._form._geometry.text()


def test_hexbeam_dialog_updates_the_wire_path(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._driver_half.setValue(5.84)
    dialog._form._reflector_half.setValue(5.52)
    dialog._form._turning_radius.setValue(3.47)
    dialog._form._tip_gap.setValue(0.64)

    parameters = dialog.parameters()

    assert parameters.driver_half_length_m == pytest.approx(5.84, abs=1e-3)
    assert parameters.reflector_half_length_m == pytest.approx(5.52, abs=1e-3)
    assert parameters.turning_radius_m == pytest.approx(3.47, abs=1e-3)
    assert parameters.tip_gap_m == pytest.approx(0.64, abs=1e-3)
    assert len(parameters.to_antenna().wires) == 10


def test_hexbeam_dialog_seeds_the_reference_at_the_requested_frequency(
    qtbot: QtBot,
) -> None:
    dialog = HexbeamDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=21_200_000.0,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    assert parameters.frequency_hz == pytest.approx(21_200_000.0)
    assert parameters.driver_half_length_m == pytest.approx(3.7217, abs=1e-3)
    assert parameters.reflector_half_length_m == pytest.approx(3.5178, abs=1e-3)


def test_hexbeam_form_load_starting_preserves_installation_fields(
    qtbot: QtBot,
) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form._frequency.setValue(21.2)
    form._height.setValue(12.0)
    form._azimuth.setValue(30.0)
    form._driver_half.setValue(10.0)

    form._starting.click()

    parameters = form.parameters()
    assert parameters.driver_half_length_m == pytest.approx(3.7217, abs=1e-3)
    assert parameters.height_m == pytest.approx(12.0)
    assert parameters.azimuth_deg == pytest.approx(30.0)


def test_hexbeam_form_auto_resizes_pristine_geometry(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    form._frequency.setValue(21.2)

    assert form.parameters().driver_half_length_m == pytest.approx(3.7217, abs=1e-3)

    form._height.setValue(12.0)
    form._frequency.setValue(28.4)

    assert form.parameters().height_m == pytest.approx(12.0)
    assert form.parameters().driver_half_length_m < 3.0

    form._driver_half.setValue(2.82)
    form._frequency.setValue(30.0)

    assert form.parameters().driver_half_length_m == pytest.approx(2.82)
    assert "not resized" in form._starting_note.text().lower()


def test_hexbeam_form_preserves_lengths_when_switching_units(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._driver_half.setValue(5.5)
    dialog._form._turning_radius.setValue(3.3)

    dialog._form.set_unit_system(UnitSystem.IMPERIAL)

    parameters = dialog.parameters()
    assert parameters.driver_half_length_m == pytest.approx(5.5, rel=1e-3)
    assert parameters.turning_radius_m == pytest.approx(3.3, rel=1e-3)
    assert dialog._form._driver_half.suffix().strip() == "ft"


def test_hexbeam_form_represents_uhf_tip_and_feed_gaps(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters

    dialog = _dialog()
    qtbot.addWidget(dialog)
    parameters = published_hexbeam_parameters(
        frequency_hz=435_000_000.0,
        height_m=10.0,
    )

    dialog._form.set_parameters(parameters)

    restored = dialog.parameters()
    assert restored.tip_gap_m == pytest.approx(parameters.tip_gap_m, abs=5e-4)
    assert restored.feed_gap_m == pytest.approx(parameters.feed_gap_m, abs=5e-4)
    assert restored.element_separation_m == pytest.approx(
        parameters.element_separation_m,
        abs=5e-4,
    )
    assert dialog._form._tip_gap.value() > 0.0
    assert dialog._form._feed_gap.value() > 0.0


def test_hexbeam_form_uses_per_field_units_when_auto(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters
    from antennadesk.ui.units import DisplayUnits, LengthPolicy
    from antennadesk.ui.widgets.hexbeam_form import HexbeamForm

    form = HexbeamForm(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        display_units=DisplayUnits(UnitSystem.METRIC, LengthPolicy.AUTO),
    )
    qtbot.addWidget(form)
    form.set_parameters(published_hexbeam_parameters(frequency_hz=435_000_000.0))

    assert form._driver_half_field.unit == "cm"
    assert form._turning_radius_field.unit == "cm"
    assert form._tip_gap_field.unit == "cm"
    assert form._height_field.unit == "m"
