# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.transmission_line import (
    TransmissionLine,
    mismatched_line_loss_db,
)


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


def test_mismatched_line_loss_adds_the_load_mismatch() -> None:
    total = mismatched_line_loss_db(
        length_m=100.0,
        loss_db_per_100m=1.0,
        characteristic_impedance_ohm=50.0,
        load_impedance_ohm=150.0 + 0.0j,
    )

    assert total == pytest.approx(1.504, abs=0.002)


def test_mismatched_line_loss_keeps_the_matched_case() -> None:
    total = mismatched_line_loss_db(
        length_m=100.0,
        loss_db_per_100m=1.0,
        characteristic_impedance_ohm=50.0,
        load_impedance_ohm=50.0 + 0.0j,
    )

    assert total == pytest.approx(1.0)


def test_mismatched_line_loss_is_zero_for_a_lossless_line() -> None:
    total = mismatched_line_loss_db(
        length_m=100.0,
        loss_db_per_100m=0.0,
        characteristic_impedance_ohm=50.0,
        load_impedance_ohm=150.0 + 0.0j,
    )

    assert total == 0.0


def test_mismatched_line_loss_falls_back_for_a_singular_load() -> None:
    total = mismatched_line_loss_db(
        length_m=100.0,
        loss_db_per_100m=1.0,
        characteristic_impedance_ohm=50.0,
        load_impedance_ohm=-50.0 + 0.0j,
    )

    assert total == pytest.approx(1.0)
