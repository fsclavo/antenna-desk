# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.folded_dipole import (
    DRIVEN_WIRE_ID,
    FoldedDipoleParameters,
)
from antennadesk.domain.environment.ground import GroundModel


def _parameters(**overrides: object) -> FoldedDipoleParameters:
    values: dict[str, object] = {
        "frequency_hz": 7_100_000.0,
        "total_length_m": 20.0,
        "height_m": 8.0,
        "spacing_m": 0.2,
        "azimuth_deg": 0.0,
        "wire_radius_m": 0.001,
    }
    values.update(overrides)
    return FoldedDipoleParameters(**values)  # type: ignore[arg-type]


def test_folded_dipole_generates_two_elements_and_end_connectors() -> None:
    antenna = _parameters().to_antenna()

    assert [wire.id for wire in antenna.wires] == [
        "folded-1",
        "folded-2",
        "end-start",
        "end-end",
    ]
    assert len(antenna.wires) == 4
    assert antenna.feed.wire_id == DRIVEN_WIRE_ID
    assert antenna.feed.offset_m == pytest.approx(10.0)
    assert antenna.design_frequency_hz == pytest.approx(7_100_000.0)


def test_folded_dipole_has_parallel_elements_and_short_connectors() -> None:
    antenna = _parameters().to_antenna()
    driven, other, start_connector, end_connector = antenna.wires

    assert driven.length_m == pytest.approx(20.0)
    assert other.length_m == pytest.approx(20.0)
    assert start_connector.length_m == pytest.approx(0.2)
    assert end_connector.length_m == pytest.approx(0.2)
    assert driven.start.z_m == pytest.approx(8.0)
    assert driven.end.z_m == pytest.approx(8.0)
    assert driven.start.y_m == pytest.approx(0.1)
    assert other.start.y_m == pytest.approx(-0.1)


def test_folded_dipole_total_conductor_length() -> None:
    parameters = _parameters()

    assert parameters.total_conductor_length_m == pytest.approx(40.4)


def test_folded_dipole_azimuth_rotates_the_elements() -> None:
    wire = _parameters(azimuth_deg=90.0).to_antenna().wires[0]

    assert wire.start.x_m == pytest.approx(-0.1)
    assert wire.start.y_m == pytest.approx(-10.0)
    assert wire.end.x_m == pytest.approx(-0.1)
    assert wire.end.y_m == pytest.approx(10.0)


def test_folded_dipole_preserves_ground() -> None:
    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    antenna = _parameters(ground=ground).to_antenna()

    assert antenna.environment.ground == ground


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("frequency_hz", 0.0),
        ("total_length_m", 0.0),
        ("height_m", -1.0),
        ("spacing_m", 0.0),
        ("wire_radius_m", 0.0),
        ("frequency_hz", math.nan),
    ],
)
def test_folded_dipole_rejects_invalid_parameters(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        _parameters(**{field: value})
