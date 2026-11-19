# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Decision metric definitions from stored far-field samples."""

from __future__ import annotations

import math

import pytest

from antennadesk.domain.simulation.metrics import (
    circular_metrics,
    decision_metrics,
    half_power_beamwidth,
    measure_swr_bandwidth,
    swr_bandwidth_rows,
)
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    PowerBudget,
)


def _point(
    theta: float,
    phi: float,
    gain: float,
    *,
    axial_ratio: float = 1.0,
    polarization: str = "RIGHT",
) -> FarFieldPoint:
    return FarFieldPoint(
        theta_deg=theta,
        phi_deg=phi,
        gain_vertical_db=gain,
        gain_horizontal_db=None,
        gain_total_db=gain,
        axial_ratio=axial_ratio,
        tilt_deg=0.0,
        polarization=polarization,
        e_theta_magnitude_v_per_m=1.0,
        e_theta_phase_deg=0.0,
        e_phi_magnitude_v_per_m=1.0,
        e_phi_phase_deg=90.0,
    )


def _frequency(
    points: tuple[FarFieldPoint, ...],
    swr: float = 1.5,
    frequency_hz: float = 7_100_000.0,
) -> FrequencyResult:
    return FrequencyResult(
        frequency_hz=frequency_hz,
        feed_tag=1,
        feed_segment=1,
        impedance_ohm=complex(50.0, 0.0),
        swr=swr,
        input_power_w=1.0,
        far_field=points,
        power_budget=PowerBudget(1.0, 0.8, 0.2, 0.0, 80.0),
        directivity_db=8.0,
        realized_gain_db=4.0,
    )


def test_swr_bandwidth_is_bracketed_or_reported_as_unbracketed() -> None:
    frequencies = [7.0e6, 7.1e6, 7.2e6]
    bracketed = measure_swr_bandwidth(
        frequencies,
        [3.0, 1.5, 3.0],
        center_hz=7.1e6,
    )
    unbracketed = measure_swr_bandwidth(
        frequencies,
        [1.5, 1.5, 3.0],
        center_hz=7.0e6,
    )

    assert bracketed.bracketed is True
    assert bracketed.bandwidth_hz == pytest.approx(0.0666667e6, rel=1e-5)
    assert unbracketed.bracketed is False
    assert unbracketed.bandwidth_hz is None


def test_bandwidth_rows_keep_every_sample_and_edge_state() -> None:
    rows = swr_bandwidth_rows([7.0e6, 7.1e6, 7.2e6], [1.5, 1.5, 3.0])

    assert len(rows) == 3
    assert rows[0].bracketed is False
    assert rows[1].bracketed is False
    assert rows[2].bracketed is False


def test_half_power_beamwidth_handles_azimuth_wrap_and_elevation() -> None:
    azimuth_points = tuple(
        _point(
            90.0,
            phi,
            10.0 if phi in {0.0, 360.0} else (7.01 if phi in {30.0, 330.0} else 0.0),
        )
        for phi in (0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0)
    )
    elevation_points = tuple(
        _point(
            theta,
            0.0,
            10.0 if theta == 90.0 else (7.01 if theta in {70.0, 110.0} else 0.0),
        )
        for theta in (30.0, 50.0, 70.0, 90.0, 110.0, 130.0, 150.0)
    )

    azimuth = half_power_beamwidth(azimuth_points, axis="phi", cut_value=90.0)
    elevation = half_power_beamwidth(elevation_points, axis="theta", cut_value=0.0)

    assert azimuth.width_deg == pytest.approx(60.0, abs=2.0)
    assert elevation.width_deg == pytest.approx(40.0, abs=5.0)
    assert azimuth.resolution_deg == pytest.approx(30.0)
    assert elevation.resolution_deg == pytest.approx(20.0)


def test_decision_metrics_report_gain_bandwidth_and_circular_values() -> None:
    points = (
        _point(90.0, 0.0, 10.0, axial_ratio=1.0),
        _point(90.0, 180.0, 0.0, axial_ratio=1.0),
    )
    frequency = _frequency(points)
    frequencies = (
        _frequency(points, swr=3.0, frequency_hz=7.0e6),
        frequency,
        _frequency(points, swr=3.0, frequency_hz=7.2e6),
    )

    metrics = decision_metrics(frequency, frequencies)

    assert metrics.swr_bandwidth_2_1.bracketed is True
    assert metrics.front_to_back_db == pytest.approx(10.0)
    assert metrics.takeoff_deg == pytest.approx(0.0)
    assert metrics.efficiency_percent == pytest.approx(80.0)
    assert metrics.axial_ratio_db == pytest.approx(0.0)
    assert metrics.polarization_sense == "RHCP"
    assert metrics.cp_gain_db == pytest.approx(10.0)
    assert math.isinf(metrics.cross_polar_discrimination_db or 0.0)


def test_linear_polarization_is_labelled_and_cp_gain_is_three_db_below() -> None:
    frequency = _frequency((_point(90.0, 0.0, 10.0, axial_ratio=1000.0, polarization="LINEAR"),))

    circular = circular_metrics(frequency)

    assert circular.sense == "linear"
    assert circular.cp_gain_db == pytest.approx(7.0, abs=0.1)
    assert circular.axial_ratio_db is not None
    assert circular.axial_ratio_db > 50.0
