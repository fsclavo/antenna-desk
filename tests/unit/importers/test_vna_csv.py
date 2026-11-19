# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.importers.vna_csv import (
    MAX_VNA_ROWS,
    VnaColumnMapping,
    VnaCsvError,
    parse_number,
    parse_vna_csv,
)


def test_parses_frequency_r_x_csv() -> None:
    parsed = parse_vna_csv("frequency_hz,r_ohm,x_ohm\n7000000,50,0\n7100000,70,10\n")

    assert len(parsed.points) == 2
    assert parsed.points[0].frequency_hz == 7_000_000.0
    assert parsed.points[0].impedance_ohm == complex(50.0, 0.0)
    assert parsed.points[0].swr(50.0) == pytest.approx(1.0)


def test_parses_s11_real_imaginary_csv() -> None:
    parsed = parse_vna_csv("frequency_mhz,s11_real,s11_imag\n7.1,0.2,0.1\n")

    assert parsed.points[0].frequency_hz == pytest.approx(7_100_000.0)
    assert parsed.points[0].impedance_ohm.real > 0.0


def test_parses_magnitude_phase_csv() -> None:
    parsed = parse_vna_csv("frequency_mhz,magnitude,phase_deg\n7.1,0.2,0\n")

    assert parsed.points[0].impedance_ohm == pytest.approx(complex(75.0, 0.0))


def test_parses_nanovna_decimal_comma_and_semicolon() -> None:
    text = (
        "# NanoVNA Saver export\n"
        "frequency (Hz);R (Ω);X (Ω)\n"
        "7.000.000;50,0;0,0\n"
        "7.100.000;75,0;10,0\n"
    )

    parsed = parse_vna_csv(text)

    assert [point.frequency_hz for point in parsed.points] == [7_000_000.0, 7_100_000.0]
    assert parsed.points[1].impedance_ohm == pytest.approx(complex(75.0, 10.0))
    assert parsed.profile == "NanoVNA Saver"
    assert "R (Ω)" in parsed.mapping


def test_parse_number_handles_locale_and_units() -> None:
    assert parse_number("7,1") == pytest.approx(7.1)
    assert parse_number("7.100,5") == pytest.approx(7100.5)
    assert parse_number("7,100.5") == pytest.approx(7100.5)
    assert parse_number("7.1 MHz") == pytest.approx(7.1)


def test_explicit_mapping_and_mapping_metadata() -> None:
    text = "frequency_mhz,real,imag\n7.1,0.2,0.1\n"
    mapping = VnaColumnMapping(
        frequency="frequency_mhz",
        mode="complex",
        first="real",
        second="imag",
    )

    parsed = parse_vna_csv(text, mapping=mapping)

    assert parsed.points[0].frequency_hz == pytest.approx(7_100_000.0)
    assert "mode=complex" in parsed.mapping


def test_malformed_row_is_rejected_with_row_context() -> None:
    with pytest.raises(VnaCsvError, match="row 2"):
        parse_vna_csv("frequency_hz,r_ohm,x_ohm\n7100000,not-a-number,0\n")


def test_huge_row_count_is_rejected_before_parsing() -> None:
    text = "frequency_hz,r_ohm,x_ohm\n" + "7100000,50,0\n" * (MAX_VNA_ROWS + 1)
    with pytest.raises(VnaCsvError, match="too many rows"):
        parse_vna_csv(text)


def test_mixed_frequency_units_in_rows_are_scaled_individually() -> None:
    parsed = parse_vna_csv("frequency,r_ohm,x_ohm\n7.1MHz,50,0\n7100kHz,50,0\n7100000Hz,50,0\n")

    assert [point.frequency_hz for point in parsed.points] == pytest.approx(
        [7_100_000.0, 7_100_000.0, 7_100_000.0]
    )


def test_rejects_unsupported_headers() -> None:
    with pytest.raises(VnaCsvError, match="supported"):
        parse_vna_csv("frequency_hz,foo\n7100000,1\n")
