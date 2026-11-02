# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.family import AntennaFamily, antenna_family
from antennadesk.domain.antennas.feed import FeedPoint


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
    assert custom.wires[0].length_m == pytest.approx(20.0)
    assert custom.generator_name == "End-fed"
    assert antenna_family(custom) is AntennaFamily.DIPOLE


def test_endfed_rejects_below_ground_heights() -> None:
    with pytest.raises(ValueError, match="end_height"):
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            end_height_m=-1.0,
        )


def test_endfed_rejects_a_slope_steeper_than_the_wire() -> None:
    with pytest.raises(ValueError, match="height difference"):
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=5.0,
            feed_height_m=1.0,
            end_height_m=10.0,
        )


def test_endfed_counterpoise_adds_a_drop_and_horizontal_wire() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=5.0,
        azimuth_deg=0.0,
        counterpoise_length_m=3.0,
        counterpoise_height_m=0.2,
    )
    custom = parameters.to_custom_parameters()

    assert [wire.id for wire in custom.wires] == [
        "radiator",
        "counterpoise-drop",
        "counterpoise",
    ]
    drop, counterpoise = custom.wires[1], custom.wires[2]
    assert drop.start.z_m == pytest.approx(10.0)
    assert drop.end.z_m == pytest.approx(0.2)
    assert drop.length_m == pytest.approx(9.8)
    assert counterpoise.start == drop.end
    assert counterpoise.end.x_m == pytest.approx(-3.0)
    assert counterpoise.end.y_m == pytest.approx(0.0, abs=1e-12)
    assert counterpoise.length_m == pytest.approx(3.0)
    assert custom.feed == FeedPoint("radiator", 0.0)


def test_endfed_counterpoise_is_optional() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        counterpoise_length_m=0.0,
    )

    assert len(parameters.to_custom_parameters().wires) == 1


def test_endfed_counterpoise_azimuth_defaults_opposite_the_radiator() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        azimuth_deg=30.0,
        counterpoise_length_m=2.0,
    )

    assert parameters.effective_counterpoise_azimuth_deg == pytest.approx(210.0)


def test_endfed_rejects_an_invalid_transformer_ratio() -> None:
    with pytest.raises(ValueError, match="transformer_ratio"):
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            transformer_ratio=0.0,
        )
