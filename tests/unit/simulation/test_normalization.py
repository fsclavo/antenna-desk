# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.simulation.normalization import (
    calculate_reflection_coefficient,
    calculate_swr,
)


def test_reflection_coefficient_for_manual_example() -> None:
    impedance = complex(82.6979, 46.3060)
    gamma = calculate_reflection_coefficient(impedance, 50.0)
    assert abs(gamma) == pytest.approx(0.40333507086482756)


def test_swr_for_manual_example() -> None:
    impedance = complex(82.6979, 46.3060)
    assert calculate_swr(impedance, 50.0) == pytest.approx(2.35196506839923)


def test_matched_load_has_swr_one() -> None:
    assert calculate_swr(complex(50.0, 0.0), 50.0) == pytest.approx(1.0)


def test_open_circuit_has_infinite_swr() -> None:
    assert math.isinf(calculate_swr(complex(0.0, 0.0), 50.0))


def test_active_load_with_gain_has_infinite_swr() -> None:
    assert math.isinf(calculate_swr(complex(-100.0, 0.0), 50.0))


def test_invalid_reference_impedance_is_rejected() -> None:
    with pytest.raises(ValueError, match="positive"):
        calculate_reflection_coefficient(complex(50.0, 0.0), 0.0)


def test_non_finite_impedance_is_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        calculate_reflection_coefficient(complex(math.nan, 0.0), 50.0)
