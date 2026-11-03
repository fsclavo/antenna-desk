# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.g5rv import (
    G5RV_DIPOLE_TOTAL_LENGTH_M,
    g5rv_parameters,
)


def test_g5rv_uses_the_published_dipole_and_matching_line() -> None:
    parameters = g5rv_parameters(
        frequency_hz=14_100_000.0,
        height_m=10.0,
        line_impedance_ohm=450.0,
        line_length_m=10.36,
        line_velocity_factor=0.9,
    )

    assert parameters.generator_id == "g5rv"
    assert parameters.generator_name == "G5RV"
    assert len(parameters.wires) == 2
    assert parameters.wires[1].id == "dipole"
    assert parameters.wires[1].length_m == pytest.approx(G5RV_DIPOLE_TOTAL_LENGTH_M)
    assert len(parameters.transmission_lines) == 1
    line = parameters.transmission_lines[0]
    assert line.characteristic_impedance_ohm == pytest.approx(450.0)
    assert line.length_m == pytest.approx(10.36)
    assert line.velocity_factor == pytest.approx(0.9)
    assert line.electrical_length_m == pytest.approx(10.36 / 0.9)
    assert parameters.feed.wire_id == "source"


def test_g5rv_supports_the_300_ohm_line_and_rejects_bad_velocity_factor() -> None:
    parameters = g5rv_parameters(
        frequency_hz=14_100_000.0,
        line_impedance_ohm=300.0,
        line_length_m=8.84,
    )
    assert parameters.transmission_lines[0].characteristic_impedance_ohm == pytest.approx(300.0)

    with pytest.raises(ValueError, match="line_velocity_factor"):
        g5rv_parameters(
            frequency_hz=14_100_000.0,
            line_velocity_factor=1.1,
        )
