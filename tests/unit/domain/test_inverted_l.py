# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.family import AntennaFamily, antenna_family
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.design.estimators import supports_estimation


def _parameters(**overrides: object) -> InvertedLParameters:
    values: dict[str, object] = {
        "frequency_hz": 7_100_000.0,
        "vertical_height_m": 10.0,
        "horizontal_length_m": 20.0,
        "base_height_m": 1.0,
        "azimuth_deg": 0.0,
        "wire_radius_m": 0.001,
    }
    values.update(overrides)
    return InvertedLParameters(**values)  # type: ignore[arg-type]


def test_inverted_l_generates_a_vertical_and_horizontal_wire() -> None:
    parameters = _parameters()
    antenna = parameters.to_antenna()

    assert len(antenna.wires) == 2
    vertical, horizontal = antenna.wires
    assert vertical.id == "vertical"
    assert horizontal.id == "horizontal"
    assert vertical.start == horizontal.start or vertical.end == horizontal.start
    assert vertical.start.z_m == pytest.approx(1.0)
    assert vertical.end.z_m == pytest.approx(11.0)
    assert horizontal.end.z_m == pytest.approx(11.0)
    assert horizontal.length_m == pytest.approx(20.0)
    assert parameters.total_length_m == pytest.approx(30.0)
    assert parameters.top_height_m == pytest.approx(11.0)
    assert antenna.feed.wire_id == "vertical"
    assert antenna.feed.offset_m == 0.0


def test_inverted_l_azimuth_rotates_the_horizontal_run() -> None:
    parameters = _parameters(azimuth_deg=90.0)
    horizontal = parameters.to_antenna().wires[1]

    assert horizontal.start.x_m == pytest.approx(0.0)
    assert horizontal.end.x_m == pytest.approx(0.0)
    assert horizontal.end.y_m == pytest.approx(20.0)


def test_inverted_l_rejects_invalid_dimensions() -> None:
    for field, value in (
        ("frequency_hz", 0.0),
        ("vertical_height_m", 0.0),
        ("horizontal_length_m", 0.0),
        ("base_height_m", -1.0),
        ("wire_radius_m", 0.0),
    ):
        with pytest.raises(ValueError):
            _parameters(**{field: value})


def test_inverted_l_belongs_to_the_vertical_family() -> None:
    assert antenna_family(_parameters()) is AntennaFamily.VERTICAL


def test_inverted_l_has_no_frequency_first_estimator() -> None:
    assert not supports_estimation(_parameters())


def test_inverted_l_round_trips_through_custom_parameters() -> None:
    parameters = _parameters(azimuth_deg=35.0)
    custom = parameters.to_custom_parameters()

    restored = InvertedLParameters.from_custom_parameters(custom)

    assert restored.vertical_height_m == pytest.approx(parameters.vertical_height_m)
    assert restored.horizontal_length_m == pytest.approx(parameters.horizontal_length_m)
    assert restored.base_height_m == pytest.approx(parameters.base_height_m)
    assert restored.azimuth_deg == pytest.approx(parameters.azimuth_deg)
    assert restored.wire_radius_m == pytest.approx(parameters.wire_radius_m)
    assert restored.material == parameters.material
    assert restored.ground == parameters.ground


def test_inverted_l_from_custom_parameters_rejects_other_geometry() -> None:
    parameters = _parameters()
    custom = parameters.to_custom_parameters()

    with pytest.raises(ValueError):
        InvertedLParameters.from_custom_parameters(
            custom.__class__(
                frequency_hz=custom.frequency_hz,
                wires=custom.wires[:1],
                feed=custom.feed,
                ground=custom.ground,
            )
        )
