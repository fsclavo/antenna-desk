# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Matching-network design-target persistence and preload."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.matching_network import LNetwork
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
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.main_window import MainWindow


def _target() -> MatchingNetworkDesign:
    return MatchingNetworkDesign(
        frequency_hz=7_100_000.0,
        load_resistance_ohm=120.0,
        load_reactance_ohm=-35.0,
        source_impedance_ohm=50.0,
        origin="manual",
    )


def _network() -> LNetwork:
    return LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)


def test_current_matching_point_uses_the_raw_feed_impedance(window: MainWindow) -> None:
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        feed_transformer_ratio=4.0,
        reference_impedance_ohm=50.0,
    )
    frequency = FrequencyResult(
        frequency_hz=7_100_000.0,
        feed_tag=1,
        feed_segment=11,
        impedance_ohm=complex(50.0, 0.0),
        swr=1.0,
        input_power_w=0.001,
        source_results=(
            SourceResult(
                wire_id="radiator",
                offset_m=0.0,
                tag=1,
                segment=11,
                amplitude=1.0,
                phase_deg=0.0,
                voltage_v=complex(1.0, 0.0),
                current_a=complex(0.005, 0.0),
                impedance_ohm=complex(200.0, 20.0),
                power_w=0.001,
            ),
        ),
    )
    window._last_result = SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="fake", version="1.0"),
        frequencies=(frequency,),
    )

    point = window._current_matching_network_point()

    assert point is not None
    assert point.frequency_hz == pytest.approx(7_100_000.0)
    assert point.load_resistance_ohm == pytest.approx(50.0)
    assert point.load_reactance_ohm == pytest.approx(5.0)
    assert point.source_impedance_ohm == pytest.approx(50.0)
    assert point.origin == "simulation"
    window._last_result = None


def test_current_matching_point_is_unavailable_without_source_results(
    window: MainWindow,
) -> None:
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))
    frequency = FrequencyResult(
        frequency_hz=7_100_000.0,
        feed_tag=1,
        feed_segment=11,
        impedance_ohm=complex(50.0, 0.0),
        swr=1.0,
        input_power_w=0.001,
    )
    window._last_result = SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="fake", version="1.0"),
        frequencies=(frequency,),
    )

    assert window._current_matching_network_point() is None
    window._last_result = None


def test_configure_matching_network_persists_and_reopens_the_design_target(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            calls.append(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_network(self) -> LNetwork:
            return _network()

        def result_design(self) -> MatchingNetworkDesign:
            return _target()

    monkeypatch.setattr(main_window_module, "MatchingNetworkDialog", FakeDialog)

    window.configure_matching_network()

    assert window._matching_network_design == _target()
    assert window._project is not None
    assert window._project.matching_network_design == _target()
    assert window._project.matching_network == _network()

    window.configure_matching_network()

    assert calls[-1]["design"] == _target()

    window._undo_stack.undo()
    assert window._matching_network_design is None
    assert window._project.matching_network_design is None

    window._undo_stack.redo()
    assert window._matching_network_design == _target()
    assert window._project.matching_network_design == _target()
    window._dirty = False


def test_disabling_the_network_clears_the_design_target(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_network(self) -> None:
            return None

        def result_design(self) -> MatchingNetworkDesign:
            return _target()

    monkeypatch.setattr(main_window_module, "MatchingNetworkDialog", FakeDialog)

    window.configure_matching_network()

    assert window._matching_network is None
    assert window._matching_network_design is None
    assert window._project is not None
    assert window._project.matching_network_design is None
    window._dirty = False


def test_matching_design_preloads_from_a_loaded_project(
    window: MainWindow,
    qtbot: QtBot,
) -> None:
    from antennadesk.ui.dialogs.matching_network_dialog import MatchingNetworkDialog

    assert window._project is not None
    window._project = window._project.with_matching_network(
        _network(),
        updated_at=window._project.updated_at,
    ).with_matching_network_design(
        _target(),
        updated_at=window._project.updated_at,
    )
    window._set_project(
        window._project,
        window._design_id,
        path=None,
        dirty=False,
    )
    dialog = MatchingNetworkDialog(
        window._translator,
        window._matching_network,
        design=window._matching_network_design,
    )
    qtbot.addWidget(dialog)

    assert dialog._load_r.value() == pytest.approx(120.0)
    assert dialog._load_x.value() == pytest.approx(-35.0)
    window._dirty = False
