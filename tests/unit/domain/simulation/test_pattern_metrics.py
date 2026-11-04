# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.simulation.pattern import (
    PatternGainMetric,
    pattern_gain_offset_db,
)
from antennadesk.domain.simulation.result import FarFieldPoint, FrequencyResult


def _point(theta: float, gain: float) -> FarFieldPoint:
    return FarFieldPoint(
        theta_deg=theta,
        phi_deg=0.0,
        gain_vertical_db=gain,
        gain_horizontal_db=None,
        gain_total_db=gain,
        axial_ratio=None,
        tilt_deg=None,
        polarization="LINEAR",
        e_theta_magnitude_v_per_m=None,
        e_theta_phase_deg=None,
        e_phi_magnitude_v_per_m=None,
        e_phi_phase_deg=None,
    )


def _frequency() -> FrequencyResult:
    return FrequencyResult(
        frequency_hz=14_100_000.0,
        feed_tag=1,
        feed_segment=1,
        impedance_ohm=complex(50.0, 0.0),
        swr=1.0,
        input_power_w=1.0,
        far_field=(_point(0.0, 5.0), _point(90.0, 2.0)),
        directivity_db=8.0,
        realized_gain_db=4.0,
    )


def test_pattern_metric_offsets_are_relative_to_the_sampled_maximum() -> None:
    frequency = _frequency()

    assert pattern_gain_offset_db(frequency, PatternGainMetric.POWER) == 0.0
    assert pattern_gain_offset_db(frequency, PatternGainMetric.DIRECTIVITY) == 3.0
    assert pattern_gain_offset_db(frequency, PatternGainMetric.REALIZED) == -1.0


def test_pattern_metric_offset_is_none_when_metric_is_missing() -> None:
    from dataclasses import replace

    frequency = replace(_frequency(), directivity_db=None, realized_gain_db=None)

    assert pattern_gain_offset_db(frequency, PatternGainMetric.DIRECTIVITY) is None
    assert pattern_gain_offset_db(frequency, PatternGainMetric.REALIZED) is None
