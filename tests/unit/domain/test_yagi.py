# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters, nbs_five_element
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.spec import SimulationSpec


def test_nbs_preset_has_the_published_element_positions() -> None:
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=0.0)

    wavelength = 299_792_458.0 / 50_100_000.0
    assert len(yagi.elements) == 5
    assert yagi.driven_index == 1
    assert [element.position_m for element in yagi.elements] == pytest.approx(
        [0.0, 0.2 * wavelength, 0.4 * wavelength, 0.6 * wavelength, 0.8 * wavelength]
    )
    assert yagi.elements[1].length_m == pytest.approx(0.5 * wavelength)


def test_yagi_generates_parallel_wires_and_center_feed() -> None:
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0)
    parameters = yagi.to_custom_parameters()

    assert len(parameters.wires) == 5
    assert all(wire.start.z_m == 8.0 and wire.end.z_m == 8.0 for wire in parameters.wires)
    assert parameters.feed.wire_id == "element-2"
    assert parameters.feed.offset_m == pytest.approx(parameters.wires[1].length_m / 2.0)
    assert parameters.wires[0].start.x_m == pytest.approx(0.0)
    assert parameters.wires[1].start.x_m > parameters.wires[0].start.x_m


def test_yagi_azimuth_rotates_the_boom() -> None:
    yagi = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=0.0,
        azimuth_deg=90.0,
    )
    parameters = yagi.to_custom_parameters()
    driven = parameters.wires[1]

    assert driven.start.y_m == pytest.approx(driven.end.y_m)
    assert driven.start.y_m > 0.0
    assert driven.start.x_m == pytest.approx(-driven.end.x_m)
    assert driven.start.z_m == 0.0


def test_elements_are_sorted_and_must_be_distinct() -> None:
    yagi = YagiParameters(
        frequency_hz=50_100_000.0,
        elements=(
            YagiElement(1.0, 10.0, 0.001),
            YagiElement(0.0, 10.5, 0.001),
            YagiElement(2.0, 9.5, 0.001),
        ),
        height_m=0.0,
        driven_index=0,
    )

    assert [element.position_m for element in yagi.elements] == [0.0, 1.0, 2.0]
    with pytest.raises(ValueError, match="distinct"):
        YagiParameters(
            frequency_hz=50_100_000.0,
            elements=(
                YagiElement(0.0, 10.0, 0.001),
                YagiElement(0.0, 9.0, 0.001),
            ),
            height_m=0.0,
        )


def test_yagi_requires_two_elements_and_a_valid_driven_index() -> None:
    with pytest.raises(ValueError, match="at least"):
        YagiParameters(
            frequency_hz=50_100_000.0,
            elements=(YagiElement(0.0, 10.0, 0.001),),
            height_m=0.0,
        )
    with pytest.raises(ValueError, match="driven_index"):
        YagiParameters(
            frequency_hz=50_100_000.0,
            elements=(
                YagiElement(0.0, 10.0, 0.001),
                YagiElement(1.0, 9.0, 0.001),
            ),
            height_m=0.0,
            driven_index=2,
        )


def test_yagi_preset_is_finite_and_simulatable() -> None:
    yagi = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=0.0,
        ground=GroundModel.free_space(),
    )
    parameters = yagi.to_custom_parameters()
    model = parameters.to_antenna(name="Yagi")

    assert model.design_frequency_hz == pytest.approx(50_100_000.0)
    assert math.isfinite(model.wires[0].length_m)
    assert (
        SimulationSpec(frequency_plan=FrequencyPlan.single(50_100_000.0)).frequency_plan.count == 1
    )
