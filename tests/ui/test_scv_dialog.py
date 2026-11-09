# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.scv import (
    BOBTAIL_REFERENCE_HORIZONTAL_LENGTH_M,
    BOBTAIL_REFERENCE_VERTICAL_HEIGHT_M,
    HALF_SQUARE_REFERENCE_HORIZONTAL_LENGTH_M,
    HALF_SQUARE_REFERENCE_VERTICAL_HEIGHT_M,
    SCV_REFERENCE_FREQUENCY_HZ,
    ScvKind,
    ScvParameters,
)
from antennadesk.ui.dialogs.scv_dialog import ScvDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem, radius_from_m


def test_scv_dialog_builds_a_half_square_by_default(qtbot: QtBot) -> None:
    dialog = ScvDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    assert parameters.kind is ScvKind.HALF_SQUARE
    assert parameters.horizontal_length_m > 0.0
    assert parameters.vertical_height_m > 0.0
    assert dialog._form._ground.currentText() == "Finite ground"


def test_scv_dialog_can_start_with_the_bobtail_variant(qtbot: QtBot) -> None:
    dialog = ScvDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        kind=ScvKind.BOBTAIL_CURTAIN,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    assert parameters.kind is ScvKind.BOBTAIL_CURTAIN
    assert len(parameters.to_custom_parameters().wires) == 5


def test_scv_dialog_loads_the_published_cebik_reference(qtbot: QtBot) -> None:
    dialog = ScvDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        kind=ScvKind.BOBTAIL_CURTAIN,
    )
    qtbot.addWidget(dialog)

    dialog._example.click()
    parameters = dialog.parameters()
    assert parameters.frequency_hz == pytest.approx(SCV_REFERENCE_FREQUENCY_HZ)
    assert parameters.horizontal_length_m == pytest.approx(
        BOBTAIL_REFERENCE_HORIZONTAL_LENGTH_M, abs=1e-3
    )
    assert parameters.vertical_height_m == pytest.approx(
        BOBTAIL_REFERENCE_VERTICAL_HEIGHT_M, abs=1e-3
    )

    dialog._form._kind.setCurrentIndex(dialog._form._kind.findData(ScvKind.HALF_SQUARE.value))
    dialog._example.click()
    parameters = dialog.parameters()
    assert parameters.kind is ScvKind.HALF_SQUARE
    assert parameters.horizontal_length_m == pytest.approx(
        HALF_SQUARE_REFERENCE_HORIZONTAL_LENGTH_M, abs=1e-3
    )
    assert parameters.vertical_height_m == pytest.approx(
        HALF_SQUARE_REFERENCE_VERTICAL_HEIGHT_M, abs=1e-3
    )


def test_scv_dialog_scales_the_reference_and_preserves_installation_fields(
    qtbot: QtBot,
) -> None:
    dialog = ScvDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    form = dialog._form
    form._frequency.setValue(14.3)
    form._base_height.setValue(5.0)
    form._feed_offset.setValue(0.75)
    form._radius.setValue(radius_from_m(0.002, UnitSystem.METRIC))
    form._ground.setCurrentIndex(form._ground.findData("perfect"))

    dialog._example.click()

    parameters = dialog.parameters()
    scale = SCV_REFERENCE_FREQUENCY_HZ / 14_300_000.0
    assert parameters.frequency_hz == pytest.approx(14_300_000.0)
    assert parameters.horizontal_length_m == pytest.approx(
        HALF_SQUARE_REFERENCE_HORIZONTAL_LENGTH_M * scale, abs=1e-3
    )
    assert parameters.vertical_height_m == pytest.approx(
        HALF_SQUARE_REFERENCE_VERTICAL_HEIGHT_M * scale, abs=1e-3
    )
    assert parameters.base_height_m == pytest.approx(5.0)
    assert parameters.feed_offset_m == pytest.approx(0.75)
    assert parameters.wire_radius_m == pytest.approx(0.002)
    assert parameters.ground.kind.value == "perfect"


def test_scv_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    original = ScvParameters(
        frequency_hz=7_050_000.0,
        kind=ScvKind.BOBTAIL_CURTAIN,
        horizontal_length_m=38.0,
        vertical_height_m=11.5,
        base_height_m=1.5,
        feed_offset_m=0.75,
        azimuth_deg=35.0,
    )
    dialog = ScvDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters() == original
    assert "38.000" in dialog._form._geometry.text()
