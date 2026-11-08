# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.beverage import (
    BEVERAGE_TERMINATION_LOAD_ID,
    BEVERAGE_TERMINATION_WIRE_ID,
    BEVERAGE_WIRE_ID,
    BeverageParameters,
    beverage_parameters,
)
from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    template_load_ids,
    with_primary_dimension,
)
from antennadesk.domain.antennas.family import (
    AntennaFamily,
    antenna_family,
    antenna_template_id,
)


def test_beverage_builds_a_terminated_long_wire() -> None:
    parameters = beverage_parameters(
        frequency_hz=7_100_000.0,
        length_m=42.0,
        height_m=3.0,
        termination_resistance_ohm=470.0,
    )
    model = parameters.to_antenna()

    assert parameters.template_name == "Beverage"
    assert len(model.wires) == 2
    assert model.feed.wire_id == BEVERAGE_WIRE_ID
    assert model.feed.offset_m == 0.0
    assert len(model.loads) == 1
    load = model.loads[0]
    assert load.id == BEVERAGE_TERMINATION_LOAD_ID
    assert load.wire_id == BEVERAGE_TERMINATION_WIRE_ID
    assert load.resistance_ohm == pytest.approx(470.0)
    assert load.offset_m == pytest.approx(parameters.height_m / 2.0)
    assert parameters.total_conductor_length_m == pytest.approx(45.0)
    assert parameters.managed_load_ids == frozenset({BEVERAGE_TERMINATION_LOAD_ID})
    assert template_load_ids(parameters) == parameters.managed_load_ids
    assert antenna_type_for(parameters) == "beverage"
    assert antenna_template_id(parameters) == "beverage"
    assert antenna_family(parameters) is AntennaFamily.WIRE


def test_beverage_without_termination_has_one_wire_and_no_load() -> None:
    parameters = beverage_parameters(termination_enabled=False)
    model = parameters.to_antenna()

    assert len(model.wires) == 1
    assert model.loads == ()
    assert parameters.managed_load_ids == frozenset()
    assert parameters.total_conductor_length_m == pytest.approx(parameters.length_m)


def test_beverage_starting_length_is_one_wavelength() -> None:
    from antennadesk.domain.design.formulas import wavelength_m

    parameters = beverage_parameters(frequency_hz=3_500_000.0)

    assert parameters.length_m == pytest.approx(wavelength_m(3_500_000.0))
    assert parameters.height_m == pytest.approx(3.0)
    assert parameters.termination_resistance_ohm == pytest.approx(500.0)


def test_beverage_primary_dimension_is_the_wire_length() -> None:
    parameters = beverage_parameters(length_m=40.0)
    scaled = with_primary_dimension(parameters, 60.0)

    assert isinstance(scaled, BeverageParameters)
    assert primary_dimension_m(parameters) == pytest.approx(40.0)
    assert primary_dimension_m(scaled) == pytest.approx(60.0)


def test_beverage_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="height_m"):
        BeverageParameters(
            frequency_hz=7_100_000.0,
            length_m=40.0,
            height_m=0.0,
        )
    with pytest.raises(ValueError, match="termination_resistance_ohm"):
        BeverageParameters(
            frequency_hz=7_100_000.0,
            length_m=40.0,
            termination_resistance_ohm=0.0,
        )


def test_beverage_rotates_the_wire_with_azimuth() -> None:
    parameters = beverage_parameters(
        frequency_hz=7_100_000.0,
        length_m=10.0,
        azimuth_deg=90.0,
    )
    model = parameters.to_antenna()

    wire = next(item for item in model.wires if item.id == BEVERAGE_WIRE_ID)
    assert wire.start.x_m == pytest.approx(0.0)
    assert wire.end.x_m == pytest.approx(0.0, abs=1e-9)
    assert wire.end.y_m == pytest.approx(10.0)
