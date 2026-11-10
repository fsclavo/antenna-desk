# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Multi-seed verification for the family optimizer."""

from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import pytest

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.application.use_cases.optimize_antenna import (
    OptimizeAntenna,
    OptimizeAntennaCommand,
    _seed_parameter_spread,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.optimization.descriptor import FamilyOptimizationObjective
from antennadesk.domain.optimization.engine import (
    BudgetProfile,
    CandidateEvaluation,
    OptimizationBudget,
    OptimizationStatus,
    OptimizerRunResult,
    budget_for,
)
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.optimization.variables import OptimizationVariable, VariableKind
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.spec import SimulationSpec


class _NoopSolver:
    """The fake engine replaces the solver, so this must never run."""

    def run(self, *_args: object, **_kwargs: object) -> object:
        raise AssertionError("the solver should not run")


def _command(**kwargs: object) -> OptimizeAntennaCommand:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    return OptimizeAntennaCommand(
        descriptor=availability.descriptor,
        base_spec=SimulationSpec(
            frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
        ),
        objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
        budget=budget_for(BudgetProfile.FAST, 3),
        budget_profile=BudgetProfile.FAST,
        **kwargs,  # type: ignore[arg-type]
    )


def _run(
    seed: int,
    score: float | None,
    length_m: float,
    *,
    status: OptimizationStatus = OptimizationStatus.CONVERGED,
) -> OptimizerRunResult:
    values = {"total_length_m": length_m}
    evaluations = (
        CandidateEvaluation(
            index=1,
            values=values,
            score=score,
            feasible=score is not None,
            metrics={"swr": 1.0},
        ),
    )
    return OptimizerRunResult(
        status=status,
        best_values=values if score is not None else None,
        best_score=score,
        best_metrics={"swr": 1.0, "target_error_ohm": score or 0.0},
        evaluations=evaluations,
        seed=seed,
    )


def _install_engine(
    monkeypatch: pytest.MonkeyPatch,
    runs: dict[int, OptimizerRunResult],
    *,
    calls: list[int] | None = None,
) -> None:
    def fake_optimize_design(
        variables: object,
        initial_values: object,
        evaluate: object,
        *,
        budget: OptimizationBudget,
        seed: int = 0,
        start_points: object = (),
        cancel_check: object = None,
        progress: object = None,
        batch_evaluate: object = None,
    ) -> OptimizerRunResult:
        del variables, initial_values, evaluate, budget, start_points
        del cancel_check, progress, batch_evaluate
        if calls is not None:
            calls.append(seed)
        return runs[seed]

    monkeypatch.setattr(
        "antennadesk.application.use_cases.optimize_antenna.optimize_design",
        fake_optimize_design,
    )


def test_converged_seeds_choose_the_best_score(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    _install_engine(
        monkeypatch,
        {
            10: _run(10, 1.02, 20.02),
            11: _run(11, 1.00, 20.00),
            12: _run(12, 1.01, 20.01),
        },
        calls=calls,
    )

    result = OptimizeAntenna(_NoopSolver()).execute(_command(seed=10, seed_runs=3))

    assert calls == [10, 11, 12]
    assert result.seed == 11
    assert result.best_parameters is not None
    assert result.best_parameters.total_length_m == pytest.approx(20.0)
    assert result.best_metrics["seed_requested"] == 3.0
    assert result.best_metrics["seed_base"] == 10.0
    assert result.best_metrics["seed_count"] == 3.0
    assert result.best_metrics["seed_scored_count"] == 3.0
    assert result.best_metrics["seed_converged"] == 1.0
    assert result.best_metrics["seed_score_spread"] == pytest.approx(0.02)
    assert result.best_metrics["seed_parameter_spread"] < 0.02
    assert result.summary is not None
    assert result.summary.seed == 11
    assert result.summary.best_metrics["seed_converged"] == 1.0
    assert all(
        recommendation.key != "optimize.recommend.seed_divergence"
        for recommendation in result.summary.recommendations
    )


def test_divergent_scores_warn_and_keep_the_best_design(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_engine(
        monkeypatch,
        {
            4: _run(4, 1.0, 20.0),
            5: _run(5, 1.4, 20.0),
            6: _run(6, 1.2, 20.0),
        },
    )

    result = OptimizeAntenna(_NoopSolver()).execute(_command(seed=4, seed_runs=3))

    assert result.seed == 4
    assert result.best_metrics["seed_converged"] == 0.0
    assert result.best_metrics["seed_score_spread"] == pytest.approx(0.4)
    assert result.summary is not None
    assert any(
        recommendation.key == "optimize.recommend.seed_divergence"
        for recommendation in result.summary.recommendations
    )


def test_equal_scores_with_different_geometry_do_not_count_as_converged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_engine(
        monkeypatch,
        {
            0: _run(0, 1.0, 18.0),
            1: _run(1, 1.0, 21.0),
            2: _run(2, 1.0, 22.0),
        },
    )

    result = OptimizeAntenna(_NoopSolver()).execute(_command(seed=0, seed_runs=3))

    assert result.best_metrics["seed_score_spread"] == pytest.approx(0.0)
    assert result.best_metrics["seed_parameter_spread"] > 0.02
    assert result.best_metrics["seed_converged"] == 0.0


def test_integer_variables_must_match_exactly_for_convergence() -> None:
    variable = OptimizationVariable(
        name="radial_count",
        label_key="field.radial_count",
        group="optimize.group.geometry",
        minimum=2.0,
        maximum=8.0,
        kind=VariableKind.INTEGER,
        unit="count",
    )
    runs = [
        SimpleNamespace(best_values={"radial_count": 4.0}),
        SimpleNamespace(best_values={"radial_count": 5.0}),
    ]

    assert _seed_parameter_spread(runs, (variable,)) == 1.0


def test_single_seed_run_keeps_the_existing_result_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_engine(monkeypatch, {3: _run(3, 1.0, 20.0)})

    result = OptimizeAntenna(_NoopSolver()).execute(_command(seed=3))

    assert result.seed == 3
    assert "seed_count" not in result.best_metrics
    assert "seed_converged" not in result.best_metrics
    assert result.summary is not None
    assert result.summary.seed == 3


def test_cancelled_seed_stops_the_remaining_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    _install_engine(
        monkeypatch,
        {
            0: _run(0, 1.0, 20.0),
            1: _run(1, 1.1, 20.5),
            2: _run(2, None, 20.0, status=OptimizationStatus.CANCELLED),
            3: _run(3, 1.0, 20.0),
        },
        calls=calls,
    )

    result = OptimizeAntenna(_NoopSolver()).execute(_command(seed=0, seed_runs=4))

    assert calls == [0, 1, 2]
    assert result.status is OptimizationStatus.CANCELLED
    assert result.seed == 0
    assert result.best_metrics["seed_requested"] == 4.0
    assert result.best_metrics["seed_count"] == 3.0
    assert result.best_metrics["seed_scored_count"] == 2.0
    assert result.best_metrics["seed_score_spread"] == pytest.approx(0.1)
    assert result.best_metrics["seed_parameter_spread"] > 0.02
    assert result.best_metrics["seed_converged"] == 0.0


def test_pre_cancelled_token_skips_every_seed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    _install_engine(monkeypatch, {0: _run(0, 1.0, 20.0)}, calls=calls)
    token = EventCancelToken()
    token.cancel()

    result = OptimizeAntenna(_NoopSolver()).execute(
        _command(seed=0, seed_runs=3, cancel_token=token)
    )

    assert calls == []
    assert result.status is OptimizationStatus.CANCELLED
    assert result.best_metrics["seed_count"] == 0.0
    assert result.summary is not None
    assert result.summary.status == OptimizationStatus.CANCELLED.value


def test_progress_is_cumulative_across_seeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_optimize_design(
        variables: object,
        initial_values: object,
        evaluate: object,
        *,
        budget: OptimizationBudget,
        seed: int = 0,
        start_points: object = (),
        cancel_check: object = None,
        progress: object = None,
        batch_evaluate: object = None,
    ) -> OptimizerRunResult:
        del variables, initial_values, evaluate, budget, start_points
        del cancel_check, batch_evaluate
        callback = progress
        assert callable(callback)
        for count in (1, 2):
            callback(count, 2.0 - (seed - 10) * 0.1)
        run = _run(seed, 2.0 - (seed - 10) * 0.1, 20.0)
        first = run.evaluations[0]
        second = replace(first, index=2)
        return replace(run, evaluations=(first, second))

    monkeypatch.setattr(
        "antennadesk.application.use_cases.optimize_antenna.optimize_design",
        fake_optimize_design,
    )
    seen: list[tuple[int, float | None]] = []

    OptimizeAntenna(_NoopSolver()).execute(
        _command(seed=10, seed_runs=2, progress=lambda count, score: seen.append((count, score)))
    )

    assert [count for count, _score in seen] == [1, 2, 3, 4]
    assert seen[-1][1] == pytest.approx(1.9)


@pytest.mark.parametrize("seed_runs", [0, 5])
def test_seed_runs_are_bounded(seed_runs: int) -> None:
    with pytest.raises(ValueError, match="seed_runs"):
        replace(_command(), seed_runs=seed_runs)


def test_negative_base_seed_is_rejected() -> None:
    with pytest.raises(ValueError, match="seed"):
        replace(_command(), seed=-1)
