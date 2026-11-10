# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Band-aware and robust Apply Best must show every analyzed band."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime

import pytest
from helpers import wait_for_condition
from main_window_support import use_parameters
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.application.use_cases.optimize_antenna import OptimizeAntennaResult
from antennadesk.domain.antennas.design import AntennaDesignParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.endfed import EndFedParameters, EndFedPreset
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.design.band_plan import BandPlan, BandSelection
from antennadesk.domain.optimization.engine import (
    BudgetProfile,
    OptimizationStatus,
    budget_for,
)
from antennadesk.domain.optimization.summary import (
    OptimizationMode,
    OptimizationSummary,
)
from antennadesk.domain.simulation.bands import amateur_band_by_id
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.main_window import MainWindow


@dataclass(frozen=True, slots=True)
class BandPlanCase:
    name: str
    parameters: AntennaDesignParameters
    changed: Callable[[AntennaDesignParameters], AntennaDesignParameters]
    changed_field: str
    manual_plan: BandPlan | None = None


def _changed(parameters: AntennaDesignParameters, **changes: float) -> AntennaDesignParameters:
    return replace(parameters, **changes)


BAND_PLAN_CASES = (
    BandPlanCase(
        "ocfd-harmonic",
        OCFDParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.4,
            height_m=10.0,
        ),
        lambda parameters: _changed(parameters, total_length_m=20.9),
        "total_length_m",
    ),
    BandPlanCase(
        "endfed-shortened",
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=12.0,
            transformer_ratio=49.0,
            preset=EndFedPreset.SHORTENED_40_10,
        ),
        lambda parameters: _changed(parameters, length_m=12.5),
        "length_m",
    ),
    BandPlanCase(
        "trap-dipole",
        TrapDipoleParameters(
            frequency_hz=7_100_000.0,
            high_band_frequency_hz=14_100_000.0,
            inner_length_m=10.0,
            outer_length_m=5.0,
            trap_frequency_hz=14_100_000.0,
            trap_inductance_h=10e-6,
            height_m=12.0,
        ),
        lambda parameters: _changed(parameters, inner_length_m=10.1),
        "inner_length_m",
    ),
    BandPlanCase(
        "t2fd-broadband",
        T2FDParameters(
            frequency_hz=1_800_000.0,
            highest_frequency_hz=30_000_000.0,
            length_m=50.8,
            spacing_m=1.69,
        ),
        lambda parameters: _changed(parameters, length_m=51.8),
        "length_m",
    ),
    BandPlanCase(
        "manual-plan-dipole",
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        lambda parameters: _changed(parameters, total_length_m=20.5),
        "total_length_m",
        manual_plan=BandPlan(
            (
                BandSelection(amateur_band_by_id("40m")),
                BandSelection(amateur_band_by_id("20m")),
            )
        ),
    ),
)


def _summary(
    *,
    mode: OptimizationMode,
    plan: BandPlan,
    tolerance: float,
) -> OptimizationSummary:
    edges = tuple(
        dict.fromkeys(
            frequency
            for selection in plan.selections
            for frequency in (
                selection.band.start_hz,
                selection.band.center_hz,
                selection.band.stop_hz,
            )
        )
    )
    return OptimizationSummary(
        mode=mode,
        objective="min_swr",
        status="converged",
        budget_profile="fast",
        evaluations=24,
        seed=0,
        best_values={"optimized": 1.0},
        best_metrics={"swr": 1.2},
        completed_at=datetime(2026, 11, 10, tzinfo=UTC),
        band_edges_hz=edges if mode is not OptimizationMode.SINGLE else (),
        tolerance=tolerance,
    )


def _result(
    parameters: AntennaDesignParameters,
    summary: OptimizationSummary,
) -> OptimizeAntennaResult:
    return OptimizeAntennaResult(
        status=OptimizationStatus.CONVERGED,
        best_parameters=parameters,
        best_values=summary.best_values,
        best_score=1.0,
        best_metrics=summary.best_metrics,
        evaluations=(),
        sensitivity=(),
        budget=budget_for(BudgetProfile.FAST, 3),
        seed=0,
        summary=summary,
    )


def _install_fake_optimizer(
    monkeypatch: pytest.MonkeyPatch,
    optimized: AntennaDesignParameters,
    result: OptimizeAntennaResult,
) -> None:
    class FakeFamilyOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_parameters(self) -> AntennaDesignParameters:
            return optimized

        def selected_result(self) -> OptimizeAntennaResult:
            return result

    monkeypatch.setattr(
        main_window_module,
        "FamilyOptimizationDialog",
        FakeFamilyOptimizationDialog,
    )


def _prepare(
    window: MainWindow,
    case: BandPlanCase,
) -> BandPlan:
    use_parameters(window, case.parameters)
    assert window._project is not None
    assert window._design_id is not None
    if case.manual_plan is not None:
        window._band_plans[window._design_id] = case.manual_plan
    design = window._project.design_by_id(window._design_id)
    return window._current_band_plan(design)


@pytest.mark.parametrize(
    ("case", "mode"),
    [
        (case, mode)
        for case in BAND_PLAN_CASES
        for mode in (OptimizationMode.BAND_AWARE, OptimizationMode.ROBUST)
    ],
    ids=lambda value: value.name if isinstance(value, BandPlanCase) else value.value,
)
def test_band_aware_apply_best_analyzes_every_selected_band(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    case: BandPlanCase,
    mode: OptimizationMode,
) -> None:
    plan = _prepare(window, case)
    optimized = case.changed(case.parameters)
    tolerance = 0.05 if mode is OptimizationMode.ROBUST else 0.0
    summary = _summary(mode=mode, plan=plan, tolerance=tolerance)
    _install_fake_optimizer(monkeypatch, optimized, _result(optimized, summary))
    errors: list[str] = []
    monkeypatch.setattr(window, "_show_error", errors.append)
    monkeypatch.setattr(window, "_maybe_save_changes", lambda: True)

    window.optimize_current_design()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )

    assert errors == []
    assert window._project is not None
    assert window._design_id is not None
    design = window._project.designs[0]
    assert type(design.parameters) is type(optimized)
    assert getattr(design.parameters, case.changed_field) == pytest.approx(
        getattr(optimized, case.changed_field)
    )
    assert design.optimization_summary == summary
    assert design.optimization_summary is not None
    assert design.optimization_summary.tolerance == tolerance
    analysis = window._band_analysis_results.get(window._design_id)
    assert analysis is not None
    assert tuple(band.band.name for band in analysis.bands) == plan.band_ids
    assert window._results._bands_table.rowCount() == len(plan.band_ids)
    window._dirty = False


def test_single_mode_apply_best_keeps_the_single_band_simulation(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = BAND_PLAN_CASES[0]
    plan = _prepare(window, case)
    optimized = case.changed(case.parameters)
    summary = _summary(mode=OptimizationMode.SINGLE, plan=plan, tolerance=0.0)
    _install_fake_optimizer(monkeypatch, optimized, _result(optimized, summary))
    errors: list[str] = []
    monkeypatch.setattr(window, "_show_error", errors.append)
    monkeypatch.setattr(window, "_maybe_save_changes", lambda: True)

    window.optimize_current_design()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )

    assert errors == []
    assert window._project is not None
    assert window._design_id is not None
    design = window._project.designs[0]
    assert type(design.parameters) is type(optimized)
    assert getattr(design.parameters, case.changed_field) == pytest.approx(
        getattr(optimized, case.changed_field)
    )
    assert design.optimization_summary == summary
    assert window._band_analysis_results.get(window._design_id) is None
    assert window._results._table.rowCount() == 1
    window._dirty = False
