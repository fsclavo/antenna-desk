# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpinBox
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.design.band_plan import default_band_plan
from antennadesk.ui.dialogs.band_analysis_dialog import PRESET_CURRENT, BandAnalysisDialog
from antennadesk.ui.i18n import Language, Translator


def test_band_dialog_preselects_the_family_default(qtbot: QtBot) -> None:
    default = default_band_plan(OCFDParameters(frequency_hz=7_100_000.0, total_length_m=20.4))
    dialog = BandAnalysisDialog(
        Translator(Language.ENGLISH),
        default,
        current_frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(dialog)

    plan = dialog.plan()

    assert plan.band_ids == ("40m", "20m", "10m")
    assert all(selection.points == 15 for selection in plan.selections)


def test_band_dialog_current_preset_selects_one_band(qtbot: QtBot) -> None:
    default = default_band_plan(OCFDParameters(frequency_hz=7_100_000.0, total_length_m=20.4))
    dialog = BandAnalysisDialog(
        Translator(Language.ENGLISH),
        default,
        current_frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(dialog)

    index = dialog._preset.findData(PRESET_CURRENT)
    dialog._preset.setCurrentIndex(index)

    assert dialog.plan().band_ids == ("40m",)


def test_band_dialog_optionally_changes_points_per_band(qtbot: QtBot) -> None:
    default = default_band_plan(OCFDParameters(frequency_hz=7_100_000.0, total_length_m=20.4))
    dialog = BandAnalysisDialog(
        Translator(Language.ENGLISH),
        default,
        current_frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(dialog)

    for row in range(dialog._table.rowCount()):
        item = dialog._table.item(row, 0)
        if item is not None and item.data(Qt.ItemDataRole.UserRole) == "20m":
            spin = dialog._table.cellWidget(row, 2)
            assert isinstance(spin, QSpinBox)
            spin.setValue(31)

    band = dialog.plan().result if False else None
    del band
    selection = next(item for item in dialog.plan().selections if item.band_id == "20m")
    assert selection.points == 31
