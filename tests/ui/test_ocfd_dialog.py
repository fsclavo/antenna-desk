# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.ui.dialogs.ocfd_dialog import OCFDDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_ocfd_dialog_builds_an_offset_feed(qtbot: QtBot) -> None:
    dialog = OCFDDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert parameters.total_length_m == pytest.approx(20.0)
    assert parameters.feed_offset_m == pytest.approx(20.0 / 3.0, abs=0.01)
    assert parameters.feed_ratio == pytest.approx(1.0 / 3.0, abs=0.001)
    assert dialog._ground.currentText() == "Finite ground"


def test_ocfd_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    original = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        feed_ratio=0.3,
        height_m=10.0,
        azimuth_deg=30.0,
    )
    dialog = OCFDDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    restored = dialog.parameters()
    assert restored.feed_ratio == pytest.approx(0.3)
    assert restored.azimuth_deg == pytest.approx(30.0)
