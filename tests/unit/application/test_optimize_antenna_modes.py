# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace

import pytest

from antennadesk.application.ports.antenna_solver import ProgressCallback
from antennadesk.application.ports.cancellation import CancelToken
from antennadesk.application.use_cases.optimize_antenna import (
    OptimizeAntenna,
    OptimizeAntennaCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.descriptor import FamilyOptimizationObjective
from antennadesk.domain.optimization.engine import (
    BudgetProfile,
    OptimizationStatus,
    budget_for,
)
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.optimization.summary import OptimizationMode
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.pattern_resolution import far_field_request

BAND_EDGES = (7_000_000.0, 7_100_000.0, 7_200_000.0)


class FrequencySolver:
    """A solver whose impedance depends on wire length and frequency."""

    def __init__(self) -> None:
        self.calls: list[float] = []

    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="fake",
            supports_frequency_sweep=True,
            supports_currents=True,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )

    def validate(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
    ) -> tuple[Diagnostic, ...]:
        del model, spec
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="fake", version="1.0")

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult:
        del progress_callback, cancel_token
        frequency_hz = spec.frequency_plan.start_hz
        self.calls.append(frequency_hz)
        length_m = model.wires[0].length_m
        resistance = 50.0 + (length_m - 20.0) * 10.0
        reactance = (frequency_hz - 7_100_000.0) / 1_000_000.0 * 5.0
        impedance = complex(resistance, reactance)
        reflection = abs((impedance - 50.0) / (impedance + 50.0))
        swr = (1.0 + reflection) / (1.0 - reflection)
        point = FrequencyResult(
            frequency_hz=frequency_hz,
            feed_tag=1,
            feed_segment=1,
            impedance_ohm=impedance,
            swr=swr,
            input_power_w=0.001,
        )
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(point,),
            duration_s=0.01,
        )


def _command(
    mode: OptimizationMode,
    *,
    tolerance: float = 0.0,
    objective: FamilyOptimizationObjective = FamilyOptimizationObjective.TARGET_IMPEDANCE,
) -> OptimizeAntennaCommand:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor
    return OptimizeAntennaCommand(
        descriptor=descriptor,
        base_spec=SimulationSpec(
            frequency_plan=FrequencyPlan.single(7_100_000.0),
            far_field=far_field_request(5.0, parameters.ground),
        ),
        objective=objective,
        budget=budget_for(BudgetProfile.FAST, len(descriptor.variables)),
        mode=mode,
        band_edges_hz=BAND_EDGES,
        robust_tolerance=tolerance,
        budget_profile=BudgetProfile.FAST,
    )


def test_band_aware_mode_evaluates_every_edge() -> None:
    solver = FrequencySolver()

    result = OptimizeAntenna(solver).execute(_command(OptimizationMode.BAND_AWARE))

    assert result.best_parameters is not None
    assert len(solver.calls) == 3 * len(result.evaluations)
    assert set(solver.calls) == set(BAND_EDGES)
    assert result.best_metrics["multi_point_count"] == 3.0
    assert result.best_metrics["swr_spread"] > 0.0
    assert result.pareto
    assert all(
        "swr" in candidate.metrics and "target_error_ohm" in candidate.metrics
        for candidate in result.pareto
    )
    assert result.summary is not None
    assert result.summary.mode is OptimizationMode.BAND_AWARE
    assert result.summary.band_edges_hz == BAND_EDGES
    assert result.summary.constraints == ()


def test_robust_mode_evaluates_tolerance_scenarios() -> None:
    solver = FrequencySolver()

    result = OptimizeAntenna(solver).execute(_command(OptimizationMode.ROBUST, tolerance=0.02))

    assert result.best_parameters is not None
    assert len(solver.calls) == 3 * 3 * len(result.evaluations)
    assert result.summary is not None
    assert result.summary.mode is OptimizationMode.ROBUST
    assert result.summary.tolerance == pytest.approx(0.02)
    assert result.best_metrics["optimization_score_spread"] >= 0.0


def test_quality_modes_reject_the_bandwidth_objective() -> None:
    with pytest.raises(ValueError, match="single-frequency"):
        _command(
            OptimizationMode.BAND_AWARE,
            objective=FamilyOptimizationObjective.MAX_BANDWIDTH,
        )


def test_band_aware_mode_requires_two_distinct_edges() -> None:
    command = _command(OptimizationMode.BAND_AWARE)
    with pytest.raises(ValueError, match="two distinct edges"):
        replace(command, band_edges_hz=(7_100_000.0,))


def test_robust_mode_requires_a_tolerance() -> None:
    with pytest.raises(ValueError, match="positive tolerance"):
        _command(OptimizationMode.ROBUST, tolerance=0.0)


def test_single_mode_keeps_the_tolerance_out_of_the_command() -> None:
    with pytest.raises(ValueError, match="only used in robust mode"):
        _command(OptimizationMode.SINGLE, tolerance=0.01)


def test_turning_radius_limit_can_make_all_candidates_infeasible() -> None:
    command = replace(
        _command(OptimizationMode.SINGLE),
        max_turning_radius_m=1.0,
    )

    result = OptimizeAntenna(FrequencySolver()).execute(command)

    assert result.status is OptimizationStatus.NO_FEASIBLE
    assert result.best_parameters is None
    assert result.summary is not None
    assert "turning_radius_m<=1" in result.summary.constraints
    assert any(
        recommendation.key == "optimize.recommend.no_feasible"
        for recommendation in result.summary.recommendations
    )


def test_turning_radius_limit_reports_the_metric_when_feasible() -> None:
    command = replace(
        _command(OptimizationMode.SINGLE),
        max_turning_radius_m=20.0,
    )

    result = OptimizeAntenna(FrequencySolver()).execute(command)

    assert result.best_parameters is not None
    assert result.best_metrics["turning_radius_m"] == pytest.approx(10.0, abs=0.5)


def test_space_limits_must_be_positive() -> None:
    with pytest.raises(ValueError, match="max_turning_radius_m"):
        replace(_command(OptimizationMode.SINGLE), max_turning_radius_m=0.0)


def test_summary_records_the_constraint_and_recommendation() -> None:
    from antennadesk.domain.optimization.constraints import OptimizationMetric, SoftConstraint

    command = replace(
        _command(OptimizationMode.BAND_AWARE),
        soft_constraints=(SoftConstraint(metric=OptimizationMetric.SWR, maximum=1.01),),
    )

    result = OptimizeAntenna(FrequencySolver()).execute(command)

    assert result.summary is not None
    assert result.summary.constraints == ("swr<=1.01",)
    assert any(
        recommendation.key == "optimize.recommend.high_swr_constraint"
        for recommendation in result.summary.recommendations
    )
