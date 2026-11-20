# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Direct tests for the Qt-free far-field budget planner."""

from __future__ import annotations

import pytest

from antennadesk.application.pattern_planning import (
    fit_band_specs_to_budget,
    fit_spec_to_budget,
    snapshot_frequencies,
)
from antennadesk.application.pattern_resolution import far_field_request
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec


def _model(total_length_m: float = 20.0) -> object:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=total_length_m,
        height_m=8.0,
    ).to_antenna()


def _spec(
    *,
    frequency_plan: FrequencyPlan | None = None,
    far_field: FarFieldRequest | None = None,
) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=frequency_plan or FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=far_field or far_field_request(5.0, _model().environment.ground),
    )


def test_requested_step_is_kept_when_it_fits() -> None:
    plan = fit_spec_to_budget(
        _model(),
        _spec(),
        requested_step_deg=10.0,
        pattern_frequency_count=1,
    )

    assert plan.budget is not None
    assert plan.budget.far_field_enabled is True
    assert plan.spec.far_field.theta_step_deg == pytest.approx(10.0)
    assert plan.diagnostic is None


def test_pattern_is_disabled_when_the_sweep_cannot_fit() -> None:
    plan = fit_spec_to_budget(
        _model(total_length_m=200.0),
        _spec(frequency_plan=FrequencyPlan.sweep(7_000_000.0, 7_300_000.0, 10_000)),
        requested_step_deg=1.0,
        pattern_frequency_count=1,
    )

    assert plan.budget is not None
    assert plan.budget.far_field_enabled is False
    assert plan.spec.far_field.enabled is False
    assert plan.spec.pattern_frequencies_hz == ()
    assert plan.diagnostic is not None
    assert plan.diagnostic.code == "solver.pattern_disabled"


def test_disabled_far_field_clears_snapshots_without_a_budget() -> None:
    spec = _spec(
        far_field=FarFieldRequest(enabled=False),
    )
    plan = fit_spec_to_budget(
        _model(),
        spec,
        requested_step_deg=None,
        pattern_frequency_count=5,
    )

    assert plan.spec.pattern_frequencies_hz == ()
    assert plan.budget is None
    assert plan.diagnostic is None


def test_snapshot_frequencies_respect_an_explicit_count() -> None:
    frequencies = snapshot_frequencies(
        FrequencyPlan.sweep(7_000_000.0, 7_300_000.0, 100),
        preferred_frequency_hz=7_100_000.0,
        count=5,
    )

    assert len(frequencies) == 5
    assert frequencies[0] == pytest.approx(7_000_000.0)
    assert frequencies[-1] == pytest.approx(7_300_000.0)


def test_band_planning_shares_one_pattern_step() -> None:
    specs = (
        _spec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
        _spec(frequency_plan=FrequencyPlan.single(14_100_000.0)),
    )

    fitted, budget = fit_band_specs_to_budget(
        _model(),
        specs,
        requested_step_deg=10.0,
    )

    assert budget is not None
    assert budget.far_field_enabled is True
    assert len(fitted) == 2
    assert fitted[0].far_field.theta_step_deg == fitted[1].far_field.theta_step_deg
    assert fitted[0].far_field.theta_step_deg == pytest.approx(10.0)


def test_empty_band_batch_keeps_its_input() -> None:
    fitted, budget = fit_band_specs_to_budget(
        _model(),
        (),
        requested_step_deg=None,
    )

    assert fitted == ()
    assert budget is None
