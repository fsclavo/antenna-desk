# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDoubleSpinBox
from pytestqt.qtbot import QtBot

from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import DisplayUnits, LengthPolicy, UnitSystem
from antennadesk.ui.widgets.form_units import LengthField, LengthFieldSpec


def _field(qtbot: QtBot, *, display_units: DisplayUnits | None = None) -> LengthField:
    spin = QDoubleSpinBox()
    qtbot.addWidget(spin)
    return LengthField(
        spin,
        LengthFieldSpec(minimum_m=0.0001, maximum_m=100.0),
        Translator(Language.ENGLISH),
        display_units or DisplayUnits(length_policy=LengthPolicy.AUTO),
    )


def test_length_field_chooses_cm_and_preserves_the_physical_value(
    qtbot: QtBot,
) -> None:
    field = _field(qtbot)

    field.configure(0.0199)

    assert field.unit == "cm"
    assert field.value_m() == pytest.approx(0.0199)


def test_length_field_switches_to_imperial_inches(qtbot: QtBot) -> None:
    field = _field(qtbot)
    field.configure(0.0199)

    field.set_display_units(DisplayUnits(UnitSystem.IMPERIAL, LengthPolicy.AUTO))

    assert field.unit == "in"
    assert field.value_m() == pytest.approx(0.0199, abs=5e-4)


def test_length_field_uses_a_scale_hint_for_zero(qtbot: QtBot) -> None:
    field = LengthField(
        QDoubleSpinBox(),
        LengthFieldSpec(minimum_m=0.0, maximum_m=1.0, scale_hint="mm"),
        Translator(Language.ENGLISH),
        DisplayUnits(length_policy=LengthPolicy.AUTO),
    )

    field.configure(0.0)

    assert field.unit == "mm"


def test_length_field_respects_fixed_units(qtbot: QtBot) -> None:
    field = _field(
        qtbot,
        display_units=DisplayUnits(UnitSystem.METRIC, LengthPolicy.FIXED),
    )

    field.configure(0.0199)

    assert field.unit == "m"
    assert field.value_m() == pytest.approx(0.0199, abs=5e-4)
