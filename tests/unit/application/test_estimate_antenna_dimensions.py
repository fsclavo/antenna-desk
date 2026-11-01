# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.application.use_cases.estimate_antenna_dimensions import (
    EstimateAntennaDimensions,
)
from antennadesk.domain.design import DesignIntent


def test_estimate_use_case_returns_valid_dipole_parameters() -> None:
    intent = DesignIntent(
        frequency_hz=7_100_000.0,
        antenna_type="wire_dipole",
        height_m=8.0,
    )

    estimate = EstimateAntennaDimensions().execute(intent)

    assert estimate.parameters.frequency_hz == intent.frequency_hz
    assert estimate.parameters.total_length_m > 19.0
    assert estimate.parameters.total_length_m < 21.0
    assert estimate.rows
