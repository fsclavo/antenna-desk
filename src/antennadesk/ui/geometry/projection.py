# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared orthographic projection for the geometry and pattern 3D views."""

from __future__ import annotations

import math


def project_world(
    x: float,
    y: float,
    z: float,
    yaw_deg: float,
    pitch_deg: float,
) -> tuple[float, float]:
    """Project a world vector to the shared orthographic screen plane.

    The returned ``y`` grows upward. Callers invert it when painting.
    """

    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    cos_yaw = math.cos(yaw)
    sin_yaw = math.sin(yaw)
    cos_pitch = math.cos(pitch)
    sin_pitch = math.sin(pitch)
    rotated_x = x * cos_yaw - y * sin_yaw
    rotated_y = x * sin_yaw + y * cos_yaw
    return rotated_x, rotated_y * sin_pitch + z * cos_pitch
