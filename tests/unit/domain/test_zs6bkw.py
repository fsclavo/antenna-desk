# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.zs6bkw import (
    ZS6BKW_DIPOLE_ID,
    ZS6BKW_LINE_ID,
    ZS6BKW_SOURCE_ID,
    ZS6BKW_VARIANTS,
    zs6bkw_parameters,
    zs6bkw_with_dimensions,
)


def test_zs6bkw_uses_the_reference_wire_and_matching_line() -> None:
    parameters = zs6bkw_parameters()

    assert parameters.generator_id == "zs6bkw"
    assert parameters.generator_name == "ZS6BKW"
    assert {wire.id for wire in parameters.wires} == {
        ZS6BKW_SOURCE_ID,
        ZS6BKW_DIPOLE_ID,
    }
    dipole = next(wire for wire in parameters.wires if wire.id == ZS6BKW_DIPOLE_ID)
    assert dipole.length_m == pytest.approx(28.4)
    assert len(parameters.transmission_lines) == 1
    line = parameters.transmission_lines[0]
    assert line.id == ZS6BKW_LINE_ID
    assert line.characteristic_impedance_ohm == pytest.approx(400.0)
    assert line.length_m == pytest.approx(13.6)


def test_zs6bkw_has_a_documented_commercial_variant() -> None:
    parameters = zs6bkw_parameters(variant=ZS6BKW_VARIANTS[1])

    dipole = next(wire for wire in parameters.wires if wire.id == ZS6BKW_DIPOLE_ID)
    line = parameters.transmission_lines[0]

    assert dipole.length_m == pytest.approx(27.5)
    assert line.characteristic_impedance_ohm == pytest.approx(450.0)
    assert line.length_m == pytest.approx(12.2)


def test_zs6bkw_can_be_rebuilt_with_optimized_dimensions() -> None:
    parameters = zs6bkw_parameters(azimuth_deg=30.0, line_velocity_factor=0.9)
    updated = zs6bkw_with_dimensions(
        parameters,
        dipole_total_length_m=29.0,
        line_length_m=14.0,
    )

    dipole = next(wire for wire in updated.wires if wire.id == ZS6BKW_DIPOLE_ID)
    line = updated.transmission_lines[0]
    assert dipole.length_m == pytest.approx(29.0)
    assert dipole.start.z_m == pytest.approx(10.0)
    assert line.length_m == pytest.approx(14.0)
    assert line.characteristic_impedance_ohm == pytest.approx(400.0)
    assert line.velocity_factor == pytest.approx(0.9)
    assert updated.frequency_hz == pytest.approx(parameters.frequency_hz)


def test_zs6bkw_rejects_an_invalid_velocity_factor() -> None:
    with pytest.raises(ValueError, match="velocity_factor"):
        zs6bkw_parameters(line_velocity_factor=1.1)
