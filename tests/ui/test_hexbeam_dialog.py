# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.hexbeam_dialog import HexbeamDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> HexbeamDialog:
    return HexbeamDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_hexbeam_dialog_builds_the_published_reference(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Hexbeam Generator"
    assert parameters.driver_half_length_m == pytest.approx(5.5626, abs=1e-3)
    assert parameters.reflector_half_length_m == pytest.approx(5.2578, abs=1e-3)
    assert parameters.turning_radius_m == pytest.approx(3.302, abs=1e-3)
    assert parameters.tip_gap_m == pytest.approx(0.6096, abs=1e-3)
    assert len(parameters.to_antenna().wires) == 9
    assert "driver 5.563 m half" in dialog._form._geometry.text()


def test_hexbeam_dialog_updates_the_wire_path(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._driver_half.setValue(5.8)
    dialog._form._reflector_half.setValue(5.4)
    dialog._form._turning_radius.setValue(3.4)
    dialog._form._tip_gap.setValue(0.7)

    parameters = dialog.parameters()

    assert parameters.driver_half_length_m == pytest.approx(5.8, abs=1e-3)
    assert parameters.reflector_half_length_m == pytest.approx(5.4, abs=1e-3)
    assert parameters.turning_radius_m == pytest.approx(3.4, abs=1e-3)
    assert parameters.tip_gap_m == pytest.approx(0.7, abs=1e-3)
    assert len(parameters.to_antenna().wires) == 9


def test_hexbeam_dialog_sets_the_requested_frequency(qtbot: QtBot) -> None:
    dialog = HexbeamDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=21_200_000.0,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters().frequency_hz == pytest.approx(21_200_000.0)


def test_hexbeam_form_preserves_lengths_when_switching_units(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._driver_half.setValue(5.5)
    dialog._form._turning_radius.setValue(3.3)

    dialog._form.set_unit_system(UnitSystem.IMPERIAL)

    parameters = dialog.parameters()
    assert parameters.driver_half_length_m == pytest.approx(5.5, rel=1e-3)
    assert parameters.turning_radius_m == pytest.approx(3.3, rel=1e-3)
    assert dialog._form._driver_half.suffix().strip() == "ft"
