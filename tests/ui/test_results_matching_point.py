# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Impedance-table context menu and raw matching point."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.design.matching_design import MatchingNetworkDesign
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
    SourceResult,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.widgets.results_view import ResultsView


def _result(
    *,
    source_impedance_ohm: complex | None = complex(200.0, 20.0),
    post_chain_impedance_ohm: complex = complex(12.5, -3.0),
) -> SimulationResult:
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        feed_transformer_ratio=4.0,
        reference_impedance_ohm=75.0,
    )
    sources: tuple[SourceResult, ...] = ()
    if source_impedance_ohm is not None:
        sources = (
            SourceResult(
                wire_id="radiator",
                offset_m=0.0,
                tag=1,
                segment=11,
                amplitude=1.0,
                phase_deg=0.0,
                voltage_v=complex(1.0, 0.0),
                current_a=complex(0.005, 0.0),
                impedance_ohm=source_impedance_ohm,
                power_w=0.001,
            ),
        )
    frequency = FrequencyResult(
        frequency_hz=7_100_000.0,
        feed_tag=1,
        feed_segment=11,
        impedance_ohm=post_chain_impedance_ohm,
        swr=1.0,
        input_power_w=0.001,
        source_results=sources,
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="fake", version="1.0"),
        frequencies=(frequency,),
    )


def _view(qtbot: QtBot, result: SimulationResult) -> ResultsView:
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.set_result(result)
    return view


def test_impedance_row_uses_the_raw_primary_side_impedance(qtbot: QtBot) -> None:
    view = _view(qtbot, _result())

    point = view._matching_point_for_row(0)

    assert point is not None
    assert point.frequency_hz == pytest.approx(7_100_000.0)
    assert point.load_resistance_ohm == pytest.approx(50.0)
    assert point.load_reactance_ohm == pytest.approx(5.0)
    assert point.source_impedance_ohm == pytest.approx(75.0)


def test_impedance_context_menu_emits_the_raw_matching_point(qtbot: QtBot) -> None:
    view = _view(qtbot, _result())
    menu = view._create_impedance_context_menu(0)
    emitted: list[object] = []
    view.matching_network_requested.connect(emitted.append)

    menu.actions()[0].trigger()

    assert len(emitted) == 1
    point = emitted[0]
    assert isinstance(point, MatchingNetworkDesign)
    assert point.load_resistance_ohm == pytest.approx(50.0)
    assert menu.actions()[0].text() == "Create Project Matching Network..."


def test_impedance_context_menu_disables_the_action_without_raw_impedance(
    qtbot: QtBot,
) -> None:
    view = _view(qtbot, _result(source_impedance_ohm=None))

    menu = view._create_impedance_context_menu(0)

    actions = menu.actions()
    assert actions[0].isEnabled() is False
    assert actions[1].text() == "Raw feed impedance is unavailable for this row."
    assert actions[1].isEnabled() is False
