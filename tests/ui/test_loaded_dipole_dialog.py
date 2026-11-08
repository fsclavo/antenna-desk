# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.loaded_dipole_dialog import LoadedDipoleDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> LoadedDipoleDialog:
    return LoadedDipoleDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_loaded_dipole_dialog_builds_two_coils(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Loaded / Linked Dipole Generator"
    assert parameters.loading_coil_enabled is True
    assert len(parameters.to_antenna().loads) == 2
    assert "µH" in dialog._form._geometry.text()


def test_loaded_dipole_dialog_can_open_the_links(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._link_open.setChecked(True)

    parameters = dialog.parameters()

    assert parameters.link_open is True
    assert parameters.to_antenna().loads == ()
    assert "links open" in dialog._form._geometry.text()
    assert dialog._form._total_length.isEnabled() is False


def test_loaded_dipole_dialog_disables_the_coils(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._coil_enabled.setChecked(False)

    parameters = dialog.parameters()

    assert parameters.coil_active is False
    assert parameters.to_antenna().loads == ()
    assert dialog._form._inductance.isEnabled() is False


def test_loaded_dipole_dialog_sets_the_requested_frequency(qtbot: QtBot) -> None:
    dialog = LoadedDipoleDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=3_500_000.0,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters().frequency_hz == pytest.approx(3_500_000.0)
