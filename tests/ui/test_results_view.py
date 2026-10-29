# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from datetime import UTC, datetime

from pytestqt.qtbot import QtBot

from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    CurrentSample,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.widgets.results_view import ResultsView


def _make_result() -> SimulationResult:
    spec = SimulationSpec(frequency_plan=FrequencyPlan.sweep(7_000_000.0, 7_200_000.0, 3))
    currents = (
        CurrentSample(1, 1, -1.0, 0.0, 8.0, 1.0, complex(0.1, 0.0), 0.1, 0.0),
        CurrentSample(2, 1, 0.0, 0.0, 8.0, 1.0, complex(0.2, 0.0), 0.2, 0.0),
        CurrentSample(3, 1, 1.0, 0.0, 8.0, 1.0, complex(0.1, 0.0), 0.1, 0.0),
    )
    frequencies = (
        FrequencyResult(7_000_000.0, 1, 2, complex(70.0, -10.0), 2.5, 0.001, currents=currents),
        FrequencyResult(7_100_000.0, 1, 2, complex(75.0, 0.0), 1.5, 0.001, currents=currents),
        FrequencyResult(7_200_000.0, 1, 2, complex(80.0, 10.0), 2.0, 0.001, currents=currents),
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=frequencies,
        duration_s=0.1,
        started_at=datetime(2026, 10, 29, tzinfo=UTC),
        finished_at=datetime(2026, 10, 29, tzinfo=UTC),
    )


def test_results_view_shows_currents_and_resonance(qtbot: QtBot) -> None:
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_result(_make_result())

    assert view._tabs.count() == 5
    assert view._table.rowCount() == 3
    assert view._currents_frequency.count() == 3
    assert len(view._currents_plot.listDataItems()) >= 1
    assert "Resonance" in view._resonance_label.text()


def test_results_view_localizes_known_diagnostics(qtbot: QtBot) -> None:
    from dataclasses import replace

    from antennadesk.domain.common.validation import Diagnostic, Severity

    result = replace(
        _make_result(),
        diagnostics=(
            Diagnostic(
                code="solver.timeout",
                severity=Severity.ERROR,
                message="nec2c timed out after 30 s",
            ),
        ),
    )
    view = ResultsView(Translator(Language.SPANISH))
    qtbot.addWidget(view)

    view.set_result(result)

    message_item = view._diagnostics.item(0, 2)
    assert message_item.text() == "El solver agotó el tiempo de espera."
    assert message_item.toolTip() == "nec2c timed out after 30 s"
