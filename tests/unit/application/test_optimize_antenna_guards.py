# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guards and scoring branches for the family optimizer use case."""

from __future__ import annotations

import math
from dataclasses import replace
from types import SimpleNamespace

import pytest

from antennadesk.application.use_cases.optimize_antenna import (
    OptimizeAntenna,
    OptimizeAntennaCommand,
    _max_swr_constraint,
    _metrics,
    _required,
    _score,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.common import units
from antennadesk.domain.optimization.constraints import OptimizationMetric, SoftConstraint
from antennadesk.domain.optimization.descriptor import (
    AntennaOptimizerDescriptor,
    FamilyOptimizationObjective,
    OptimizationWeights,
)
from antennadesk.domain.optimization.engine import (
    BudgetProfile,
    OptimizationStatus,
    budget_for,
)
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.optimization.variables import OptimizationVariable
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    PowerBudget,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_model,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class _NoopSolver:
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="fake",
            supports_frequency_sweep=True,
            supports_currents=False,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )

    def validate(self, model: object, spec: object) -> tuple[()]:
        del model, spec
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="fake", version="1.0")

    def run(self, model: object, spec: object, **kwargs: object) -> SimulationResult:
        del model, spec, kwargs
        raise AssertionError("the solver should not run")


def _command() -> OptimizeAntennaCommand:
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
            far_field=FarFieldRequest(enabled=False),
        ),
        objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
        budget=budget_for(BudgetProfile.FAST, len(descriptor.variables)),
    )


