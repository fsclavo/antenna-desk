# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Physical invariants that do not need an external reference.

These checks catch adapter and normalization bugs that reference comparisons
can miss: a power budget that does not close, a pattern that does not integrate
to the reported directivity, or a rotation that changes the gain.
"""

from __future__ import annotations

import math
import os
from collections.abc import Iterable
from pathlib import Path

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.solver import Nec2cSolver

NEC2C = os.environ.get("NEC2C")
requires_solver = pytest.mark.skipif(
    not NEC2C or not Path(NEC2C).is_file(),
    reason="NEC2C must point to a nec2c executable",
)
FREQUENCY_HZ = 7_100_000.0


def _spec(
    *,
    theta_count: int = 37,
    phi_count: int = 73,
    conductor_losses: bool = False,
) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(FREQUENCY_HZ),
        include_conductor_losses=conductor_losses,
        far_field=FarFieldRequest(
            enabled=True,
            theta_count=theta_count,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=phi_count,
        ),
    )


def _dipole(*, azimuth_deg: float = 0.0):
    return DipoleParameters(
        frequency_hz=FREQUENCY_HZ,
        total_length_m=20.0,
        height_m=0.0,
        azimuth_deg=azimuth_deg,
        wire_radius_m=0.001,
        ground=GroundModel.free_space(),
    ).to_antenna()


def _run(model, spec: SimulationSpec):
    assert NEC2C is not None
    return Nec2cSolver(Path(NEC2C)).run(model, spec)


def _directivity_db(samples: Iterable[tuple[float, float, float | None]]) -> float:
    """Integrate a full-sphere power pattern and return its directivity.

    ``samples`` are ``(theta_deg, phi_deg, gain_db)``.  The angle grid must be
    uniform and cover theta 0..180 and phi 0..360.
    """

    grid: dict[tuple[float, float], float | None] = {}
    for theta_deg, phi_deg, gain_db in samples:
        grid[(theta_deg, phi_deg)] = gain_db
    thetas = sorted({theta for theta, _ in grid})
    phis = sorted({phi for _, phi in grid})
    if len(thetas) < 2 or len(phis) < 2:
        raise ValueError("a full-sphere pattern needs at least two angles per axis")

    step_theta = math.radians((thetas[-1] - thetas[0]) / (len(thetas) - 1))
    step_phi = math.radians((phis[-1] - phis[0]) / (len(phis) - 1))
    total = 0.0
    for theta_index, theta in enumerate(thetas):
        weight_theta = step_theta / 2 if theta_index in (0, len(thetas) - 1) else step_theta
        sin_theta = math.sin(math.radians(theta))
        for phi_index, phi in enumerate(phis):
            gain_db = grid[(theta, phi)]
            if gain_db is None:
                continue
            weight_phi = step_phi / 2 if phi_index in (0, len(phis) - 1) else step_phi
            total += weight_theta * weight_phi * sin_theta * 10.0 ** (gain_db / 10.0)

    gains = [gain for gain in grid.values() if gain is not None]
    if not gains or total <= 0.0:
        raise ValueError("the pattern has no usable gain values")
    return 10.0 * math.log10(4.0 * math.pi * 10.0 ** (max(gains) / 10.0) / total)


def test_pattern_integration_recovers_an_isotropic_pattern() -> None:
    samples = ((theta, phi, 0.0) for theta in range(0, 181, 5) for phi in range(0, 361, 5))

    assert _directivity_db(samples) == pytest.approx(0.0, abs=0.01)


@pytest.mark.solver
@pytest.mark.science
@requires_solver
def test_power_budget_closes_for_a_lossy_dipole() -> None:
    result = _run(_dipole(), _spec(conductor_losses=True))
    budget = result.frequencies[0].power_budget

    assert budget is not None
    total = budget.radiated_w + budget.structure_loss_w + budget.network_loss_w
    assert total == pytest.approx(budget.input_w, rel=0.01)
    assert budget.efficiency_percent == pytest.approx(
        100.0 * budget.radiated_w / budget.input_w,
        abs=0.1,
    )
    assert budget.structure_loss_w > 0.0


@pytest.mark.solver
@pytest.mark.science
@requires_solver
def test_power_budget_is_lossless_without_conductor_losses() -> None:
    result = _run(_dipole(), _spec(conductor_losses=False))
    budget = result.frequencies[0].power_budget

    assert budget is not None
    assert budget.radiated_w == pytest.approx(budget.input_w, rel=1e-6)
    assert budget.structure_loss_w == pytest.approx(0.0, abs=1e-12)
    assert budget.efficiency_percent == pytest.approx(100.0)


@pytest.mark.solver
@pytest.mark.science
@requires_solver
def test_pattern_integral_recovers_the_reported_directivity() -> None:
    result = _run(_dipole(), _spec())
    frequency = result.frequencies[0]

    integrated = _directivity_db(
        (point.theta_deg, point.phi_deg, point.gain_total_db) for point in frequency.far_field
    )

    assert frequency.directivity_db is not None
    assert integrated == pytest.approx(frequency.directivity_db, abs=0.1)
    # Lossless free space: directivity and power gain are the same.
    assert result.max_total_gain_db == pytest.approx(frequency.directivity_db, abs=0.01)


@pytest.mark.solver
@pytest.mark.science
@requires_solver
def test_rotating_the_antenna_rotates_the_pattern_without_changing_gain() -> None:
    first = _run(_dipole(azimuth_deg=0.0), _spec(theta_count=19, phi_count=37))
    second = _run(_dipole(azimuth_deg=90.0), _spec(theta_count=19, phi_count=37))

    assert first.max_total_gain_db == pytest.approx(second.max_total_gain_db, abs=0.05)

    first_gain = {
        (point.theta_deg, point.phi_deg): point.gain_total_db
        for point in first.frequencies[0].far_field
    }
    second_gain = {
        (point.theta_deg, point.phi_deg): point.gain_total_db
        for point in second.frequencies[0].far_field
    }
    comparisons = 0
    for (theta_deg, phi_deg), gain_db in first_gain.items():
        rotated = second_gain.get((theta_deg, (phi_deg + 90.0) % 360.0))
        if gain_db is None or rotated is None:
            continue
        assert rotated == pytest.approx(gain_db, abs=0.05)
        comparisons += 1

    assert comparisons > 100
