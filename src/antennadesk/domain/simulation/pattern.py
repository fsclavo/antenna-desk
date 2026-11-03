# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pattern metrics shared by optimization and comparison."""

from __future__ import annotations

import math
from collections.abc import Sequence

from .result import FarFieldPoint


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
