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

    parameters = dialog.parameters().to_custom_parameters()

    assert len(parameters.wires) == 2
    assert parameters.feed.wire_id == "leg-1"
    assert parameters.feed.offset_m == 0.0
    assert "Horizontal span" in dialog._geometry.text()


def test_inverted_v_dialog_updates_geometry_and_returns_custom(qtbot: QtBot) -> None:
    dialog = InvertedVDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._included_angle.setValue(90.0)
    dialog._apex_height.setValue(20.0)

    parameters = dialog.parameters()
    custom = parameters.to_custom_parameters()

    assert parameters.included_angle_deg == pytest.approx(90.0)
    assert parameters.end_height_m > 0.0
    assert custom.wires[0].end.z_m == pytest.approx(parameters.end_height_m)