def test_optimizer_blocks_a_thin_wire_model_quality_candidate() -> None:
    parameters = DipoleParameters(
        frequency_hz=2_400_000_000.0,
        total_length_m=1.0,
        height_m=1.0,
        wire_radius_m=0.005,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor
    command = OptimizeAntennaCommand(
        descriptor=descriptor,
        base_spec=SimulationSpec(
            frequency_plan=FrequencyPlan.single(2_400_000_000.0),
            far_field=FarFieldRequest(enabled=False),
        ),
        objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
        budget=budget_for(BudgetProfile.FAST, len(descriptor.variables)),
    )

    result = OptimizeAntenna(_NoopSolver()).execute(command)

    assert result.status is OptimizationStatus.NO_FEASIBLE
    assert result.best_parameters is None
    assert result.evaluations
    assert all(not evaluation.feasible for evaluation in result.evaluations)
    assert any(
        "optimize.constraint.model_quality" in (evaluation.error or "")
        for evaluation in result.evaluations
    )


def test_optimize_returns_error_for_an_unlocked_out_of_bounds_variable() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    descriptor = AntennaOptimizerDescriptor(
        key="test_unlocked_bounds",
        variables=(
            OptimizationVariable(
                "width_m",
                "field.length",
                "optimize.group.geometry",
                0.0,
                1.0,
            ),
            OptimizationVariable(
                "height_m",
                "field.height",
                "optimize.group.geometry",
                0.1,
                0.2,
            ),
        ),
        initial_values={"width_m": 0.5, "height_m": 0.05},
        build_parameters=lambda values: parameters,
        validate=lambda values: (),
        objectives=frozenset({FamilyOptimizationObjective.TARGET_IMPEDANCE}),
    )
    command = OptimizeAntennaCommand(
        descriptor=descriptor,
        base_spec=SimulationSpec(
            frequency_plan=FrequencyPlan.single(7_100_000.0),
            far_field=FarFieldRequest(enabled=False),
        ),
        objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
        budget=budget_for(BudgetProfile.FAST, 2),
        locked_variables=frozenset(),
    )

    result = OptimizeAntenna(_NoopSolver()).execute(command)

    assert result.status is OptimizationStatus.ERROR
    assert "height_m" in result.message
    assert result.evaluations == ()
    assert result.best_parameters is None


def _scoring_command(
    objective: FamilyOptimizationObjective,
    *,
    weights: OptimizationWeights | None = None,
    constraints: tuple[SoftConstraint, ...] = (),
) -> SimpleNamespace:
    return SimpleNamespace(
        objective=objective,
        weights=weights or OptimizationWeights(),
        soft_constraints=constraints,
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("target_resistance_ohm", 0.0, "target_resistance"),
        ("target_reactance_ohm", math.inf, "target_reactance"),
        ("band_edges_hz", (0.0,), "band edges"),
        ("robust_tolerance", -0.1, "robust_tolerance"),
        ("robust_tolerance", 1.0, "robust_tolerance"),
    ],
)
def test_command_rejects_invalid_numeric_guards(
    field: str,
    value: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        replace(_command(), **{field: value})


def test_execute_requires_at_least_one_unlocked_variable() -> None:
    command = _command()
    locked = frozenset(variable.name for variable in command.descriptor.variables)

    with pytest.raises(ValueError, match="unlocked"):
        OptimizeAntenna(_NoopSolver()).execute(replace(command, locked_variables=locked))


def test_bandwidth_objective_requires_a_sweep() -> None:
    command = replace(
        _command(),
        objective=FamilyOptimizationObjective.MAX_BANDWIDTH,
    )

    with pytest.raises(ValueError, match="frequency sweep"):
        OptimizeAntenna(_NoopSolver()).execute(command)


@pytest.mark.parametrize(
    ("objective", "metrics"),
    [
        (FamilyOptimizationObjective.TARGET_IMPEDANCE, {"target_error_ohm": 2.0}),
        (FamilyOptimizationObjective.MIN_SWR, {"swr": 1.5}),
        (FamilyOptimizationObjective.MIN_SWR_OPERATING, {"operating_swr_rms": 1.5}),
        (FamilyOptimizationObjective.MAX_GAIN, {"max_gain_db": 8.0}),
        (FamilyOptimizationObjective.MAX_FRONT_TO_BACK, {"front_to_back_db": 20.0}),
        (FamilyOptimizationObjective.MAX_EFFICIENCY, {"efficiency_percent": 80.0}),
        (FamilyOptimizationObjective.MAX_BANDWIDTH, {"bandwidth_hz": 100_000.0}),
    ],
)
def test_single_objective_scores_use_the_requested_metric(
    objective: FamilyOptimizationObjective,
    metrics: dict[str, float],
) -> None:
    score = _score(_scoring_command(objective), metrics)  # type: ignore[arg-type]

    assert math.isfinite(score)


def test_operating_objective_uses_the_rms_metric_not_the_worst_target() -> None:
    command = _scoring_command(FamilyOptimizationObjective.MIN_SWR_OPERATING)

    score = _score(command, {"operating_swr_rms": 2.5, "swr": 4.0})  # type: ignore[arg-type]

    assert score == pytest.approx(2.5)


def test_multi_objective_score_combines_every_weight() -> None:
    command = _scoring_command(
        FamilyOptimizationObjective.MULTI_OBJECTIVE,
        weights=OptimizationWeights(
            gain=1.0,
            front_to_back=1.0,
            swr=1.0,
            efficiency=1.0,
        ),
    )
    metrics = {
        "max_gain_db": 9.0,
        "front_to_back_db": 20.0,
        "efficiency_percent": 80.0,
        "swr": 2.0,
    }

    score = _score(command, metrics)  # type: ignore[arg-type]

    assert score == pytest.approx(-(3.0 + 2.0 - 1.0 + 0.8))


def test_soft_constraints_add_a_penalty() -> None:
    constraint = SoftConstraint(metric=OptimizationMetric.SWR, maximum=1.0)
    command = _scoring_command(
        FamilyOptimizationObjective.MIN_SWR,
        constraints=(constraint,),
    )

    plain = _score(_scoring_command(FamilyOptimizationObjective.MIN_SWR), {"swr": 2.0})
    penalized = _score(command, {"swr": 2.0})  # type: ignore[arg-type]

    assert penalized > plain


def test_max_swr_constraint_reads_the_first_swr_limit() -> None:
    constraint = SoftConstraint(metric=OptimizationMetric.SWR, maximum=1.4)

    assert _max_swr_constraint((constraint,)) == 1.4
    assert _max_swr_constraint(()) is None


def test_required_metric_rejects_a_missing_value() -> None:
    with pytest.raises(ValueError, match="'swr'"):
        _required({}, "swr")


def _point(frequency_hz: float, swr: float) -> FrequencyResult:
    return FrequencyResult(
        frequency_hz=frequency_hz,
        feed_tag=1,
        feed_segment=1,
        impedance_ohm=complex(50.0, 0.0),
        swr=swr,
        input_power_w=1.0,
        far_field=(
            FarFieldPoint(
                theta_deg=90.0,
                phi_deg=0.0,
                gain_vertical_db=8.0,
                gain_horizontal_db=None,
                gain_total_db=8.0,
                axial_ratio=1.0,
                tilt_deg=0.0,
                polarization=None,
                e_theta_magnitude_v_per_m=None,
                e_theta_phase_deg=None,
                e_phi_magnitude_v_per_m=None,
                e_phi_phase_deg=None,
            ),
            FarFieldPoint(
                theta_deg=90.0,
                phi_deg=180.0,
                gain_vertical_db=-14.0,
                gain_horizontal_db=None,
                gain_total_db=-14.0,
                axial_ratio=1.0,
                tilt_deg=0.0,
                polarization=None,
                e_theta_magnitude_v_per_m=None,
                e_theta_phase_deg=None,
                e_phi_magnitude_v_per_m=None,
                e_phi_phase_deg=None,
            ),
        ),
        power_budget=PowerBudget(
            input_w=1.0,
            radiated_w=0.8,
            structure_loss_w=0.1,
            network_loss_w=0.1,
            efficiency_percent=80.0,
        ),
    )


def _result(points: tuple[FrequencyResult, ...]) -> SimulationResult:
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=SimulationSpec(frequency_plan=FrequencyPlan.single(points[0].frequency_hz)),
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="fake", version="1.0"),
        frequencies=points,
        duration_s=0.01,
    )


