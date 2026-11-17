# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Domain measurement conversions and validation."""

from __future__ import annotations

import math

import pytest

from antennadesk.domain.measurement import (
    impedance_from_reflection,
    reflection_coefficient,
    swr_for_impedance,
)


def test_reflection_coefficient_round_trips_a_passive_impedance() -> None:
    for impedance in (50 + 0j, 75 + 10j, 20 - 30j):
        reflection = reflection_coefficient(impedance, 50.0)
        restored = impedance_from_reflection(reflection, 50.0)
        assert restored == pytest.approx(impedance)


def test_swr_uses_the_reflection_coefficient() -> None:
    assert swr_for_impedance(50 + 0j, 50.0) == pytest.approx(1.0)
    assert swr_for_impedance(100 + 0j, 50.0) == pytest.approx(2.0)
    assert swr_for_impedance(25 + 0j, 50.0) == pytest.approx(2.0)
    assert swr_for_impedance(150 + 0j, 50.0) == pytest.approx(3.0)


def test_reflection_helpers_reject_invalid_values() -> None:
    with pytest.raises(ValueError):
        reflection_coefficient(50 + 0j, 0.0)
    with pytest.raises(ValueError):
        reflection_coefficient(complex(math.inf, 0.0), 50.0)
    with pytest.raises(ValueError):
        impedance_from_reflection(complex(1.0, 0.0), 50.0)
    with pytest.raises(ValueError):
        impedance_from_reflection(complex(math.nan, 0.0), 50.0)
