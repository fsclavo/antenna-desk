# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tuner matchability dialog tests."""

from __future__ import annotations

from datetime import UTC, datetime

from pytestqt.qtbot import QtBot

from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.tuner_match_dialog import TunerMatchDialog
from antennadesk.ui.i18n import Language, Translator


def _result() -> SimulationResult:
    frequencies = (
        FrequencyResult(7_000_000.0, 1, 1, complex(100.0, 0.0), 2.0, 0.01),
        FrequencyResult(14_000_000.0, 1, 1, complex(50.0, 0.0), 1.0, 0.01),
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=SimulationSpec(frequency_plan=FrequencyPlan.sweep(7_000_000.0, 14_000_000.0, 2)),
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=frequencies,
        duration_s=0.1,
        started_at=datetime(2026, 11, 19, tzinfo=UTC),
        finished_at=datetime(2026, 11, 19, tzinfo=UTC),
    )


def test_tuner_dialog_lists_simulated_points(qtbot: QtBot) -> None:
    dialog = TunerMatchDialog(Translator(Language.ENGLISH), _result())
    qtbot.addWidget(dialog)

    assert dialog._table.rowCount() == 2
    assert dialog._table.item(0, 0).text() == "7.000000"
    assert dialog._table.item(1, 4).text() == "Matched"


def test_tuner_dialog_recomputes_a_narrow_range(qtbot: QtBot) -> None:
    dialog = TunerMatchDialog(Translator(Language.ENGLISH), _result())
    qtbot.addWidget(dialog)

    dialog._c_min.setValue(1.0)
    dialog._c_max.setValue(2.0)
    dialog._recompute()

    assert dialog._table.item(0, 4).text() == "Out of range"
    assert dialog._table.item(0, 7).text() == "C above range"


def test_tuner_dialog_retranslates(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    dialog = TunerMatchDialog(translator, _result())
    qtbot.addWidget(dialog)

    translator.set_language(Language.SPANISH)
    dialog._retranslate()

    assert dialog._table.horizontalHeaderItem(4).text() == "Estado"
    assert dialog._table.horizontalHeaderItem(5).text() == "ROE"
