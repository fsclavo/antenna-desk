# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Far-field pattern requests."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_finite

MAX_PATTERN_POINTS_PER_AXIS = 1_000


@dataclass(frozen=True, slots=True)
class FarFieldRequest:
    """Angular sampling for a far-field pattern."""

    enabled: bool = True
    theta_start_deg: float = 0.0
    theta_stop_deg: float = 180.0
    theta_count: int = 19
    phi_start_deg: float = 0.0
    phi_stop_deg: float = 0.0
    phi_count: int = 1

    def __post_init__(self) -> None:
        if not self.enabled:
            return

        ensure_finite(self.theta_start_deg, name="theta_start_deg")
        ensure_finite(self.theta_stop_deg, name="theta_stop_deg")
        ensure_finite(self.phi_start_deg, name="phi_start_deg")
        ensure_finite(self.phi_stop_deg, name="phi_stop_deg")

        if not 0.0 <= self.theta_start_deg <= 180.0:
            raise ValueError("theta_start_deg must be between 0 and 180")
        if not 0.0 <= self.theta_stop_deg <= 180.0:
            raise ValueError("theta_stop_deg must be between 0 and 180")
        if self.theta_stop_deg < self.theta_start_deg:
            raise ValueError("theta_stop_deg must be greater than or equal to theta_start_deg")
        if self.theta_count < 1 or self.theta_count > MAX_PATTERN_POINTS_PER_AXIS:
            raise ValueError(f"theta_count must be between 1 and {MAX_PATTERN_POINTS_PER_AXIS}")
        if self.theta_count == 1 and self.theta_stop_deg != self.theta_start_deg:
            raise ValueError("theta_count=1 requires theta_start_deg == theta_stop_deg")

        if not 0.0 <= self.phi_start_deg <= 360.0:
            raise ValueError("phi_start_deg must be between 0 and 360")
        if not 0.0 <= self.phi_stop_deg <= 360.0:
            raise ValueError("phi_stop_deg must be between 0 and 360")
        if self.phi_stop_deg < self.phi_start_deg:
            raise ValueError("phi_stop_deg must be greater than or equal to phi_start_deg")
        if self.phi_count < 1 or self.phi_count > MAX_PATTERN_POINTS_PER_AXIS:
            raise ValueError(f"phi_count must be between 1 and {MAX_PATTERN_POINTS_PER_AXIS}")
        if self.phi_count == 1 and self.phi_stop_deg != self.phi_start_deg:
            raise ValueError("phi_count=1 requires phi_start_deg == phi_stop_deg")

    @property
    def theta_step_deg(self) -> float:
        if not self.enabled or self.theta_count == 1:
            return 0.0
        return (self.theta_stop_deg - self.theta_start_deg) / (self.theta_count - 1)

    @property
    def phi_step_deg(self) -> float:
        if not self.enabled or self.phi_count == 1:
            return 0.0
        return (self.phi_stop_deg - self.phi_start_deg) / (self.phi_count - 1)
