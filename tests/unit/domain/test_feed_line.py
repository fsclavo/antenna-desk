# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.common.units import SPEED_OF_LIGHT_M_PER_S


def test_zero_length_line_returns_the_load_impedance() -> None:
    line = FeedLine(length_m=0.0)

    assert line.is_active is False
    assert line.input_impedance(complex(70.0, 12.0), 7_100_000.0) == complex(70.0, 12.0)


def test_quarter_wave_line_transforms_100_ohms_to_25_ohms() -> None:
    frequency_hz = 100_000_000.0
    quarter_wavelength_m = SPEED_OF_LIGHT_M_PER_S / frequency_hz / 4.0
    line = FeedLine(length_m=quarter_wavelength_m)

    transformed = line.input_impedance(complex(100.0, 0.0), frequency_hz)

    assert transformed.real == pytest.approx(25.0, rel=1e-9)
    assert transformed.imag == pytest.approx(0.0, abs=1e-9)


def test_velocity_factor_scales_the_electrical_length() -> None:
    frequency_hz = 100_000_000.0
    quarter_wavelength_m = SPEED_OF_LIGHT_M_PER_S / frequency_hz / 4.0
    line = FeedLine(length_m=quarter_wavelength_m * 0.66, velocity_factor=0.66)

    transformed = line.input_impedance(complex(100.0, 0.0), frequency_hz)

    assert transformed.real == pytest.approx(25.0, rel=1e-9)


def test_matched_line_does_not_change_a_matched_load() -> None:
    line = FeedLine(length_m=30.0, matched_loss_db_per_100m=2.0)

    transformed = line.input_impedance(complex(50.0, 0.0), 14_000_000.0)

    assert transformed == pytest.approx(complex(50.0, 0.0), abs=1e-9)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"characteristic_impedance_ohm": 0.0},
        {"length_m": -1.0},
        {"velocity_factor": 0.0},
        {"velocity_factor": 1.1},
        {"matched_loss_db_per_100m": -1.0},
    ],
)
def test_rejects_invalid_parameters(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        FeedLine(**kwargs)
