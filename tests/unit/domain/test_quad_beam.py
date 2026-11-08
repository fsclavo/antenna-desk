# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    with_primary_dimension,
)
from antennadesk.domain.antennas.family import (
    AntennaFamily,
    antenna_family,
    antenna_template_id,
)
from antennadesk.domain.antennas.quad_beam import (
    QuadBeamParameters,
    quad_beam_parameters,
)


def test_quad_beam_builds_a_reflector_and_driven_loop() -> None:
    parameters = quad_beam_parameters(
        frequency_hz=14_100_000.0,
        element_count=2,
        loop_side_m=5.0,
        reflector_spacing_m=4.0,
        height_m=2.5,
    )

    model = parameters.to_antenna()

    assert parameters.template_name == "Quad beam"
    assert len(model.wires) == 8
    assert parameters.boom_length_m == pytest.approx(4.0)
    assert parameters.reflector_side_m == pytest.approx(5.25)
    assert parameters.director_side_m == pytest.approx(4.75)
    assert parameters.total_conductor_length_m == pytest.approx(4 * 5.25 + 4 * 5.0)
    assert model.feed.wire_id == "quad-beam-element-1-side-3"
    assert model.feed.offset_m == pytest.approx(2.5)
    assert parameters.feed_height_m == pytest.approx(5.0)
    driven = tuple(wire for wire in model.wires if wire.id.startswith("quad-beam-element-1-"))
    assert len(driven) == 4
    assert sorted(wire.start.z_m for wire in driven) == pytest.approx([2.5, 2.5, 7.5, 7.5])


def test_quad_beam_adds_a_director_and_boom() -> None:
    parameters = quad_beam_parameters(
        element_count=3,
        loop_side_m=5.0,
        reflector_spacing_m=4.0,
        director_spacing_m=3.0,
    )

    model = parameters.to_antenna()

    assert len(model.wires) == 12
    assert parameters.element_positions_m == pytest.approx((0.0, 4.0, 7.0))
    assert parameters.boom_length_m == pytest.approx(7.0)
    director = tuple(wire for wire in model.wires if wire.id.startswith("quad-beam-element-2-"))
    assert len(director) == 4
    assert parameters.total_conductor_length_m == pytest.approx(4 * 5.25 + 4 * 5.0 + 4 * 4.75)


def test_quad_beam_rotates_the_boom_with_azimuth() -> None:
    parameters = quad_beam_parameters(
        element_count=2,
        loop_side_m=5.0,
        reflector_spacing_m=4.0,
        azimuth_deg=90.0,
    )

    wires = parameters.to_antenna().wires
    reflector = tuple(wire for wire in wires if wire.id.startswith("quad-beam-element-0-"))
    driven = tuple(wire for wire in wires if wire.id.startswith("quad-beam-element-1-"))

    assert sorted(wire.start.x_m for wire in reflector) == pytest.approx(
        [-2.625, -2.625, 2.625, 2.625]
    )
    assert sorted(wire.start.x_m for wire in driven) == pytest.approx([-2.5, -2.5, 2.5, 2.5])
    assert sorted(wire.start.y_m for wire in reflector) == pytest.approx([0.0] * 4)
    assert sorted(wire.start.y_m for wire in driven) == pytest.approx([4.0] * 4)


def test_quad_beam_primary_dimension_scales_the_boom() -> None:
    parameters = quad_beam_parameters(
        element_count=3,
        loop_side_m=5.0,
        reflector_spacing_m=4.0,
        director_spacing_m=3.0,
    )

    assert primary_dimension_m(parameters) == pytest.approx(5.0)

    scaled = with_primary_dimension(parameters, 6.0)

    assert isinstance(scaled, QuadBeamParameters)
    assert scaled.loop_side_m == pytest.approx(6.0)
    assert scaled.reflector_spacing_m == pytest.approx(4.8)
    assert scaled.director_spacing_m == pytest.approx(3.6)
    assert antenna_type_for(scaled) == "quad_beam"
    assert antenna_template_id(scaled) == "quad_beam"
    assert antenna_family(scaled) is AntennaFamily.LOOP


def test_quad_beam_rejects_invalid_scales_and_spacing() -> None:
    with pytest.raises(ValueError, match="reflector_scale"):
        quad_beam_parameters(reflector_scale=0.95)
    with pytest.raises(ValueError, match="director_scale"):
        quad_beam_parameters(director_scale=1.05)
    with pytest.raises(ValueError, match="director_spacing_m"):
        quad_beam_parameters(element_count=3, director_spacing_m=0.0)
    with pytest.raises(ValueError, match="reflector spacing"):
        quad_beam_parameters(reflector_spacing_m=0.001, wire_radius_m=0.001)


def test_quad_beam_normalizes_azimuth() -> None:
    parameters = quad_beam_parameters(azimuth_deg=-90.0)

    assert parameters.azimuth_deg == pytest.approx(270.0)
