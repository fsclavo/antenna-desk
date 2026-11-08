# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.biquad import (
    ANTENNA_TYPE_BIQUAD,
    ANTENNA_TYPE_DOUBLE_BIQUAD,
    BiquadKind,
    BiquadParameters,
    biquad_parameters,
)
from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    with_primary_dimension,
)
from antennadesk.domain.antennas.family import AntennaFamily, antenna_family, antenna_template_id


@pytest.mark.parametrize(
    ("kind", "loop_count", "antenna_type"),
    [
        (BiquadKind.SINGLE, 2, ANTENNA_TYPE_BIQUAD),
        (BiquadKind.DOUBLE, 4, ANTENNA_TYPE_DOUBLE_BIQUAD),
    ],
)
def test_biquad_builds_the_expected_loop_stack(
    kind: BiquadKind,
    loop_count: int,
    antenna_type: str,
) -> None:
    parameters = biquad_parameters(kind)
    model = parameters.to_antenna()

    assert parameters.loop_count == loop_count
    assert parameters.feed_rail_index == loop_count // 2
    assert parameters.total_height_m == pytest.approx(loop_count * parameters.loop_side_m)
    assert parameters.feed_height_m == pytest.approx(
        parameters.base_height_m + parameters.feed_rail_index * parameters.loop_side_m
    )
    assert len(model.wires) == 3 * loop_count + 5
    assert model.feed.wire_id == f"biquad-rail-{loop_count // 2}"
    assert model.feed.offset_m == pytest.approx(parameters.loop_side_m / 2.0)
    assert antenna_type_for(parameters) == antenna_type
    assert antenna_template_id(parameters) == antenna_type
    assert antenna_family(parameters) is AntennaFamily.LOOP


def test_biquad_starting_side_is_a_quarter_wave_and_spacing_is_half_the_side() -> None:
    from antennadesk.domain.design.formulas import quarter_wave_length_m

    parameters = biquad_parameters(BiquadKind.SINGLE, frequency_hz=14_100_000.0)

    expected_side = quarter_wave_length_m(14_100_000.0)
    assert parameters.loop_side_m == pytest.approx(expected_side)
    assert parameters.reflector_spacing_m == pytest.approx(expected_side / 2.0)


def test_biquad_can_disable_the_reflector() -> None:
    parameters = biquad_parameters(BiquadKind.SINGLE, reflector_enabled=False)
    model = parameters.to_antenna()

    assert len(model.wires) == 3 * parameters.loop_count + 1
    assert all(not wire.id.startswith("biquad-reflector") for wire in model.wires)
    assert parameters.total_conductor_length_m == pytest.approx(
        (3 * parameters.loop_count + 1) * parameters.loop_side_m
    )


def test_biquad_total_conductor_includes_the_reflector_frame() -> None:
    parameters = biquad_parameters(BiquadKind.DOUBLE)

    driven = (3 * parameters.loop_count + 1) * parameters.loop_side_m
    reflector = 2.0 * (parameters.loop_side_m + parameters.total_height_m)
    assert parameters.total_conductor_length_m == pytest.approx(driven + reflector)


def test_biquad_rejects_a_reflector_closer_than_the_wire_diameter() -> None:
    parameters = biquad_parameters(BiquadKind.SINGLE)

    with pytest.raises(ValueError, match="conductor diameter"):
        BiquadParameters(
            frequency_hz=parameters.frequency_hz,
            loop_side_m=parameters.loop_side_m,
            reflector_spacing_m=0.001,
            kind=parameters.kind,
            wire_radius_m=0.002,
        )


def test_biquad_primary_dimension_scales_the_reflector_spacing() -> None:
    parameters = biquad_parameters(BiquadKind.SINGLE)
    ratio = 2.0

    scaled = with_primary_dimension(
        parameters,
        parameters.loop_side_m * ratio,
    )

    assert isinstance(scaled, BiquadParameters)
    assert primary_dimension_m(scaled) == pytest.approx(parameters.loop_side_m * ratio)
    assert scaled.reflector_spacing_m == pytest.approx(parameters.reflector_spacing_m * ratio)


def test_biquad_normalizes_the_kind_and_azimuth() -> None:
    parameters = biquad_parameters(BiquadKind.SINGLE, azimuth_deg=360.0)

    assert parameters.kind is BiquadKind.SINGLE
    assert parameters.azimuth_deg == pytest.approx(0.0)


def test_biquad_rejects_an_unknown_kind() -> None:
    parameters = biquad_parameters(BiquadKind.SINGLE)

    with pytest.raises(ValueError):
        BiquadParameters(
            frequency_hz=parameters.frequency_hz,
            loop_side_m=parameters.loop_side_m,
            reflector_spacing_m=parameters.reflector_spacing_m,
            kind="triple",  # type: ignore[arg-type]
        )
