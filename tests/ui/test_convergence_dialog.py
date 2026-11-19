# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Convergence dialog population and CSV export."""

from __future__ import annotations

from pathlib import Path

import pytest
from main_window_support import FakeSolver
from PySide6.QtWidgets import QFileDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.convergence_dialog import ConvergenceDialog
from antennadesk.ui.i18n import Language, Translator


def _dialog(qtbot: QtBot) -> ConvergenceDialog:
    model = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna()
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=FarFieldRequest(enabled=False),
    )
    dialog = ConvergenceDialog(
        Translator(Language.ENGLISH),
        FakeSolver(),
        model,
        spec,
    )
    qtbot.addWidget(dialog)
    return dialog


def test_convergence_dialog_populates_the_density_table(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    qtbot.waitUntil(lambda: dialog._result is not None, timeout=10_000)

    assert dialog._table.rowCount() == 4
    assert dialog._table.item(0, 1).text() == "5"
    assert "Self-consistency" in dialog._status.text()
    assert dialog._export_button.isEnabled() is True
    dialog.accept()


def test_convergence_dialog_exports_csv(
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dialog = _dialog(qtbot)
    qtbot.waitUntil(lambda: dialog._result is not None, timeout=10_000)
    target = tmp_path / "convergence.csv"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(target), ""),
    )

    dialog._export_csv()

    text = target.read_text(encoding="utf-8")
    assert text.startswith("density_lambda,total_segments,resistance_ohm,")
    assert "converged" in text
    dialog.accept()
