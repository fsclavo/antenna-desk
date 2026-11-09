# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.family import AntennaFamily, antenna_family
from antennadesk.domain.antennas.moxon import MoxonParameters, moxon_20m_wire
from antennadesk.domain.antennas.polarization import Polarization
from antennadesk.domain.environment.ground import GroundModel


def test_moxon_generates_six_connected_wires() -> None:
    parameters = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.6,
        depth_m=2.5,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 6
    assert custom.feed.wire_id == "driven"
    assert custom.feed.offset_m == pytest.approx(5.3)
    assert parameters.gap_m == pytest.approx(0.5)
    assert custom.generator_name == "Moxon"
    assert antenna_family(custom) is AntennaFamily.YAGI


def test_moxon_vertical_polarization_puts_the_rectangle_in_a_vertical_plane() -> None:
    parameters = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.0,
        depth_m=2.5,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
        azimuth_deg=25.0,
        polarization=Polarization.VERTICAL,
    )
    custom = parameters.to_custom_parameters()

    reflector = custom.wires[0]
    driven = custom.wires[3]
    assert reflector.start.x_m == pytest.approx(reflector.end.x_m)
    assert reflector.start.y_m == pytest.approx(reflector.end.y_m)
    assert driven.start.x_m == pytest.approx(driven.end.x_m)
    assert driven.start.y_m == pytest.approx(driven.end.y_m)
    assert (reflector.start.z_m + reflector.end.z_m) / 2.0 == pytest.approx(10.0)
    assert reflector.length_m == pytest.approx(10.0)
    assert driven.length_m == pytest.approx(10.0)
    assert custom.wires[1].length_m == pytest.approx(1.0)
    assert custom.feed.wire_id == "driven"
    assert custom.feed.offset_m == pytest.approx(5.0)
    assert parameters.lowest_edge_m == pytest.approx(5.0)


def test_moxon_vertical_rejects_a_rectangle_below_ground() -> None:
    with pytest.raises(ValueError, match="below ground"):
        MoxonParameters(
            frequency_hz=14_100_000.0,
            width_m=20.0,
            depth_m=2.5,
            reflector_tip_m=1.0,
            driven_tip_m=1.0,
            height_m=10.0,
            polarization=Polarization.VERTICAL,
        )


def test_moxon_20m_wire_reference_dimensions() -> None:
    parameters = moxon_20m_wire()

    assert parameters.frequency_hz == pytest.approx(14_170_000.0)
    assert parameters.width_m == pytest.approx(25.00 * 0.3048)
    assert parameters.depth_m == pytest.approx(9.57 * 0.3048)
    assert parameters.reflector_tip_m == pytest.approx(4.85 * 0.3048)
    assert parameters.driven_tip_m == pytest.approx(4.00 * 0.3048)
    assert parameters.gap_m == pytest.approx(0.72 * 0.3048)


def test_moxon_20m_wire_scales_from_the_reference() -> None:
    reference = moxon_20m_wire()
    scaled = moxon_20m_wire(
        frequency_hz=28_400_000.0,
        wire_radius_m=0.002,
        ground=GroundModel.perfect(),
    )
    scale = 14_170_000.0 / 28_400_000.0

    assert scaled.frequency_hz == pytest.approx(28_400_000.0)
    assert scaled.width_m == pytest.approx(reference.width_m * scale)
    assert scaled.depth_m == pytest.approx(reference.depth_m * scale)
    assert scaled.reflector_tip_m == pytest.approx(reference.reflector_tip_m * scale)
    assert scaled.driven_tip_m == pytest.approx(reference.driven_tip_m * scale)
    assert scaled.wire_radius_m == pytest.approx(0.002)
    assert scaled.ground.kind is GroundModel.perfect().kind


def test_moxon_rejects_overlapping_tips() -> None:
    with pytest.raises(ValueError, match="gap"):
        MoxonParameters(
            frequency_hz=14_100_000.0,
            width_m=10.0,
            depth_m=1.0,
            reflector_tip_m=0.6,
            driven_tip_m=0.6,
        )
