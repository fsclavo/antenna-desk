# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.family import AntennaFamily, antenna_family
from antennadesk.domain.antennas.moxon import MoxonParameters, moxon_20m_wire


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


def test_moxon_20m_wire_reference_dimensions() -> None:
    parameters = moxon_20m_wire()

    assert parameters.frequency_hz == pytest.approx(14_170_000.0)
    assert parameters.width_m == pytest.approx(25.00 * 0.3048)
    assert parameters.depth_m == pytest.approx(9.57 * 0.3048)
    assert parameters.reflector_tip_m == pytest.approx(4.85 * 0.3048)
    assert parameters.driven_tip_m == pytest.approx(4.00 * 0.3048)
    assert parameters.gap_m == pytest.approx(0.72 * 0.3048)


def test_moxon_rejects_overlapping_tips() -> None:
    with pytest.raises(ValueError, match="gap"):
        MoxonParameters(
            frequency_hz=14_100_000.0,
            width_m=10.0,
            depth_m=1.0,
            reflector_tip_m=0.6,
            driven_tip_m=0.6,
        )
