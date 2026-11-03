# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.simulation.band_summary import summarize_band
from antennadesk.domain.simulation.bands import amateur_band_by_id
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


def _point(theta_deg: float, gain: float) -> FarFieldPoint:
    return FarFieldPoint(
        theta_deg=theta_deg,
        phi_deg=0.0,
        gain_vertical_db=gain,
        gain_horizontal_db=None,
        gain_total_db=gain,
        axial_ratio=0.0,
        tilt_deg=0.0,
        polarization="LINEAR",
        e_theta_magnitude_v_per_m=None,
        e_theta_phase_deg=None,
        e_phi_magnitude_v_per_m=None,
        e_phi_phase_deg=None,
    )


def _result() -> SimulationResult:
    spec = SimulationSpec(frequency_plan=FrequencyPlan.sweep(7_000_000.0, 7_200_000.0, 3))
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="test", version="1"),
        frequencies=(
            FrequencyResult(
                frequency_hz=7_000_000.0,
                feed_tag=1,
                feed_segment=1,
                impedance_ohm=complex(50.0, 0.0),
                swr=2.0,
                input_power_w=1.0,
                far_field=(_point(90.0, 2.0),),
            ),
            FrequencyResult(
                frequency_hz=7_100_000.0,
                feed_tag=1,
                feed_segment=1,
                impedance_ohm=complex(50.0, 0.0),
                swr=1.2,
                input_power_w=1.0,
                far_field=(_point(75.0, 5.0),),
            ),
            FrequencyResult(
                frequency_hz=7_200_000.0,
                feed_tag=1,
                feed_segment=1,
                impedance_ohm=complex(50.0, 0.0),
                swr=1.8,
                input_power_w=1.0,
                far_field=(_point(60.0, 3.0),),
            ),
        ),
    )


def test_band_summary_reports_best_swr_and_takeoff() -> None:
    band = amateur_band_by_id("40m")
    assert band is not None

    summary = summarize_band(band, _result())

    assert summary.best_swr == 1.2
    assert summary.best_swr_hz == 7_100_000.0
    assert summary.max_gain_db == 5.0
    assert summary.takeoff_deg == 15.0
    assert summary.status is SimulationStatus.COMPLETED


def test_band_summary_handles_missing_patterns() -> None:
    band = amateur_band_by_id("40m")
    assert band is not None
    result = _result()
    from dataclasses import replace

    no_patterns = replace(
        result,
        frequencies=tuple(replace(frequency, far_field=()) for frequency in result.frequencies),
    )

    summary = summarize_band(band, no_patterns)

    assert summary.best_swr == 1.2
    assert summary.max_gain_db is None
    assert summary.takeoff_deg is None


def test_band_summary_ignores_sentinel_gain_values() -> None:
    from dataclasses import replace

    band = amateur_band_by_id("40m")
    assert band is not None
    result = _result()
    sentinel = replace(
        result,
        frequencies=tuple(
            replace(frequency, far_field=(_point(0.0, -999.99),))
            for frequency in result.frequencies
        ),
    )

    summary = summarize_band(band, sentinel)

    assert summary.max_gain_db is None
    assert summary.takeoff_deg is None
