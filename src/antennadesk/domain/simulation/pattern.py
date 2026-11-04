# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pattern metrics shared by optimization and comparison."""

from __future__ import annotations

import math
from collections.abc import Sequence
from enum import StrEnum

from .result import FarFieldPoint, FrequencyResult


class PatternGainMetric(StrEnum):
    POWER = "power"
    DIRECTIVITY = "directivity"
    REALIZED = "realized"


def pattern_gain_offset_db(
    frequency: FrequencyResult,
    metric: PatternGainMetric,
) -> float | None:
    """Return the constant to add to each power-gain point for a metric.

    Directivity and realized gain are derived at the maximum-gain direction.
    Applying the difference between that value and the sampled maximum preserves
    the pattern shape while shifting its peak to the requested metric.
    """

    if metric is PatternGainMetric.POWER:
        return 0.0
    maximum = max_power_gain_db(frequency.far_field)
    if maximum is None:
        return None
    if metric is PatternGainMetric.DIRECTIVITY:
        target = frequency.directivity_db
    else:
        target = frequency.realized_gain_db
    if target is None or not math.isfinite(target):
        return None
    return target - maximum


def takeoff_angle_deg(theta_deg: float) -> float:
    """Return the elevation above the ground plane for a NEC theta angle.

    NEC measures theta from the zenith, so a point on the horizon (theta = 90)
    has a takeoff angle of 0 degrees.
    """

    return 90.0 - theta_deg


def max_power_gain_db(points: Sequence[FarFieldPoint]) -> float | None:
    gains = [
        point.gain_total_db
        for point in points
        if point.gain_total_db is not None and math.isfinite(point.gain_total_db)
    ]
    return max(gains) if gains else None


def front_to_back_db(points: Sequence[FarFieldPoint]) -> float | None:
    """Return forward gain minus the gain 180 degrees away in azimuth.

    The rear sample is taken at the same elevation as the forward maximum.
    """

    valid = [
        point
        for point in points
        if point.gain_total_db is not None and math.isfinite(point.gain_total_db)
    ]
    if not valid:
        return None
    forward = max(valid, key=lambda point: point.gain_total_db or -math.inf)
    rear_phi = (forward.phi_deg + 180.0) % 360.0
    rear = min(
        valid,
        key=lambda point: (
            abs(point.theta_deg - forward.theta_deg)
            + abs(((point.phi_deg - rear_phi + 180.0) % 360.0) - 180.0)
        ),
    )
    if rear.gain_total_db is None or forward.gain_total_db is None:
        return None
    return forward.gain_total_db - rear.gain_total_db
