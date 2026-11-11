# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""End-fed editor inverted-L bend controls."""

from __future__ import annotations

from dataclasses import replace

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.endfed_form import EndFedForm


def test_endfed_form_enables_and_builds_the_bend(qtbot: QtBot) -> None:
    form = EndFedForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.set_parameters(shortened_efhw_80_10_parameters())
    form._bend_enabled.setChecked(True)

    parameters = form.parameters()

    assert parameters.bend_enabled is True
    assert parameters.bend_vertical_length_m == 8.0
    assert parameters.bend_horizontal_length_m == pytest.approx(14.74)
    assert form._end_height.isEnabled() is False
    assert "14.74 m horizontal" in form._bend_horizontal.text()
    assert "top at 18.00 m" in form._bend_horizontal.text()
    assert "horizontal 14.74 m" in form._geometry.text()


def test_endfed_form_restores_a_stored_bend(qtbot: QtBot) -> None:
    parameters = replace(
        shortened_efhw_80_10_parameters(feed_height_m=2.0),
        bend_enabled=True,
        bend_vertical_length_m=8.0,
    )
    form = EndFedForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)

    form.set_parameters(parameters)

    assert form._bend_enabled.isChecked() is True
    assert form._bend_vertical.value() == 8.0
    assert form._end_height.isEnabled() is False
    assert "top at 10.00 m" in form._bend_horizontal.text()
    assert "vertical 8.00 m" in form._geometry.text()


def test_endfed_form_retranslates_the_bend_controls(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    form = EndFedForm(translator, UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.set_parameters(shortened_efhw_80_10_parameters())
    form._bend_enabled.setChecked(True)

    assert form._bend_enabled.text() == "Inverted-L bend"
    assert "Horizontal run" in form._bend_horizontal.text() or "horizontal" in (
        form._bend_horizontal.text()
    )

    translator.set_language(Language.SPANISH)
    form.retranslate()

    assert form._bend_enabled.text() == "Codo en L invertida"
    assert "horizontal" in form._bend_horizontal.text()
    assert "codo" in form._bend_vertical.toolTip()
