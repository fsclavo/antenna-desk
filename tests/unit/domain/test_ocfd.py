# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.family import AntennaFamily, antenna_family
from antennadesk.domain.antennas.ocfd import OCFDParameters


def test_ocfd_generates_an_offset_feed_on_one_wire() -> None:
    parameters = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        feed_ratio=1.0 / 3.0,
        height_m=10.0,
        azimuth_deg=30.0,
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 1
    assert custom.feed.wire_id == "radiator"
    assert custom.feed.offset_m == pytest.approx(20.0 / 3.0)
    assert custom.generator_id == "ocfd"
    assert antenna_family(custom) is AntennaFamily.DIPOLE


def test_ocfd_can_be_reconstructed_from_custom_geometry() -> None:
    original = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        feed_ratio=0.3,
        height_m=10.0,
        azimuth_deg=30.0,
    )
    restored = OCFDParameters.from_custom_parameters(original.to_custom_parameters())

    assert restored.total_length_m == pytest.approx(original.total_length_m)
    assert restored.feed_ratio == pytest.approx(original.feed_ratio)
    assert restored.azimuth_deg == pytest.approx(original.azimuth_deg)
    assert restored.height_m == pytest.approx(original.height_m)


def test_ocfd_rejects_invalid_feed_ratio() -> None:
    with pytest.raises(ValueError, match="feed_ratio"):
        OCFDParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            feed_ratio=0.0,
        )
