# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.inverted_v_dialog import InvertedVDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_inverted_v_dialog_builds_two_wires(qtbot: QtBot) -> None:
    dialog = InvertedVDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.leg_length_m > 0.0
    assert parameters.included_angle_deg == 120.0
    assert parameters.ground.kind.value == "finite"
    assert dialog._ground.currentText() == "Finite ground"
    assert dialog._material.currentText() == "Copper"
    assert "Horizontal span" in dialog._geometry.text()


def test_inverted_v_dialog_updates_geometry_and_returns_custom(qtbot: QtBot) -> None:
    dialog = InvertedVDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._included_angle.setValue(90.0)
    dialog._apex_height.setValue(20.0)

    parameters = dialog.parameters()

    assert parameters.included_angle_deg == pytest.approx(90.0)
    assert parameters.end_height_m > 0.0


def test_inverted_v_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.inverted_v import InvertedVParameters

    original = InvertedVParameters(
        frequency_hz=7_100_000.0,
        leg_length_m=10.6,
        apex_height_m=12.0,
        included_angle_deg=110.0,
        azimuth_deg=25.0,
    )
    dialog = InvertedVDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    restored = dialog.parameters()
    assert restored.included_angle_deg == pytest.approx(110.0)
    assert restored.azimuth_deg == pytest.approx(25.0)
    assert restored.leg_length_m == pytest.approx(10.6)


def test_inverted_v_form_uses_per_field_units_when_auto(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.inverted_v import InvertedVParameters
    from antennadesk.ui.units import DisplayUnits, LengthPolicy
    from antennadesk.ui.widgets.inverted_v_form import InvertedVForm

    form = InvertedVForm(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        display_units=DisplayUnits(UnitSystem.METRIC, LengthPolicy.AUTO),
    )
    qtbot.addWidget(form)
    form.set_parameters(
        InvertedVParameters(
            frequency_hz=7_100_000.0,
            leg_length_m=10.6,
            apex_height_m=12.0,
        )
    )

    assert form._leg_length_field.unit == "m"
    assert form._apex_height_field.unit == "m"
