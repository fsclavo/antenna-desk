# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.discone_dialog import DisconeDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> DisconeDialog:
    return DisconeDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_discone_dialog_builds_the_default_radials(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Discone Generator"
    assert parameters.wire_count == 12
    assert len(parameters.to_antenna().wires) == 25
    assert "12 radial wires" in dialog._form._geometry.text()


def test_discone_dialog_updates_the_cone_and_disc(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._wire_count.setValue(8)
    dialog._form._cone_height.setValue(0.5)
    dialog._form._cone_radius.setValue(0.3)
    dialog._form._disc_radius.setValue(0.6)

    parameters = dialog.parameters()

    assert parameters.wire_count == 8
    assert parameters.cone_height_m == pytest.approx(0.5, abs=1e-3)
    assert parameters.cone_radius_m == pytest.approx(0.3, abs=1e-3)
    assert parameters.disc_radius_m == pytest.approx(0.6, abs=1e-3)
    assert len(parameters.to_antenna().wires) == 17


def test_discone_dialog_sets_the_requested_frequency(qtbot: QtBot) -> None:
    dialog = DisconeDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=50_000_000.0,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters().frequency_hz == pytest.approx(50_000_000.0)


def test_discone_form_preserves_lengths_when_switching_units(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._cone_height.setValue(0.5)
    dialog._form._disc_radius.setValue(0.6)

    dialog._form.set_unit_system(UnitSystem.IMPERIAL)

    parameters = dialog.parameters()
    assert parameters.cone_height_m == pytest.approx(0.5, rel=1e-3)
    assert parameters.disc_radius_m == pytest.approx(0.6, rel=1e-3)
    assert dialog._form._cone_height.suffix().strip() == "ft"
