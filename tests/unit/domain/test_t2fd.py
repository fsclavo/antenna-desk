# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    with_primary_dimension,
)
from antennadesk.domain.antennas.dipole import DipoleOrientation
from antennadesk.domain.antennas.family import (
    AntennaFamily,
    antenna_family,
    antenna_template_id,
)
from antennadesk.domain.antennas.load import SeriesLoad
from antennadesk.domain.antennas.t2fd import (
    T2FD_DRIVEN_WIRE_ID,
    T2FD_END_CONNECTOR_ID,
    T2FD_START_CONNECTOR_ID,
    T2FD_TERMINATED_WIRE_ID,
    T2FD_TERMINATION_LOAD_ID,
    T2FDParameters,
    t2fd_starting_dimensions,
)


def _parameters(**overrides: object) -> T2FDParameters:
    values: dict[str, object] = {
        "frequency_hz": 3_500_000.0,
        "highest_frequency_hz": 30_000_000.0,
        "length_m": 26.0,
        "spacing_m": 0.9,
        "height_m": 10.0,
    }
    values.update(overrides)
    return T2FDParameters(**values)


def test_t2fd_builds_a_folded_loop_with_a_series_termination() -> None:
    parameters = _parameters()

    custom = parameters.to_custom_parameters()
    antenna = parameters.to_antenna(name="T2FD")

    assert len(custom.wires) == 4
    assert [wire.id for wire in custom.wires] == [
        T2FD_DRIVEN_WIRE_ID,
        T2FD_TERMINATED_WIRE_ID,
        T2FD_START_CONNECTOR_ID,
        T2FD_END_CONNECTOR_ID,
    ]
    assert custom.wires[0].length_m == pytest.approx(26.0)
    assert custom.wires[1].length_m == pytest.approx(26.0)
    assert custom.wires[2].length_m == pytest.approx(0.9)
    assert custom.wires[3].length_m == pytest.approx(0.9)
    assert custom.feed.wire_id == T2FD_DRIVEN_WIRE_ID
    assert custom.feed.offset_m == pytest.approx(13.0)
    assert len(custom.loads) == 1
    load = custom.loads[0]
    assert isinstance(load, SeriesLoad)
    assert load.id == T2FD_TERMINATION_LOAD_ID
    assert load.wire_id == T2FD_TERMINATED_WIRE_ID
    assert load.offset_m == pytest.approx(13.0)
    assert load.resistance_ohm == pytest.approx(800.0)
    assert load.inductance_h == pytest.approx(0.0)
    assert load.capacitance_f == pytest.approx(0.0)
    assert custom.generator_id == "t2fd"
    assert antenna == custom.to_antenna(name="T2FD")
    assert parameters.managed_load_ids == frozenset({T2FD_TERMINATION_LOAD_ID})
    assert parameters.total_conductor_length_m == pytest.approx(2 * 26.0 + 2 * 0.9)


def test_t2fd_horizontal_geometry_uses_the_requested_azimuth() -> None:
    parameters = _parameters(length_m=10.0, spacing_m=1.0, azimuth_deg=90.0)

    antenna = parameters.to_antenna()
    driven = antenna.wire_by_id(T2FD_DRIVEN_WIRE_ID)
    terminated = antenna.wire_by_id(T2FD_TERMINATED_WIRE_ID)

    assert driven.start.x_m == pytest.approx(-0.5)
    assert driven.start.y_m == pytest.approx(-5.0)
    assert driven.end.x_m == pytest.approx(-0.5)
    assert driven.end.y_m == pytest.approx(5.0)
    assert terminated.start.x_m == pytest.approx(0.5)
    assert terminated.start.y_m == pytest.approx(-5.0)
    assert driven.start.z_m == pytest.approx(10.0)
    assert driven.end.z_m == pytest.approx(10.0)


def test_t2fd_vertical_geometry_spans_the_requested_height_and_spacing() -> None:
    parameters = _parameters(
        length_m=10.0,
        spacing_m=1.0,
        height_m=2.0,
        orientation=DipoleOrientation.VERTICAL,
    )

    antenna = parameters.to_antenna()
    driven = antenna.wire_by_id(T2FD_DRIVEN_WIRE_ID)
    terminated = antenna.wire_by_id(T2FD_TERMINATED_WIRE_ID)

    assert driven.start.z_m == pytest.approx(2.0)
    assert driven.end.z_m == pytest.approx(12.0)
    assert driven.start.y_m == pytest.approx(0.5)
    assert terminated.start.y_m == pytest.approx(-0.5)
    assert driven.start.x_m == pytest.approx(terminated.start.x_m)
    assert antenna.feed.offset_m == pytest.approx(5.0)
    assert antenna.loads[0].offset_m == pytest.approx(5.0)


def test_t2fd_starting_dimensions_follow_the_wide_long_reference() -> None:
    span_m, spacing_m = t2fd_starting_dimensions(3_500_000.0)

    assert span_m == pytest.approx(300.0 * 0.3048 / 3.5)
    assert spacing_m == pytest.approx(10.0 * 0.3048 / 3.5)
    assert span_m / spacing_m == pytest.approx(30.0)
    with pytest.raises(ValueError, match="frequency_hz"):
        t2fd_starting_dimensions(0.0)


def test_t2fd_rejects_invalid_band_and_geometry_values() -> None:
    with pytest.raises(ValueError, match="highest_frequency_hz"):
        _parameters(highest_frequency_hz=3_500_000.0)
    with pytest.raises(ValueError, match="length_m"):
        _parameters(length_m=0.0)
    with pytest.raises(ValueError, match="spacing_m"):
        _parameters(spacing_m=0.0)
    with pytest.raises(ValueError, match="termination_resistance_ohm"):
        _parameters(termination_resistance_ohm=0.0)
    with pytest.raises(ValueError, match="transformer_ratio"):
        _parameters(transformer_ratio=0.0)
    with pytest.raises(ValueError):
        _parameters(orientation="diagonal")


def test_t2fd_maps_to_the_dipole_family_and_primary_dimension() -> None:
    parameters = _parameters()

    assert antenna_family(parameters) is AntennaFamily.DIPOLE
    assert antenna_template_id(parameters) == "t2fd"
    assert antenna_type_for(parameters) == "t2fd"
    assert primary_dimension_m(parameters) == pytest.approx(26.0)

    resized = with_primary_dimension(parameters, 30.0)
    assert isinstance(resized, T2FDParameters)
    assert resized.length_m == pytest.approx(30.0)
    assert resized.spacing_m == pytest.approx(0.9)


def test_t2fd_azimuth_is_normalized_and_length_helper_preserves_the_rest() -> None:
    parameters = _parameters(azimuth_deg=450.0)

    assert parameters.azimuth_deg == pytest.approx(90.0)
    resized = parameters.with_length(24.0)
    assert resized.length_m == pytest.approx(24.0)
    assert resized.termination_resistance_ohm == pytest.approx(800.0)
    with pytest.raises(ValueError, match="length_m"):
        parameters.with_length(0.0)
    assert math.isfinite(parameters.total_conductor_length_m)
