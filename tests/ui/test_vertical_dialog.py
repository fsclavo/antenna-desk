# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.vertical_dialog import VerticalDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_vertical_dialog_builds_radiator_and_radials(qtbot: QtBot) -> None:
    dialog = VerticalDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters().to_custom_parameters()

    assert len(parameters.wires) == 17
    assert parameters.feed.wire_id == "radiator"
    assert parameters.generator_name == "Vertical"
    assert "16 radials" in dialog._geometry.text()


def test_vertical_dialog_can_disable_radials(qtbot: QtBot) -> None:
    dialog = VerticalDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._radial_count.setValue(0)

    assert dialog._radial_length.isEnabled() is False
    assert len(dialog.parameters().to_custom_parameters().wires) == 1
