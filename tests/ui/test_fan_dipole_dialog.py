# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.ui.dialogs.fan_dipole_dialog import FanDipoleDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_fan_dipole_dialog_builds_parameters(qtbot: QtBot) -> None:
    dialog = FanDipoleDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert len(parameters.elements) == 2
    assert dialog._table.rowCount() == 2
    assert dialog._form._ground.currentText() == "Finite ground"


def test_fan_dipole_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    original = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(
            FanElement(length_m=20.0, included_angle_deg=120.0),
            FanElement(length_m=10.0, included_angle_deg=90.0),
        ),
        apex_height_m=12.0,
    )
    dialog = FanDipoleDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original


def test_fan_dipole_add_element_uses_a_distinct_angle(qtbot: QtBot) -> None:
    dialog = FanDipoleDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    dialog._form._add_element()

    parameters = dialog.parameters()
    angles = [element.included_angle_deg for element in parameters.elements]
    assert len(angles) == 3
    assert len(set(angles)) == len(angles)


def test_fan_dipole_form_uses_per_field_and_per_table_units_when_auto(
    qtbot: QtBot,
) -> None:
    from antennadesk.ui.units import DisplayUnits, LengthPolicy
    from antennadesk.ui.widgets.fan_dipole_form import FanDipoleForm

    form = FanDipoleForm(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        display_units=DisplayUnits(UnitSystem.METRIC, LengthPolicy.AUTO),
    )
    qtbot.addWidget(form)
    form.set_parameters(
        FanDipoleParameters(
            frequency_hz=435_000_000.0,
            elements=(
                FanElement(length_m=0.16, included_angle_deg=120.0),
                FanElement(length_m=0.33, included_angle_deg=90.0),
            ),
            apex_height_m=12.0,
        )
    )

    assert form._table_unit == "cm"
    assert form._apex_height_field.unit == "m"
    assert "(cm)" in form._table.horizontalHeaderItem(0).text()
    assert form.parameters().elements[0].length_m == pytest.approx(0.16, abs=1e-3)
