# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.family import AntennaFamily, antenna_family, antenna_template_id
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.antennas.yagi import nbs_five_element


def _custom(generator_id: str | None) -> CustomAntennaParameters:
    return CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                id="wire-1",
                start=Point3D(-1.0, 0.0, 8.0),
                end=Point3D(1.0, 0.0, 8.0),
                radius_m=0.001,
                material=COPPER,
            ),
        ),
        feed=FeedPoint("wire-1", 1.0),
        generator_id=generator_id,
        generator_name=generator_id,
    )


def test_native_templates_map_to_families() -> None:
    dipole = DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0)
    folded = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.1,
    )
    loop = LoopParameters(frequency_hz=7_100_000.0, circumference_m=40.0, height_m=8.0)

    assert antenna_family(dipole) is AntennaFamily.DIPOLE
    assert antenna_family(folded) is AntennaFamily.DIPOLE
    assert antenna_family(loop) is AntennaFamily.LOOP
    assert antenna_template_id(dipole) == "wire_dipole"
    assert antenna_template_id(folded) == "folded_dipole"
    assert antenna_template_id(loop) == "loop"


def test_generated_templates_map_to_their_family() -> None:
    inverted = InvertedVParameters(
        frequency_hz=7_100_000.0,
        leg_length_m=10.0,
        apex_height_m=12.0,
    ).to_custom_parameters()
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0).to_custom_parameters()

    assert antenna_family(inverted) is AntennaFamily.DIPOLE
    assert antenna_template_id(inverted) == "inverted_v"
    assert antenna_family(yagi) is AntennaFamily.YAGI
    assert antenna_template_id(yagi) == "yagi"


def test_custom_without_generator_is_custom() -> None:
    custom = _custom(None)

    assert antenna_family(custom) is AntennaFamily.CUSTOM
    assert antenna_template_id(custom) == "custom"
