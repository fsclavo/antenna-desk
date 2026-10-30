# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.importers.vna_csv import VnaCsvError, parse_vna_csv


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


def test_rejects_unsupported_headers() -> None:
    with pytest.raises(VnaCsvError, match="supported"):
        parse_vna_csv("frequency_hz,foo\n7100000,1\n")
