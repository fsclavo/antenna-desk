# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleOrientation
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.design.formulas import half_wave_length_m
from antennadesk.ui.dialogs.trap_dipole_dialog import TrapDipoleDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_trap_dipole_dialog_builds_starting_dimensions(qtbot: QtBot) -> None:
    dialog = TrapDipoleDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert parameters.high_band_frequency_hz == pytest.approx(14_100_000.0)
    assert parameters.inner_length_m == pytest.approx(half_wave_length_m(14_100_000.0), abs=0.001)
    assert parameters.total_length_m == pytest.approx(half_wave_length_m(7_100_000.0), abs=0.001)
    assert parameters.trap_frequency_hz == pytest.approx(14_100_000.0)
    assert parameters.trap_inductance_h == pytest.approx(10e-6)
    assert parameters.trap_capacitance_f > 0.0
    assert dialog._trap_capacitance.text().endswith("pF")
    assert dialog._ground.currentText() == "Finite ground"


def test_trap_dipole_starting_button_recomputes_lengths(qtbot: QtBot) -> None:
    dialog = TrapDipoleDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._inner_length.setValue(1.0)
    dialog._outer_length.setValue(1.0)

    dialog._start.click()

    parameters = dialog.parameters()
    assert parameters.inner_length_m == pytest.approx(half_wave_length_m(14_100_000.0), abs=0.001)
    assert parameters.total_length_m == pytest.approx(half_wave_length_m(7_100_000.0), abs=0.001)


def test_trap_dipole_dialog_rejects_inverted_bands(qtbot: QtBot) -> None:
    dialog = TrapDipoleDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._high_band.setValue(7.0)

    with pytest.raises(ValueError, match="high_band_frequency_hz"):
        dialog.parameters()
    assert dialog._start.isEnabled() is False


def test_trap_dipole_dialog_disables_azimuth_for_vertical(qtbot: QtBot) -> None:
    dialog = TrapDipoleDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    dialog._orientation.setCurrentIndex(
        dialog._orientation.findData(DipoleOrientation.VERTICAL.value)
    )

    assert dialog._azimuth.isEnabled() is False
    assert dialog._form._height_label.text() == "Base height"


def test_trap_dipole_dialog_restores_existing_parameters(qtbot: QtBot) -> None:
    original = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=21_200_000.0,
        inner_length_m=6.0,
        outer_length_m=7.0,
        trap_frequency_hz=21_200_000.0,
        trap_inductance_h=5e-6,
        height_m=9.0,
        orientation=DipoleOrientation.VERTICAL,
    )
    dialog = TrapDipoleDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    restored = dialog.parameters()
    assert restored.high_band_frequency_hz == pytest.approx(21_200_000.0)
    assert restored.inner_length_m == pytest.approx(6.0)
    assert restored.outer_length_m == pytest.approx(7.0)
    assert restored.trap_inductance_h == pytest.approx(5e-6)
    assert restored.orientation is DipoleOrientation.VERTICAL


def test_trap_dipole_dialog_warns_when_trap_is_below_the_high_band(
    qtbot: QtBot,
) -> None:
    dialog = TrapDipoleDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    dialog._trap_frequency.setValue(10.0)

    assert "below the high band" in dialog._form._trap_warning.text()
