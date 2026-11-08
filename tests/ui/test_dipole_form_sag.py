# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleOrientation, DipoleParameters
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.dipole_form import DipoleForm


def test_dipole_form_round_trips_sag(qtbot: QtBot) -> None:
    form = DipoleForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        sag_m=1.2,
    )

    form.set_parameters(parameters)

    assert form.parameters().sag_m == pytest.approx(1.2)
    assert form._sag.isEnabled() is True


def test_dipole_form_preserves_sag_when_switching_units(qtbot: QtBot) -> None:
    form = DipoleForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.set_parameters(
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
            sag_m=1.2,
        )
    )

    form.set_unit_system(UnitSystem.IMPERIAL)

    assert form.parameters().sag_m == pytest.approx(1.2, abs=1e-3)


def test_dipole_form_disables_sag_for_vertical_orientation(qtbot: QtBot) -> None:
    form = DipoleForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.set_parameters(
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=2.0,
            orientation=DipoleOrientation.VERTICAL,
        )
    )

    assert form._sag.isEnabled() is False