class _FixedSolver:
    """Return a completed, matched point without running an engine."""

    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="fake",
            supports_frequency_sweep=True,
            supports_currents=False,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )

    def validate(self, model: object, spec: object) -> tuple[()]:
        del model, spec
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="fake", version="1.0")

    def run(
        self,
        model: object,
        spec: SimulationSpec,
        **kwargs: object,
    ) -> SimulationResult:
        del model, kwargs
        return _result((_point(spec.frequency_plan.start_hz, 1.0),))


def _moxon_2_4ghz() -> MoxonParameters:
    scale = 14_170_000.0 / 2_400_000_000.0
    depth = 9.57 * 0.3048 * scale
    reflector_tip = 4.85 * 0.3048 * scale
    driven_tip = 4.00 * 0.3048 * scale
    gap = depth - reflector_tip - driven_tip
    return MoxonParameters(
        frequency_hz=2_400_000_000.0,
        width_m=25.00 * 0.3048 * scale,
        depth_m=depth,
        reflector_tip_m=reflector_tip,
        driven_tip_m=driven_tip,
        height_m=1.0,
        wire_radius_m=gap / 5.0,
    )


def test_2_4ghz_moxon_optimizer_never_returns_the_067_lambda_gap() -> None:
    parameters = _moxon_2_4ghz()
    wavelength = units.wavelength_m(parameters.frequency_hz)
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor

    result = OptimizeAntenna(_FixedSolver()).execute(
        OptimizeAntennaCommand(
            descriptor=descriptor,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
                segmentation=aligned_policy_for_model(
                    parameters.to_antenna(),
                    parameters.frequency_hz,
                    SegmentationPolicy(min_segments_per_wire=3),
                ),
                far_field=FarFieldRequest(enabled=False),
            ),
            objective=FamilyOptimizationObjective.TARGET_IMPEDANCE,
            budget=budget_for(BudgetProfile.FAST, len(descriptor.variables)),
        )
    )

    assert result.evaluations
    assert result.best_parameters is not None
    best = result.best_parameters
    assert isinstance(best, MoxonParameters)
    assert best.driven_tip_m > 0.0
    assert best.gap_m / wavelength <= 0.10
    assert best.gap_m / wavelength != pytest.approx(0.67)


def test_metrics_include_gain_front_to_back_and_efficiency() -> None:
    result = _result((_point(7_100_000.0, 1.2),))

    metrics = _metrics(
        result,
        7_100_000.0,
        50.0,
        0.0,
        needs_gain=True,
        needs_bandwidth=False,
    )

    assert metrics["max_gain_db"] == pytest.approx(8.0)
    assert metrics["front_to_back_db"] == pytest.approx(22.0)
    assert metrics["efficiency_percent"] == pytest.approx(80.0)


def test_metrics_include_bandwidth_for_a_sweep() -> None:
    result = _result(
        (
            _point(7_000_000.0, 3.0),
            _point(7_050_000.0, 2.0),
            _point(7_100_000.0, 1.0),
            _point(7_150_000.0, 2.0),
            _point(7_200_000.0, 3.0),
        )
    )

    metrics = _metrics(
        result,
        7_100_000.0,
        50.0,
        0.0,
        needs_gain=False,
        needs_bandwidth=True,
    )

    assert metrics["bandwidth_hz"] > 0.0


def test_metrics_skip_missing_gain_and_power_data() -> None:
    point = replace(_point(7_100_000.0, 1.2), far_field=(), power_budget=None)
    result = _result((point,))

    metrics = _metrics(
        result,
        7_100_000.0,
        50.0,
        0.0,
        needs_gain=True,
        needs_bandwidth=False,
    )

    assert "max_gain_db" not in metrics
    assert "front_to_back_db" not in metrics
    assert "efficiency_percent" not in metrics
