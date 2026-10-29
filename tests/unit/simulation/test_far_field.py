# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.simulation.far_field import FarFieldRequest


def test_default_request() -> None:
    request = FarFieldRequest()
    assert request.enabled is True
    assert request.theta_step_deg == pytest.approx(10.0)
    assert request.phi_step_deg == 0.0


def test_three_dimensional_request() -> None:
    request = FarFieldRequest(
        theta_start_deg=0.0,
        theta_stop_deg=180.0,
        theta_count=19,
        phi_start_deg=0.0,
        phi_stop_deg=360.0,
        phi_count=37,
    )
    assert request.theta_step_deg == pytest.approx(10.0)
    assert request.phi_step_deg == pytest.approx(10.0)


def test_disabled_request_skips_validation() -> None:
    request = FarFieldRequest(enabled=False, theta_count=0, phi_count=0)
    assert request.enabled is False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"theta_start_deg": -1.0},
        {"theta_stop_deg": 181.0},
        {"theta_start_deg": 90.0, "theta_stop_deg": 80.0},
        {"theta_count": 0},
        {"theta_count": 1, "theta_start_deg": 0.0, "theta_stop_deg": 10.0},
        {"phi_start_deg": -1.0},
        {"phi_stop_deg": 361.0},
        {"phi_start_deg": 90.0, "phi_stop_deg": 80.0},
        {"phi_count": 0},
        {"phi_count": 1, "phi_start_deg": 0.0, "phi_stop_deg": 10.0},
    ],
)
def test_invalid_requests_are_rejected(kwargs: dict[str, float | int]) -> None:
    with pytest.raises(ValueError):
        FarFieldRequest(**kwargs)
