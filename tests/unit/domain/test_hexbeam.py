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
from antennadesk.domain.antennas.hexbeam import (
    PUBLISHED_DRIVER_HALF_M,
    PUBLISHED_HEXBEAM_FREQUENCY_HZ,
    PUBLISHED_REFLECTOR_HALF_M,
    PUBLISHED_TIP_GAP_M,
    PUBLISHED_TURNING_RADIUS_M,
    HexbeamParameters,
    published_hexbeam_parameters,
)


def test_published_hexbeam_reference_dimensions() -> None:
    parameters = published_hexbeam_parameters()

    assert parameters.template_name == "Hexbeam"
    assert parameters.frequency_hz == pytest.approx(PUBLISHED_HEXBEAM_FREQUENCY_HZ)
    assert parameters.driver_half_length_m == pytest.approx(PUBLISHED_DRIVER_HALF_M)
    assert parameters.reflector_half_length_m == pytest.approx(PUBLISHED_REFLECTOR_HALF_M)
    assert parameters.tip_gap_m == pytest.approx(PUBLISHED_TIP_GAP_M)
    assert parameters.turning_radius_m == pytest.approx(PUBLISHED_TURNING_RADIUS_M)
    assert parameters.driver_tip_half_span_m > parameters.turning_radius_m
    assert parameters.reflector_tip_half_span_m > parameters.turning_radius_m
    assert parameters.overall_span_m == pytest.approx(
        2.0 * max(parameters.driver_tip_half_span_m, parameters.reflector_tip_half_span_m)
    )
    assert parameters.total_conductor_length_m == pytest.approx(
        2.0 * (PUBLISHED_DRIVER_HALF_M + PUBLISHED_REFLECTOR_HALF_M) + parameters.feed_gap_m
    )


def test_hexbeam_builds_a_w_driver_and_u_reflector() -> None:
    parameters = published_hexbeam_parameters(height_m=12.0)

    model = parameters.to_antenna()

    assert len(model.wires) == 9
    assert model.feed.wire_id == "hexbeam-feed"
    assert model.feed.offset_m == pytest.approx(parameters.feed_gap_m / 2.0)
    assert parameters.height_m == pytest.approx(12.0)
    assert len(model.sources) == 0
    driver_ids = {wire.id for wire in model.wires if "driver" in wire.id}
    reflector_ids = {wire.id for wire in model.wires if "reflector" in wire.id}
    assert driver_ids == {
        "hexbeam-driver-left-inner",
        "hexbeam-driver-left-tip",
        "hexbeam-driver-right-inner",
        "hexbeam-driver-right-tip",
    }
    assert reflector_ids == {
        "hexbeam-reflector-left-inner",
        "hexbeam-reflector-left-tip",
        "hexbeam-reflector-right-inner",
        "hexbeam-reflector-right-tip",
    }
    assert all(wire.start.z_m == pytest.approx(12.0) for wire in model.wires)


def test_hexbeam_scales_with_frequency() -> None:
    reference = published_hexbeam_parameters()
    lower = published_hexbeam_parameters(frequency_hz=7_092_000.0)
    ratio = 2.0
    assert lower.driver_half_length_m == pytest.approx(reference.driver_half_length_m * ratio)
    assert lower.reflector_half_length_m == pytest.approx(reference.reflector_half_length_m * ratio)
    assert lower.turning_radius_m == pytest.approx(reference.turning_radius_m * ratio)
    assert lower.tip_gap_m == pytest.approx(reference.tip_gap_m * ratio)


def test_hexbeam_primary_dimension_scales_the_wire_path() -> None:
    parameters = published_hexbeam_parameters()

    assert primary_dimension_m(parameters) == pytest.approx(parameters.driver_half_length_m)

    scaled = with_primary_dimension(parameters, parameters.driver_half_length_m * 1.1)

    assert isinstance(scaled, HexbeamParameters)
    assert scaled.driver_half_length_m == pytest.approx(parameters.driver_half_length_m * 1.1)
    assert scaled.turning_radius_m == pytest.approx(parameters.turning_radius_m * 1.1)
    assert scaled.tip_gap_m == pytest.approx(parameters.tip_gap_m * 1.1)
    assert antenna_type_for(scaled) == "hexbeam"
    assert antenna_template_id(scaled) == "hexbeam"
    assert antenna_family(scaled) is AntennaFamily.YAGI


def test_hexbeam_rejects_inconsistent_dimensions() -> None:
    with pytest.raises(ValueError, match=r"1\.5 times"):
        HexbeamParameters(
            frequency_hz=14_184_000.0,
            driver_half_length_m=1.0,
            reflector_half_length_m=2.0,
            turning_radius_m=1.0,
            tip_gap_m=0.1,
        )
    with pytest.raises(ValueError, match="reflector_half_length_m is too short"):
        HexbeamParameters(
            frequency_hz=14_184_000.0,
            driver_half_length_m=5.0,
            reflector_half_length_m=2.0,
            turning_radius_m=3.0,
            tip_gap_m=0.1,
        )
    with pytest.raises(ValueError, match="tip_gap_m"):
        HexbeamParameters(
            frequency_hz=14_184_000.0,
            driver_half_length_m=5.0,
            reflector_half_length_m=5.0,
            turning_radius_m=3.0,
            tip_gap_m=0.001,
            wire_radius_m=0.001,
        )
