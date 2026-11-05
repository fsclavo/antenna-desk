# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pattern snapshots and the project size budget with the real engine."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from nec2c_support import (
    g5rv_model_and_segmentation,
)

from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationStatus
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.solver import Nec2cSolver

NEC2C = os.environ.get("NEC2C")
pytestmark = [
    pytest.mark.solver,
    pytest.mark.science,
    pytest.mark.slow,
    pytest.mark.skipif(
        not NEC2C or not Path(NEC2C).is_file(),
        reason="NEC2C must point to a nec2c executable",
    ),
]


def test_g5rv_default_budgeted_pattern_completes(solver: Nec2cSolver) -> None:
    from antennadesk.domain.simulation.bands import band_snapshot_frequencies
    from antennadesk.domain.simulation.budget import choose_pattern_step
    from antennadesk.ui.pattern_resolution import pattern_counts

    model, segmentation, ground = g5rv_model_and_segmentation()
    plan = FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 41)
    snapshots = band_snapshot_frequencies(plan, preferred_frequency_hz=14_100_000.0)
    segment_count = sum(segmentation.segments_for(wire, plan.stop_hz) for wire in model.wires)
    budget = choose_pattern_step(
        frequency_count=plan.count,
        pattern_frequency_count=len(snapshots),
        segment_count=segment_count,
        candidate_steps=(1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        counts_for_step=lambda step: pattern_counts(step, ground),
    )

    assert budget.pattern_step_deg == 1.0
    spec = SimulationSpec(
        frequency_plan=plan,
        segmentation=segmentation,
        include_conductor_losses=True,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=91,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=361,
        ),
        pattern_frequencies_hz=snapshots,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 41
    assert sum(1 for frequency in result.frequencies if frequency.far_field) == 9
    assert all(frequency.currents for frequency in result.frequencies)
    assert len(result.raw_output) < 50 * 1024 * 1024


def test_g5rv_dense_sweep_uses_pattern_snapshots(solver: Nec2cSolver) -> None:
    from antennadesk.domain.simulation.bands import band_snapshot_frequencies
    from antennadesk.domain.simulation.budget import (
        DEFAULT_MAX_PROJECT_BYTES,
        choose_pattern_step,
    )
    from antennadesk.ui.pattern_resolution import pattern_counts

    model, segmentation, ground = g5rv_model_and_segmentation()
    plan = FrequencyPlan.sweep(3_500_000.0, 30_000_000.0, 200)
    snapshots = band_snapshot_frequencies(plan, preferred_frequency_hz=14_100_000.0)
    segment_count = sum(segmentation.segments_for(wire, plan.stop_hz) for wire in model.wires)
    budget = choose_pattern_step(
        frequency_count=plan.count,
        pattern_frequency_count=len(snapshots),
        segment_count=segment_count,
        candidate_steps=(1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        counts_for_step=lambda step: pattern_counts(step, ground),
    )

    assert budget.pattern_step_deg == 1.0
    assert budget.estimated_project_bytes < DEFAULT_MAX_PROJECT_BYTES
    spec = SimulationSpec(
        frequency_plan=plan,
        segmentation=segmentation,
        include_conductor_losses=True,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=90.0,
            theta_count=91,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=361,
        ),
        pattern_frequencies_hz=snapshots,
    )

    result = solver.run(model, spec)

    assert result.status is SimulationStatus.COMPLETED
    assert len(result.frequencies) == 200
    assert sum(1 for frequency in result.frequencies if frequency.far_field) == 9
    assert all(frequency.currents for frequency in result.frequencies)
    assert all(frequency.swr is not None for frequency in result.frequencies)
    assert len(result.raw_output) < 50 * 1024 * 1024
