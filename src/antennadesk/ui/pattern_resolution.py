# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Angular sampling presets shared by simulation forms."""

from __future__ import annotations

from ..domain.environment.ground import GroundKind, GroundModel
from ..domain.simulation.far_field import FarFieldRequest

PATTERN_STEPS_DEG: tuple[float, ...] = (10.0, 5.0, 2.0, 1.0)
DEFAULT_PATTERN_STEP_DEG = 5.0


def pattern_counts(step_deg: float, ground: GroundModel) -> tuple[int, int]:
    if step_deg <= 0.0:
        raise ValueError("pattern step must be positive")
    stop = 180.0 if ground.kind is GroundKind.FREE_SPACE else 90.0
    theta_count = round(stop / step_deg) + 1
    phi_count = round(360.0 / step_deg) + 1
    return theta_count, phi_count


def far_field_request(step_deg: float, ground: GroundModel) -> FarFieldRequest:
    theta_count, phi_count = pattern_counts(step_deg, ground)
    return FarFieldRequest(
        enabled=True,
        theta_start_deg=0.0,
        theta_stop_deg=(180.0 if ground.kind is GroundKind.FREE_SPACE else 90.0),
        theta_count=theta_count,
        phi_start_deg=0.0,
        phi_stop_deg=360.0,
        phi_count=phi_count,
    )
