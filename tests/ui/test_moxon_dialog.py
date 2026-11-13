# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.moxon import MoxonParameters, moxon_20m_wire
from antennadesk.ui.dialogs.moxon_dialog import MoxonDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.moxon_form import (
    MOXON_DEFAULT_FREQUENCY_HZ,
    MOXON_DEFAULT_HEIGHT_M,
)


def test_moxon_dialog_builds_parameters(qtbot: QtBot) -> None:
    dialog = MoxonDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.width_m > 0.0
    assert parameters.gap_m > 0.0
    assert dialog._form._ground.currentText() == "Finite ground"
    assert dialog._form._polarization.currentText() == "Horizontal"
    assert dialog._form._polarization.itemText(1) == "Vertical"


def test_moxon_dialog_starts_on_10m_with_scaled_reference_geometry(
    qtbot: QtBot,
) -> None:
    dialog = MoxonDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    reference = moxon_20m_wire(
        frequency_hz=MOXON_DEFAULT_FREQUENCY_HZ,
        height_m=MOXON_DEFAULT_HEIGHT_M,
    )

    parameters = dialog.parameters()

    assert parameters.frequency_hz == pytest.approx(MOXON_DEFAULT_FREQUENCY_HZ)
    assert parameters.width_m == pytest.approx(reference.width_m, abs=1e-3)
    assert parameters.depth_m == pytest.approx(reference.depth_m, abs=1e-3)
    assert parameters.reflector_tip_m == pytest.approx(reference.reflector_tip_m, abs=1e-3)
    assert parameters.driven_tip_m == pytest.approx(reference.driven_tip_m, abs=1e-3)
    assert parameters.height_m == pytest.approx(MOXON_DEFAULT_HEIGHT_M)


def test_moxon_dialog_scales_the_starting_geometry_to_a_requested_frequency(
    qtbot: QtBot,
) -> None:
    dialog = MoxonDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=21_000_000.0,
    )
    qtbot.addWidget(dialog)
    reference = moxon_20m_wire(frequency_hz=21_000_000.0, height_m=10.0)

    parameters = dialog.parameters()

    assert parameters.frequency_hz == pytest.approx(21_000_000.0)
    assert parameters.width_m == pytest.approx(reference.width_m, abs=1e-3)
    assert parameters.gap_m == pytest.approx(reference.gap_m, abs=1e-3)


def test_moxon_dialog_scales_the_reference_to_the_current_frequency(
    qtbot: QtBot,
) -> None:
    dialog = MoxonDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._form._frequency.setValue(28.4)
    dialog._form._ground.setCurrentIndex(dialog._form._ground.findData("perfect"))
    dialog._form._radius.setValue(2.0)

    dialog._form._reference.click()

    parameters = dialog.parameters()
    scale = 14_170_000.0 / 28_400_000.0
    assert parameters.frequency_hz == pytest.approx(28_400_000.0)
    assert parameters.width_m == pytest.approx(25.00 * 0.3048 * scale, abs=0.001)
    assert parameters.gap_m == pytest.approx(0.72 * 0.3048 * scale, abs=0.001)
    assert parameters.wire_radius_m == pytest.approx(0.002)
    assert parameters.ground.kind.value == "perfect"
    assert dialog._form._ground.currentText() == "Perfect ground"


def test_moxon_dialog_restores_vertical_polarization(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.polarization import Polarization

    original = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.6,
        depth_m=2.5,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
        polarization=Polarization.VERTICAL,
    )
    dialog = MoxonDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
    assert dialog._form._polarization.currentData() == "vertical"


def test_moxon_dialog_warns_when_the_rectangle_reaches_the_ground(qtbot: QtBot) -> None:
    dialog = MoxonDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog.show()
    dialog._form._height.setValue(1.0)
    index = dialog._form._polarization.findData("vertical")
    dialog._form._polarization.setCurrentIndex(index)

    assert dialog._form._clearance_warning.isHidden() is False
    assert "greater than" in dialog._form._clearance_warning.text()
    with pytest.raises(ValueError, match="below ground"):
        dialog.parameters()


def test_moxon_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    original = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.6,
        depth_m=2.5,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
    )
    dialog = MoxonDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
