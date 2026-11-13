# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.simulation.result import FarFieldPoint, FrequencyResult
from antennadesk.reporting.localization import identity_labeler
from antennadesk.reporting.pattern_cuts import pattern_cuts


def _frequency(*points: FarFieldPoint) -> FrequencyResult:
    return FrequencyResult(
        frequency_hz=7_100_000.0,
        feed_tag=1,
        feed_segment=1,
        impedance_ohm=complex(50.0, 0.0),
        swr=1.0,
        input_power_w=1.0,
        far_field=points,
    )


def _point(theta: float, phi: float, gain: float) -> FarFieldPoint:
    return FarFieldPoint(
        theta_deg=theta,
        phi_deg=phi,
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


def test_pattern_cuts_use_the_maximum_gain_direction() -> None:
    frequency = _frequency(
        _point(0.0, 0.0, 2.0),
        _point(0.0, 90.0, 1.0),
        _point(90.0, 0.0, -4.0),
        _point(90.0, 90.0, -6.0),
    )

    azimuth, elevation = pattern_cuts(frequency, identity_labeler)

    assert azimuth is not None
    assert elevation is not None
    assert azimuth.angle_deg == 0.0
    assert azimuth.series[0].points == ((0.0, 2.0), (90.0, 1.0))
    assert elevation.angle_deg == 0.0
    assert elevation.series[0].points == ((0.0, 2.0), (90.0, -4.0))


def test_pattern_cuts_report_missing_rows() -> None:
    frequency = _frequency(
        _point(0.0, 0.0, 2.0),
        _point(90.0, 0.0, -4.0),
    )

    azimuth, elevation = pattern_cuts(frequency, identity_labeler)

    assert azimuth is None
    assert elevation is not None


def test_pattern_cuts_return_none_without_far_field() -> None:
    azimuth, elevation = pattern_cuts(_frequency(), identity_labeler)

    assert azimuth is None
    assert elevation is None
