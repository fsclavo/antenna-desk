# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleOrientation
from antennadesk.domain.antennas.t2fd import (
    T2FDParameters,
    t2fd_starting_dimensions,
)
from antennadesk.ui.dialogs.t2fd_dialog import T2FDDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_t2fd_dialog_builds_starting_dimensions(qtbot: QtBot) -> None:
    dialog = T2FDDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    span_m, spacing_m = t2fd_starting_dimensions(3_500_000.0)

    assert parameters.frequency_hz == pytest.approx(3_500_000.0)
    assert parameters.highest_frequency_hz == pytest.approx(30_000_000.0)
    assert parameters.length_m == pytest.approx(span_m, abs=0.001)
    assert parameters.spacing_m == pytest.approx(spacing_m, abs=0.001)
    assert parameters.termination_resistance_ohm == pytest.approx(800.0)
    assert parameters.transformer_ratio == pytest.approx(16.0)
    assert dialog._ground.currentText() == "Finite ground"
    assert "800 Ω" in dialog._geometry.text()
    assert "16:1" in dialog._geometry.text()


def test_t2fd_starting_button_recomputes_dimensions(qtbot: QtBot) -> None:
    dialog = T2FDDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._length.setValue(1.0)
    dialog._spacing.setValue(0.1)

    dialog._start.click()

    parameters = dialog.parameters()
    span_m, spacing_m = t2fd_starting_dimensions(3_500_000.0)
    assert parameters.length_m == pytest.approx(span_m, abs=0.001)
    assert parameters.spacing_m == pytest.approx(spacing_m, abs=0.001)


def test_t2fd_dialog_rejects_an_inverted_band(qtbot: QtBot) -> None:
    dialog = T2FDDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._highest_frequency.setValue(3.0)

    with pytest.raises(ValueError, match="highest_frequency_hz"):
        dialog.parameters()
    assert dialog._start.isEnabled() is False
    assert "must be above" in dialog._band_warning.text()


def test_t2fd_dialog_disables_azimuth_for_vertical(qtbot: QtBot) -> None:
    dialog = T2FDDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    dialog._orientation.setCurrentIndex(
        dialog._orientation.findData(DipoleOrientation.VERTICAL.value)
    )

    assert dialog._azimuth.isEnabled() is False
    assert dialog._form._height_label.text() == "Base height"


def test_t2fd_dialog_restores_existing_parameters(qtbot: QtBot) -> None:
    original = T2FDParameters(
        frequency_hz=5_000_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=18.0,
        spacing_m=0.6,
        height_m=9.0,
        orientation=DipoleOrientation.VERTICAL,
        termination_resistance_ohm=820.0,
        transformer_ratio=9.0,
        azimuth_deg=45.0,
    )
    dialog = T2FDDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    restored = dialog.parameters()
    assert restored == original
    assert dialog._orientation.currentData() == DipoleOrientation.VERTICAL.value


def test_t2fd_dialog_uses_the_previous_design_frequency(qtbot: QtBot) -> None:
    dialog = T2FDDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    span_m, _spacing_m = t2fd_starting_dimensions(7_100_000.0)

    assert parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert parameters.highest_frequency_hz == pytest.approx(30_000_000.0)
    assert parameters.length_m == pytest.approx(span_m, abs=0.001)
