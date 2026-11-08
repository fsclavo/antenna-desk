# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

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
from antennadesk.domain.antennas.load import ParallelLoad
from antennadesk.domain.antennas.trap_yagi import (
    TrapYagiParameters,
    trap_yagi_parameters,
)


def test_trap_yagi_builds_elements_and_trap_pairs() -> None:
    parameters = trap_yagi_parameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        element_count=3,
        driven_length_m=20.0,
        reflector_spacing_m=4.0,
        director_spacing_m=4.0,
        trap_inset_m=3.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=5e-6,
        height_m=10.0,
    )

    model = parameters.to_antenna()

    assert parameters.template_name == "Trapped Yagi"
    assert len(model.wires) == 3
    assert len(model.loads) == 6
    assert model.feed.wire_id == "trap-yagi-element-1"
    assert model.feed.offset_m == pytest.approx(10.0)
    assert parameters.boom_length_m == pytest.approx(8.0)
    assert parameters.reflector_length_m == pytest.approx(21.0)
    assert parameters.director_length_m == pytest.approx(19.0)
    assert parameters.total_conductor_length_m == pytest.approx(60.0)
    assert parameters.managed_load_ids == frozenset(
        {
            "trap-yagi-load-0-left",
            "trap-yagi-load-0-right",
            "trap-yagi-load-1-left",
            "trap-yagi-load-1-right",
            "trap-yagi-load-2-left",
            "trap-yagi-load-2-right",
        }
    )
    assert template_load_ids(parameters) == parameters.managed_load_ids


def test_trap_yagi_places_parallel_traps_symmetrically() -> None:
    parameters = trap_yagi_parameters(
        element_count=2,
        driven_length_m=20.0,
        reflector_spacing_m=4.0,
        trap_inset_m=3.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=5e-6,
        reflector_scale=1.0,
    )

    model = parameters.to_antenna()
    loads = {load.id: load for load in model.loads if isinstance(load, ParallelLoad)}

    driven_left = loads["trap-yagi-load-1-left"]
    driven_right = loads["trap-yagi-load-1-right"]
    assert driven_left.offset_m == pytest.approx(7.0)
    assert driven_right.offset_m == pytest.approx(13.0)
    assert driven_left.inductance_h == pytest.approx(5e-6)
    assert driven_left.capacitance_f == pytest.approx(
        1.0 / ((2.0 * math.pi * 14_100_000.0) ** 2 * 5e-6)
    )


def test_trap_yagi_primary_dimension_scales_the_boom() -> None:
    parameters = trap_yagi_parameters(
        driven_length_m=20.0,
        reflector_spacing_m=4.0,
        director_spacing_m=3.0,
        trap_inset_m=3.0,
        height_m=10.0,
    )

    assert primary_dimension_m(parameters) == pytest.approx(20.0)

    scaled = with_primary_dimension(parameters, 22.0)

    assert isinstance(scaled, TrapYagiParameters)
    assert scaled.driven_length_m == pytest.approx(22.0)
    assert scaled.reflector_spacing_m == pytest.approx(4.4)
    assert scaled.director_spacing_m == pytest.approx(3.3)
    assert scaled.trap_inset_m == pytest.approx(3.3)
    assert scaled.height_m == pytest.approx(11.0)
    assert antenna_type_for(scaled) == "trap_yagi"
    assert antenna_template_id(scaled) == "trap_yagi"
    assert antenna_family(scaled) is AntennaFamily.YAGI


def test_trap_yagi_rejects_invalid_traps_and_bands() -> None:
    with pytest.raises(ValueError, match="high_band_frequency_hz"):
        trap_yagi_parameters(
            frequency_hz=14_100_000.0,
            high_band_frequency_hz=7_100_000.0,
        )
    with pytest.raises(ValueError, match="half of every element"):
        trap_yagi_parameters(
            driven_length_m=10.0,
            reflector_scale=1.0,
            trap_inset_m=5.0,
        )
    with pytest.raises(ValueError, match="conductor diameter"):
        trap_yagi_parameters(trap_inset_m=0.001, wire_radius_m=0.001)


def test_trap_yagi_normalizes_azimuth() -> None:
    parameters = trap_yagi_parameters(azimuth_deg=-90.0)

    assert parameters.azimuth_deg == pytest.approx(270.0)
