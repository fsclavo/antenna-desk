# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared orthographic projection for the two 3D views."""

from __future__ import annotations

import math

import pytest

from antennadesk.ui.geometry.projection import project_world
from antennadesk.ui.widgets.geometry_view import GeometryView


def test_projection_is_identity_at_zero_angles() -> None:
    assert project_world(1.0, 2.0, 3.0, 0.0, 0.0) == pytest.approx((1.0, 3.0))
    assert project_world(0.0, 0.0, 1.0, 0.0, 0.0) == pytest.approx((0.0, 1.0))


def test_projection_rotates_yaw_and_applies_pitch() -> None:
    assert project_world(0.0, 1.0, 0.0, 90.0, 0.0) == pytest.approx((-1.0, 0.0), abs=1e-12)
    assert project_world(0.0, 0.0, 1.0, 0.0, 90.0) == pytest.approx((0.0, 0.0), abs=1e-12)


def test_geometry_3d_uses_the_shared_projection() -> None:
    yaw_deg = 38.0
    pitch_deg = 26.0
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)

    projected = GeometryView._project_3d(
        1.2,
        -0.7,
        0.9,
        math.cos(yaw),
        math.sin(yaw),
        math.cos(pitch),
        math.sin(pitch),
    )

    assert projected == pytest.approx(project_world(1.2, -0.7, 0.9, yaw_deg, pitch_deg))
