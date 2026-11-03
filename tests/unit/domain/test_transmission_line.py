# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.transmission_line import TransmissionLine


def _line(**overrides: object) -> TransmissionLine:
    values: dict[str, object] = {
        "id": "line-1",
        "start_wire_id": "radiator",
        "start_offset_m": 0.0,
        "end_wire_id": "counterpoise",
        "end_offset_m": 2.0,
        "characteristic_impedance_ohm": 300.0,
        "length_m": 10.0,
        "velocity_factor": 0.9,
    }
    values.update(overrides)
    return TransmissionLine(**values)


def test_transmission_line_converts_physical_to_electrical_length() -> None:
    line = _line()

    assert line.electrical_length_m == pytest.approx(10.0 / 0.9)


def test_transmission_line_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="id"):
        _line(id=" ")
    with pytest.raises(ValueError, match="start_wire_id"):
        _line(start_wire_id=" ")
    with pytest.raises(ValueError, match="characteristic_impedance_ohm"):
        _line(characteristic_impedance_ohm=0.0)
    with pytest.raises(ValueError, match="length_m"):
        _line(length_m=0.0)
    with pytest.raises(ValueError, match="velocity_factor"):
        _line(velocity_factor=0.0)
    with pytest.raises(ValueError, match="velocity_factor"):
        _line(velocity_factor=1.1)
