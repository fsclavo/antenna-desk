# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""One-port Touchstone parsing and format dispatch."""

from __future__ import annotations

import pytest

from antennadesk.importers.touchstone import (
    TouchstoneError,
    looks_like_touchstone,
    parse_touchstone_s1p,
    parse_touchstone_s2p,
)
from antennadesk.importers.vna import parse_vna_data
from antennadesk.importers.vna_csv import ParsedVnaCsv


def test_parse_default_ma_options() -> None:
    parsed = parse_touchstone_s1p("! NanoVNA export\n7100000 0.2 0\n")

    assert parsed.reference_impedance_ohm == 50.0
    assert parsed.points[0].frequency_hz == pytest.approx(7_100_000.0)
    assert parsed.points[0].impedance_ohm == pytest.approx(75.0 + 0.0j)
    assert parsed.warnings == ()


def test_parse_tolerates_a_utf8_byte_order_mark() -> None:
    parsed = parse_touchstone_s1p("\ufeff# MHz S RI R 50\n7.1 0 0\n")

    assert parsed.points[0].frequency_hz == pytest.approx(7_100_000.0)


def test_parse_ri_with_custom_reference_and_units() -> None:
    parsed = parse_touchstone_s1p("# MHz S RI R 75\n7.1 0.2 0\n")

    assert parsed.reference_impedance_ohm == 75.0
    assert parsed.points[0].frequency_hz == pytest.approx(7_100_000.0)
    assert parsed.points[0].impedance_ohm == pytest.approx(112.5 + 0.0j)


def test_parse_db_magnitude_and_phase() -> None:
    parsed = parse_touchstone_s1p("# Hz S DB R 50\n7100000 -6.020599913279624 90\n")

    assert parsed.points[0].impedance_ohm == pytest.approx(30.0 + 40.0j)


def test_parse_khz_frequency_scale() -> None:
    parsed = parse_touchstone_s1p("# kHz S RI R 50\n7100 0 0\n")

    assert parsed.points[0].frequency_hz == pytest.approx(7_100_000.0)
    assert parsed.points[0].impedance_ohm == pytest.approx(50.0 + 0.0j)


def test_missing_angle_is_assumed_zero_with_a_warning() -> None:
    parsed = parse_touchstone_s1p("# MHz S MA R 50\n7.1 0.5\n")

    assert parsed.points[0].impedance_ohm == pytest.approx(150.0 + 0.0j)
    assert "missing angle" in parsed.warnings[0]


def test_reflection_at_or_above_one_is_skipped() -> None:
    parsed = parse_touchstone_s1p("# MHz S RI R 50\n7.1 1.0 0\n7.2 0.0 0\n")

    assert len(parsed.points) == 1
    assert parsed.points[0].frequency_hz == pytest.approx(7_200_000.0)
    assert "magnitude >= 1" in parsed.warnings[0]


@pytest.mark.parametrize(
    "text",
    [
        "",
        "! only a comment\n",
        "# MHz S RI R 50\n",
        "# MHz Y RI R 50\n7.1 0 0\n",
        "# MHz S RI R 50\n# MHz S RI R 50\n7.1 0 0\n",
        "# MHz S RI R 50\n7.1\n",
        "# MHz S RI R 50\n7.1 0 0 0\n",
        "# MHz S RI R 0\n7.1 0 0\n",
        "# MHz S RI R 50\n-7.1 0 0\n",
        "# MHz S RI R 50\nabc 0 0\n",
    ],
)
def test_invalid_touchstone_is_rejected(text: str) -> None:
    with pytest.raises(TouchstoneError):
        parse_touchstone_s1p(text)


def test_looks_like_touchstone_ignores_comments_and_blank_lines() -> None:
    assert looks_like_touchstone("! comment\n\n# MHz S RI R 50\n7.1 0 0\n") is True
    assert looks_like_touchstone("frequency_hz,r_ohm,x_ohm\n7100000,50,0\n") is False


def test_parse_vna_data_uses_suffix_and_content() -> None:
    touchstone = parse_vna_data(
        "# MHz S RI R 50\n7.1 0 0\n",
        suffix="",
    )
    csv = parse_vna_data(
        "frequency_hz,r_ohm,x_ohm\n7100000,50,0\n",
        suffix=".txt",
    )

    assert touchstone.points[0].impedance_ohm == pytest.approx(50.0 + 0.0j)
    assert isinstance(csv, ParsedVnaCsv)
    assert csv.points[0].impedance_ohm == pytest.approx(50.0 + 0.0j)
    with pytest.raises(TouchstoneError):
        parse_vna_data("# MHz S RI R 50\n", suffix=".s1p")


def test_s2p_uses_only_the_selected_port() -> None:
    text = "# MHz S RI R 50\n7.1 0 0 0.5 0 0.5 0 0.3 0\n"

    port1 = parse_touchstone_s2p(text, port=1)
    port2 = parse_touchstone_s2p(text, port=2)

    assert port1.points[0].impedance_ohm == pytest.approx(50.0 + 0.0j)
    assert port2.points[0].impedance_ohm == pytest.approx(92.857142857 + 0.0j)
    assert port1.profile == "Touchstone S2P port 1"
    assert port2.mapping == "frequency, S22"


def test_s2p_port2_requires_full_rows_and_dispatch_uses_suffix() -> None:
    with pytest.raises(TouchstoneError, match="S22"):
        parse_touchstone_s2p("# MHz S RI R 50\n7.1 0 0 0.5 0\n", port=2)

    parsed = parse_vna_data(
        "# MHz S RI R 50\n7.1 0 0 0.5 0 0.5 0 0.3 0\n",
        suffix=".s2p",
        s2p_port=1,
    )
    assert parsed.points[0].impedance_ohm == pytest.approx(50.0 + 0.0j)
