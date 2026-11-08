# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.biquad import BiquadKind
from antennadesk.ui.dialogs.biquad_dialog import BiquadDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog(kind: BiquadKind = BiquadKind.SINGLE) -> BiquadDialog:
    return BiquadDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        kind=kind,
    )


def test_biquad_dialog_builds_the_single_loop_stack(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Biquad Generator"
    assert parameters.kind is BiquadKind.SINGLE
    assert parameters.loop_count == 2
    assert parameters.reflector_enabled is True
    assert parameters.reflector_spacing_m == pytest.approx(parameters.loop_side_m / 2.0)
    assert len(parameters.to_antenna().wires) == 11
    assert "2 loops" in dialog._form._geometry.text()


def test_biquad_dialog_builds_the_double_variant(qtbot: QtBot) -> None:
    dialog = _dialog(BiquadKind.DOUBLE)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.kind is BiquadKind.DOUBLE
    assert parameters.loop_count == 4
    assert len(parameters.to_antenna().wires) == 17
    assert "4 loops" in dialog._form._geometry.text()


def test_biquad_dialog_scales_starting_dimensions_to_the_frequency(
    qtbot: QtBot,
) -> None:
    from antennadesk.domain.design.formulas import quarter_wave_length_m

    dialog = BiquadDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=28_400_000.0,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.frequency_hz == pytest.approx(28_400_000.0)
    assert parameters.loop_side_m == pytest.approx(
        quarter_wave_length_m(28_400_000.0),
        abs=1e-3,
    )


def test_biquad_dialog_can_disable_the_reflector(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._reflector_enabled.setChecked(False)

    parameters = dialog.parameters()

    assert parameters.reflector_enabled is False
    assert len(parameters.to_antenna().wires) == 7
    assert "off" in dialog._form._geometry.text()


def test_biquad_dialog_loads_the_quarter_wave_starting_dimensions(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form._loop_side.setValue(form._loop_side.value() * 1.5)

    form.load_starting_dimensions()

    parameters = form.parameters()
    assert parameters.reflector_spacing_m == pytest.approx(parameters.loop_side_m / 2.0)
