# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""NEC2C reference check for the log-periodic transposed feed."""

from __future__ import annotations

import math
import os
from dataclasses import replace
from pathlib import Path

import pytest

from antennadesk.domain.antennas.log_periodic import (
    LogPeriodicParameters,
    cebik_10m_log_periodic_parameters,
)
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationResult, SimulationStatus
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.solver import Nec2cSolver

NEC2C = os.environ.get("NEC2C")
pytestmark = [
    pytest.mark.solver,
    pytest.mark.science,
    pytest.mark.skipif(
        not NEC2C or not Path(NEC2C).is_file(),
        reason="NEC2C must point to a nec2c executable",
    ),
]


def _spec(parameters: LogPeriodicParameters, segments: tuple[int, ...]) -> SimulationSpec:
    model = parameters.to_antenna()
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(29_000_000.0),
        segmentation=SegmentationPolicy(
            wire_segments=tuple(
                (wire.id, count) for wire, count in zip(model.wires, segments, strict=True)
            ),
            min_segments_per_wire=3,
        ),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=90.0,
            theta_stop_deg=90.0,
            theta_count=1,
            phi_start_deg=0.0,
            phi_stop_deg=180.0,
            phi_count=181,
        ),
    )


def _run(
    solver: Nec2cSolver,
    parameters: LogPeriodicParameters,
    segments: tuple[int, ...],
    *,
    reverse: bool = True,
) -> SimulationResult:
    model = parameters.to_antenna()
    if not reverse:
        model = replace(
            model,
            transmission_lines=tuple(
                replace(line, phase_reversal=False) for line in model.transmission_lines
            ),
        )
    result = solver.run(model, _spec(parameters, segments))
    assert result.status is SimulationStatus.COMPLETED, result.diagnostics
    return result


def _gain_at(result: SimulationResult, phi_deg: float) -> float:
    points = result.frequencies[0].far_field
    candidates = [
        point
        for point in points
        if abs(point.theta_deg - 90.0) < 0.6 and abs(point.phi_deg - phi_deg) < 0.6
    ]
    assert candidates
    point = min(candidates, key=lambda item: abs(item.phi_deg - phi_deg))
    assert point.gain_total_db is not None
    return point.gain_total_db


def _front_to_back(result: SimulationResult) -> float:
    return _gain_at(result, 0.0) - _gain_at(result, 180.0)


def _center_currents(result: SimulationResult) -> list[tuple[float, float]]:
    by_tag: dict[int, list] = {}
    for current in result.frequencies[0].currents:
        by_tag.setdefault(current.tag, []).append(current)
    values = []
    for tag in sorted(by_tag):
        center = min(by_tag[tag], key=lambda item: abs(item.y_m))
        values.append((center.magnitude_a, center.phase_deg))
    return values


def test_cebik_10m_reference_matches_published_nec4_values(solver: Nec2cSolver) -> None:
    parameters = cebik_10m_log_periodic_parameters()
    result = _run(solver, parameters, (43, 41, 39, 37))

    impedance = result.frequencies[0].impedance_ohm
    assert impedance.real > 0.0
    assert impedance.real == pytest.approx(52.38, abs=1.0)
    assert impedance.imag == pytest.approx(-1.39, abs=1.0)
    assert result.max_total_gain_db == pytest.approx(7.36, abs=0.05)
    assert _front_to_back(result) == pytest.approx(22.01, abs=0.5)

    # Published element-center currents at 29 MHz for the 75-ohm line:
    # 0.53/10.6, 0.89/-79.1, 0.94/-168.1, 0.55/109.6. The magnitudes are
    # scaled by the source amplitude; the relative shape and phases are the
    # independent check.
    currents = _center_currents(result)
    assert len(currents) == 4
    published_phases = (10.6, -79.1, -168.1, 109.6)
    for (magnitude, phase), expected_phase in zip(currents, published_phases, strict=True):
        assert magnitude > 0.0
        assert phase == pytest.approx(expected_phase, abs=2.0)
    peak = max(magnitude for magnitude, _phase in currents)
    relative = [magnitude / peak for magnitude, _phase in currents]
    assert relative == pytest.approx((0.53 / 0.94, 0.89 / 0.94, 1.0, 0.55 / 0.94), abs=0.02)


def test_reference_gain_and_front_to_back_are_segmentation_stable(
    solver: Nec2cSolver,
) -> None:
    parameters = cebik_10m_log_periodic_parameters()
    results = [
        _run(solver, parameters, counts)
        for counts in ((43, 41, 39, 37), (21, 21, 21, 21), (31, 29, 27, 25))
    ]

    gains = [result.max_total_gain_db for result in results]
    ratios = [_front_to_back(result) for result in results]
    assert all(gain is not None for gain in gains)
    assert max(gains) - min(gains) < 0.05  # type: ignore[type-var]
    assert max(ratios) - min(ratios) < 0.5
    for result in results:
        assert result.frequencies[0].impedance_ohm.real > 0.0


def test_200_ohm_phase_line_matches_the_published_variant(solver: Nec2cSolver) -> None:
    parameters = replace(cebik_10m_log_periodic_parameters(), phase_line_impedance_ohm=200.0)
    result = _run(solver, parameters, (43, 41, 39, 37))

    assert result.max_total_gain_db == pytest.approx(7.04, abs=0.05)
    assert _front_to_back(result) == pytest.approx(24.56, abs=0.5)


def test_removing_the_phase_reversal_collapses_the_pattern(solver: Nec2cSolver) -> None:
    parameters = cebik_10m_log_periodic_parameters()
    result = _run(solver, parameters, (43, 41, 39, 37), reverse=False)

    assert result.frequencies[0].impedance_ohm.real > 0.0
    assert (result.max_total_gain_db or -math.inf) < 6.0
    assert _front_to_back(result) < 5.0


def test_deck_uses_the_negative_characteristic_impedance(solver: Nec2cSolver) -> None:
    del solver
    from antennadesk.simulation.nec2.input_writer import write_nec2_input

    parameters = cebik_10m_log_periodic_parameters()
    model = parameters.to_antenna()
    deck = write_nec2_input(model, _spec(parameters, (43, 41, 39, 37)))

    tl_lines = [line for line in deck.text.splitlines() if line.startswith("TL ")]
    assert len(tl_lines) == 3
    assert all(line.split()[5].startswith("-75.") for line in tl_lines)
