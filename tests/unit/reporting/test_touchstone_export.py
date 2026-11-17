# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""One-port Touchstone export formatting."""

from __future__ import annotations

import pytest

from antennadesk.importers.touchstone import parse_touchstone_s1p
from antennadesk.reporting.touchstone import format_touchstone_s1p


def test_format_round_trips_impedance_points() -> None:
    points = (
        (7_000_000.0, 50.0 + 0.0j),
        (7_100_000.0, 75.0 + 10.0j),
        (7_200_000.0, 30.0 - 40.0j),
    )

    text = format_touchstone_s1p(points, 50.0)
    parsed = parse_touchstone_s1p(text)

    assert parsed.reference_impedance_ohm == pytest.approx(50.0)
    assert [point.frequency_hz for point in parsed.points] == pytest.approx(
        [frequency for frequency, _impedance in points]
    )
    assert [point.impedance_ohm for point in parsed.points] == pytest.approx(
        [impedance for _frequency, impedance in points]
    )


def test_format_writes_the_option_line_and_comments() -> None:
    text = format_touchstone_s1p(
        ((7_100_000.0, 75.0 + 0.0j),),
        75.0,
        frequency_unit="kHz",
        comments=("Project: 40 m", "Design: A"),
    )

    lines = text.splitlines()
    assert lines[0].startswith("! AntennaDesk")
    assert "! Project: 40 m" in lines
    assert "! Design: A" in lines
    assert "# kHz S RI R 75" in lines
    assert lines[-1] == "7100 0 0"


def test_format_is_deterministic() -> None:
    points = ((7_100_000.0, 50.0 + 0.0j),)

    assert format_touchstone_s1p(points, 50.0) == format_touchstone_s1p(points, 50.0)


@pytest.mark.parametrize(
    ("points", "reference"),
    [
        ((), 50.0),
        (((0.0, 50.0 + 0.0j),), 50.0),
        (((7_100_000.0, 50.0 + 0.0j),), 0.0),
    ],
)
def test_format_rejects_invalid_input(
    points: tuple[tuple[float, complex], ...],
    reference: float,
) -> None:
    with pytest.raises(ValueError):
        format_touchstone_s1p(points, reference)


def test_format_rejects_an_unsupported_frequency_unit() -> None:
    with pytest.raises(ValueError):
        format_touchstone_s1p(((7_100_000.0, 50.0 + 0.0j),), 50.0, frequency_unit="THz")
