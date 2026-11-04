# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.zepp import (
    ZEPP_LINE_ID,
    ZEPP_RADIATOR_ID,
    ZEPP_SOURCE_ID,
    zepp_parameters,
    zepp_starting_dimensions,
)


def test_zepp_uses_a_half_wave_radiator_and_quarter_wave_line() -> None:
    parameters = zepp_parameters()
    radiator_m, line_m = zepp_starting_dimensions(7_100_000.0)

    assert parameters.generator_id == "zepp"
    assert parameters.generator_name == "Zepp"
    assert {wire.id for wire in parameters.wires} == {
        ZEPP_SOURCE_ID,
        ZEPP_RADIATOR_ID,
    }
    radiator = next(wire for wire in parameters.wires if wire.id == ZEPP_RADIATOR_ID)
    assert radiator.length_m == pytest.approx(radiator_m)
    line = parameters.transmission_lines[0]
    assert line.id == ZEPP_LINE_ID
    assert line.length_m == pytest.approx(line_m)
    assert line.characteristic_impedance_ohm == pytest.approx(400.0)


def test_zepp_accepts_manual_radiator_and_line_lengths() -> None:
    parameters = zepp_parameters(
        radiator_length_m=10.0,
        matching_line_length_m=2.5,
        matching_line_impedance_ohm=450.0,
    )

    radiator = next(wire for wire in parameters.wires if wire.id == ZEPP_RADIATOR_ID)
    line = parameters.transmission_lines[0]
    assert radiator.length_m == pytest.approx(10.0)
    assert line.length_m == pytest.approx(2.5)
    assert line.characteristic_impedance_ohm == pytest.approx(450.0)
