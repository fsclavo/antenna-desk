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

    parameters = dialog.parameters()

    assert parameters.radial_count == 16
    assert parameters.height_m == pytest.approx(10.0)
    assert dialog._ground.currentText() == "Finite ground"
    assert dialog._material.currentText() == "Copper"
    assert dialog._base_height.value() == pytest.approx(0.25)
    assert "16 radials" in dialog._geometry.text()


def test_vertical_dialog_can_disable_radials(qtbot: QtBot) -> None:
    dialog = VerticalDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._radial_count.setValue(0)

    assert dialog._radial_length.isEnabled() is False
    assert dialog.parameters().radial_count == 0


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
        parameters=original,
    )
    qtbot.addWidget(dialog)

    restored = dialog.parameters()
    assert restored.radial_count == 8
    assert restored.radial_length_m == pytest.approx(5.0)
    assert restored.base_height_m == pytest.approx(0.2)


def test_vertical_dialog_can_enable_a_loading_coil(qtbot: QtBot) -> None:
    dialog = VerticalDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert dialog._form._coil_enabled.isChecked() is False
    assert dialog._form._coil_offset.isEnabled() is False
    dialog._form._coil_enabled.setChecked(True)

    assert dialog._form._coil_offset.isEnabled() is True
    assert dialog._form._coil_inductance.isEnabled() is True
    dialog._form._coil_offset.setValue(1.0)
    dialog._form._coil_inductance.setValue(12.0)
    dialog._form._coil_resistance.setValue(0.5)
    parameters = dialog.parameters()

    assert parameters.loading_coil_enabled is True
    assert parameters.loading_coil_offset_m == pytest.approx(1.0)
    assert parameters.loading_coil_inductance_h == pytest.approx(12e-6)
    assert parameters.loading_coil_resistance_ohm == pytest.approx(0.5)
    assert "12.000 µH" in dialog._form._coil_summary.text()


def test_vertical_dialog_can_enable_a_top_hat(qtbot: QtBot) -> None:
    dialog = VerticalDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    form = dialog._form

    assert form._top_hat_enabled.isChecked() is False
    assert form._top_hat_radius.isEnabled() is False

    form._top_hat_enabled.setChecked(True)
    form._top_hat_radius.setValue(0.5)
    form._top_hat_wire_count.setValue(6)

    parameters = dialog.parameters()
    assert parameters.top_hat_enabled is True
    assert parameters.top_hat_radius_m == pytest.approx(0.5)
    assert parameters.top_hat_wire_count == 6
    assert form._top_hat_radius.isEnabled() is True


def test_loaded_vertical_dialog_uses_mobile_preset(qtbot: QtBot) -> None:
    dialog = VerticalDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        mobile=True,
    )
    qtbot.addWidget(dialog)
    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Loaded vertical / mobile whip generator"
    assert parameters.height_m == pytest.approx(2.0)
    assert parameters.radial_count == 4
    assert parameters.radial_length_m == pytest.approx(1.0)
    assert parameters.loading_coil_enabled is True
    assert parameters.loading_coil_offset_m == pytest.approx(1.0)
    assert parameters.loading_coil_inductance_h == pytest.approx(10e-6)


def test_loaded_vertical_dialog_loads_the_published_mobile_example(
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.antennas.vertical import (
        MOBILE_EXAMPLE_COIL_INDUCTANCE_H,
        MOBILE_EXAMPLE_FREQUENCY_HZ,
        MOBILE_EXAMPLE_HEIGHT_M,
    )

    dialog = VerticalDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        mobile=True,
    )
    qtbot.addWidget(dialog)

    dialog._example.click()

    parameters = dialog.parameters()
    assert parameters.frequency_hz == pytest.approx(MOBILE_EXAMPLE_FREQUENCY_HZ)
    assert parameters.height_m == pytest.approx(
        MOBILE_EXAMPLE_HEIGHT_M,
        abs=0.001,
    )
    assert parameters.radial_count == 0
    assert parameters.loading_coil_enabled is True
    assert parameters.loading_coil_offset_m == pytest.approx(0.0)
    assert parameters.loading_coil_inductance_h == pytest.approx(MOBILE_EXAMPLE_COIL_INDUCTANCE_H)
    assert parameters.loading_coil_resistance_ohm == pytest.approx(0.0)


def test_vertical_dialog_restores_a_loading_coil(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    original = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=15e-6,
        loading_coil_resistance_ohm=0.3,
    )
    dialog = VerticalDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    restored = dialog.parameters()
    assert restored.loading_coil_enabled is True
    assert restored.loading_coil_offset_m == pytest.approx(1.0)
    assert restored.loading_coil_inductance_h == pytest.approx(15e-6)
    assert restored.loading_coil_resistance_ohm == pytest.approx(0.3)
