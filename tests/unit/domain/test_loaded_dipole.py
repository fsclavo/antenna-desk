# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    template_load_ids,
    with_primary_dimension,
)
from antennadesk.domain.antennas.dipole import DipoleOrientation
from antennadesk.domain.antennas.family import (
    AntennaFamily,
    antenna_family,
    antenna_template_id,
)
from antennadesk.domain.antennas.loaded_dipole import (
    LOADED_DIPOLE_LEFT_LOAD_ID,
    LOADED_DIPOLE_RIGHT_LOAD_ID,
    LoadedDipoleParameters,
    loaded_dipole_parameters,
)


def test_loaded_dipole_places_two_symmetric_series_coils() -> None:
    parameters = loaded_dipole_parameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        link_offset_m=2.0,
        loading_coil_inductance_h=10e-6,
        loading_coil_resistance_ohm=0.5,
    )
    model = parameters.to_antenna()

    assert parameters.template_name == "Loaded dipole"
    assert model.feed.offset_m == pytest.approx(10.0)
    assert len(model.loads) == 2
    by_id = {load.id: load for load in model.loads}
    assert by_id[LOADED_DIPOLE_LEFT_LOAD_ID].offset_m == pytest.approx(8.0)
    assert by_id[LOADED_DIPOLE_RIGHT_LOAD_ID].offset_m == pytest.approx(12.0)
    assert by_id[LOADED_DIPOLE_LEFT_LOAD_ID].inductance_h == pytest.approx(10e-6)
    assert by_id[LOADED_DIPOLE_LEFT_LOAD_ID].resistance_ohm == pytest.approx(0.5)
    assert parameters.managed_load_ids == frozenset(
        {LOADED_DIPOLE_LEFT_LOAD_ID, LOADED_DIPOLE_RIGHT_LOAD_ID}
    )
    assert template_load_ids(parameters) == parameters.managed_load_ids
    assert parameters.coil_q == pytest.approx(2.0 * math.pi * 7_100_000.0 * 10e-6 / 0.5)
    assert antenna_type_for(parameters) == "loaded_dipole"
    assert antenna_template_id(parameters) == "loaded_dipole"
    assert antenna_family(parameters) is AntennaFamily.DIPOLE


def test_open_links_keep_only_the_center_section() -> None:
    parameters = loaded_dipole_parameters(
        total_length_m=20.0,
        link_offset_m=3.0,
        link_open=True,
    )
    model = parameters.to_antenna()

    assert parameters.template_name == "Linked dipole"
    assert parameters.active_length_m == pytest.approx(6.0)
    assert model.wires[0].length_m == pytest.approx(6.0)
    assert model.feed.offset_m == pytest.approx(3.0)
    assert model.loads == ()
    assert parameters.managed_load_ids == frozenset()
    assert parameters.coil_q is None


def test_disabling_the_coils_leaves_a_plain_dipole() -> None:
    parameters = loaded_dipole_parameters(
        total_length_m=20.0,
        loading_coil_enabled=False,
    )
    model = parameters.to_antenna()

    assert parameters.coil_active is False
    assert model.loads == ()
    assert parameters.managed_load_ids == frozenset()


def test_vertical_loaded_dipole_is_centered_on_the_full_length() -> None:
    parameters = loaded_dipole_parameters(
        total_length_m=20.0,
        height_m=2.0,
        link_offset_m=2.0,
        orientation=DipoleOrientation.VERTICAL,
    )
    model = parameters.to_antenna()

    wire = model.wires[0]
    assert wire.start.z_m == pytest.approx(2.0)
    assert wire.end.z_m == pytest.approx(22.0)
    assert model.feed.offset_m == pytest.approx(10.0)


def test_loaded_dipole_primary_dimension_tracks_the_active_length() -> None:
    closed = loaded_dipole_parameters(total_length_m=20.0)
    open_links = loaded_dipole_parameters(
        total_length_m=20.0,
        link_offset_m=3.0,
        link_open=True,
    )

    assert primary_dimension_m(closed) == pytest.approx(20.0)
    assert primary_dimension_m(open_links) == pytest.approx(6.0)

    scaled = with_primary_dimension(open_links, 8.0)
    assert isinstance(scaled, LoadedDipoleParameters)
    assert scaled.active_length_m == pytest.approx(8.0)
    assert scaled.total_length_m >= 8.0


def test_loaded_dipole_rejects_an_offset_outside_the_wire() -> None:
    with pytest.raises(ValueError, match="half the total length"):
        LoadedDipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            link_offset_m=11.0,
        )


def test_loaded_dipole_normalizes_orientation_and_azimuth() -> None:
    parameters = loaded_dipole_parameters(azimuth_deg=360.0)

    assert parameters.orientation is DipoleOrientation.HORIZONTAL
    assert parameters.azimuth_deg == pytest.approx(0.0)
