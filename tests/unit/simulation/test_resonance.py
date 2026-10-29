# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.simulation.resonance import find_resonances


def test_finds_a_linear_zero_crossing() -> None:
    points = find_resonances(
        [7_000_000.0, 7_100_000.0],
        [complex(70.0, -10.0), complex(80.0, 10.0)],
    )

    assert len(points) == 1
    assert points[0].frequency_hz == pytest.approx(7_050_000.0)
    assert points[0].impedance_ohm == pytest.approx(complex(75.0, 0.0))


def test_marks_an_exact_zero() -> None:
    points = find_resonances(
        [7_000_000.0, 7_100_000.0, 7_200_000.0],
        [complex(70.0, -5.0), complex(75.0, 0.0), complex(80.0, 5.0)],
    )

    assert len(points) == 1
    assert points[0].frequency_hz == pytest.approx(7_100_000.0)


def test_returns_empty_without_a_crossing() -> None:
    points = find_resonances(
        [7_000_000.0, 7_100_000.0, 7_200_000.0],
        [complex(70.0, 1.0), complex(75.0, 2.0), complex(80.0, 3.0)],
    )
    assert points == ()


def test_requires_matching_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        find_resonances([7_000_000.0], [])


def test_single_frequency_has_no_resonance() -> None:
    assert find_resonances([7_000_000.0], [complex(50.0, 0.0)]) == ()
