# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.custom_antenna_dialog import CustomAntennaDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_custom_dialog_builds_a_wire_model(qtbot: QtBot) -> None:
    dialog = CustomAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert len(parameters.wires) == 1
    assert parameters.feed.wire_id == "wire-1"
    assert parameters.wires[0].length_m > 0.0
    assert dialog._ground.currentText() == "Free space"
    assert dialog._material.currentText() == "Copper"


def test_custom_dialog_adds_a_second_wire(qtbot: QtBot) -> None:
    dialog = CustomAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(dialog)

    dialog._add_wire()
    parameters = dialog.parameters()

    assert len(parameters.wires) == 2
    assert parameters.feed.wire_id == "wire-1"


def test_custom_dialog_adds_ground_radials(qtbot: QtBot) -> None:
    dialog = CustomAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(dialog)

    dialog._radial_count.setValue(4)
    dialog._add_radials.click()
    parameters = dialog.parameters()

    assert len(parameters.wires) == 5
    assert all(wire.id.startswith("radial-") for wire in parameters.wires[1:])
    assert all(wire.start.z_m == 0.0 for wire in parameters.wires[1:])


def test_custom_dialog_preserves_generator_metadata(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.custom import CustomAntennaParameters
    from antennadesk.domain.antennas.feed import FeedPoint
    from antennadesk.domain.antennas.geometry import Point3D
    from antennadesk.domain.antennas.materials import COPPER
    from antennadesk.domain.antennas.wire import Wire

    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                id="wire-1",
                start=Point3D(-5.0, 0.0, 8.0),
                end=Point3D(5.0, 0.0, 8.0),
                radius_m=0.001,
                material=COPPER,
            ),
        ),
        feed=FeedPoint("wire-1", 5.0),
        generator_id="yagi",
        generator_name="Yagi",
    )
    dialog = CustomAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters().generator_id == "yagi"
    assert dialog.parameters().generator_name == "Yagi"
