# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.loop import ANTENNA_TYPE_LOOP
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.dipole_form import DipoleForm


def test_form_shows_family_and_template(qtbot: QtBot) -> None:
    form = DipoleForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)

    assert form._family_value.text() == "Dipole"
    index = form._type.findData(ANTENNA_TYPE_LOOP)
    form._type.setCurrentIndex(index)
    assert form._family_value.text() == "Loop"
