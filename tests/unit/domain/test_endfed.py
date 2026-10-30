# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.family import AntennaFamily, antenna_family


def test_endfed_generates_one_wire_with_end_feed() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=5.0,
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 1
    assert custom.feed.wire_id == "radiator"
    assert custom.feed.offset_m == 0.0
    assert custom.wires[0].end.z_m == pytest.approx(5.0)
    assert custom.generator_name == "End-fed"
    assert antenna_family(custom) is AntennaFamily.DIPOLE


def test_endfed_rejects_below_ground_heights() -> None:
    with pytest.raises(ValueError, match="end_height"):
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            end_height_m=-1.0,
        )
