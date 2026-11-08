# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    with_primary_dimension,
)
from antennadesk.domain.antennas.discone import (
    DISCONE_FEED_ID,
    DisconeParameters,
    discone_parameters,
)
from antennadesk.domain.antennas.family import (
    AntennaFamily,
    antenna_family,
    antenna_template_id,
)


def test_discone_builds_a_radial_cone_and_disc() -> None:
    parameters = discone_parameters(
        frequency_hz=145_000_000.0,
        cone_height_m=0.5,
        cone_radius_m=0.3,
        disc_radius_m=0.5,
        base_height_m=0.5,
        disc_gap_m=0.02,
        wire_count=8,
    )

    model = parameters.to_antenna()

    assert parameters.template_name == "Discone"
    assert len(model.wires) == 2 * 8 + 1
    assert parameters.cone_slant_m == pytest.approx(0.583095)
    assert parameters.apex_height_m == pytest.approx(1.0)
    assert parameters.disc_height_m == pytest.approx(1.02)
    assert parameters.feed_height_m == pytest.approx(1.01)
    assert parameters.overall_diameter_m == pytest.approx(1.0)
    assert model.feed.wire_id == DISCONE_FEED_ID
    assert model.feed.offset_m == pytest.approx(0.01)
    assert parameters.total_conductor_length_m == pytest.approx(
        8 * parameters.cone_slant_m + 8 * 0.5 + 0.02
    )


def test_discone_radials_share_the_apex_and_hub() -> None:
    parameters = discone_parameters(
        cone_height_m=0.5,
        cone_radius_m=0.3,
        disc_radius_m=0.5,
        wire_count=4,
    )

    wires = parameters.to_antenna().wires
    cone = [wire for wire in wires if wire.id.startswith("discone-cone-")]
    disc = [wire for wire in wires if wire.id.startswith("discone-disc-")]

    assert all(wire.start == cone[0].start for wire in cone)
    assert all(wire.start == disc[0].start for wire in disc)
    assert len({wire.end.z_m for wire in cone}) == 1
    assert len({wire.end.z_m for wire in disc}) == 1


def test_discone_primary_dimension_scales_the_shape() -> None:
    parameters = discone_parameters(
        cone_height_m=0.5,
        cone_radius_m=0.3,
        disc_radius_m=0.5,
    )

    assert primary_dimension_m(parameters) == pytest.approx(0.5)

    scaled = with_primary_dimension(parameters, 1.0)

    assert isinstance(scaled, DisconeParameters)
    assert scaled.cone_height_m == pytest.approx(1.0)
    assert scaled.cone_radius_m == pytest.approx(0.6)
    assert scaled.disc_radius_m == pytest.approx(1.0)
    assert antenna_type_for(scaled) == "discone"
    assert antenna_template_id(scaled) == "discone"
    assert antenna_family(scaled) is AntennaFamily.VERTICAL


def test_discone_rejects_invalid_wire_counts_and_dimensions() -> None:
    with pytest.raises(ValueError, match="wire_count"):
        discone_parameters(wire_count=3)
    with pytest.raises(ValueError, match="conductor diameter"):
        discone_parameters(disc_gap_m=0.001, wire_radius_m=0.001)


def test_discone_normalizes_azimuth() -> None:
    parameters = discone_parameters(azimuth_deg=-90.0)

    assert parameters.azimuth_deg == pytest.approx(270.0)
