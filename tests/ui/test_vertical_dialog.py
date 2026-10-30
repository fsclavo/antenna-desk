# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
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
    assert dialog._ground.currentText() == "Finite ground"
    assert dialog._material.currentText() == "Copper"
    assert "16 radials" in dialog._geometry.text()


def test_vertical_dialog_can_disable_radials(qtbot: QtBot) -> None:
    dialog = VerticalDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._radial_count.setValue(0)

    assert dialog._radial_length.isEnabled() is False
    assert len(dialog.parameters().to_custom_parameters().wires) == 1


def test_vertical_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    original = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.2,
        radial_count=8,
        radial_length_m=5.0,
        radial_angle_deg=22.5,
    )
    dialog = VerticalDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original.to_custom_parameters(),
    )
    qtbot.addWidget(dialog)

    restored = dialog.parameters()
    assert restored.radial_count == 8
    assert restored.radial_length_m == pytest.approx(5.0)
    assert restored.base_height_m == pytest.approx(0.2)
