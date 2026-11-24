# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Managed live-tuning dimensions per family."""

from __future__ import annotations

import pytest

from antennadesk.domain.antennas.dimensions import managed_dimensions
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.environment.ground import GroundModel


def _dipole() -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        ground=GroundModel.finite(relative_permittivity=13.0, conductivity_s_per_m=0.005),
    )


def test_dipole_exposes_primary_and_height() -> None:
    dimensions = managed_dimensions(_dipole())

    assert [dimension.key for dimension in dimensions] == ["primary", "height"]
    assert dimensions[1].read(_dipole()) == pytest.approx(8.0)
    changed = dimensions[1].write(_dipole(), 12.0)
    assert isinstance(changed, DipoleParameters)
    assert changed.height_m == pytest.approx(12.0)
    assert changed.total_length_m == pytest.approx(20.0)


def test_vertical_adds_contextual_dimensions() -> None:
    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.5,
        radial_count=4,
        radial_length_m=5.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=2.0,
        loading_coil_inductance_h=10e-6,
        top_hat_enabled=True,
        top_hat_radius_m=0.5,
        top_hat_wire_count=4,
    )
    keys = [dimension.key for dimension in managed_dimensions(parameters)]

    assert keys[0] == "primary"
    assert "base_height" in keys
    assert "radial_length" in keys
    assert "loading_coil_offset" in keys
    assert "top_hat_radius" in keys


def test_contextual_dimensions_disappear_when_disabled() -> None:
    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        radial_count=0,
    )
    keys = [dimension.key for dimension in managed_dimensions(parameters)]

    assert "radial_length" not in keys
    assert "top_hat_radius" not in keys
    assert "loading_coil_offset" not in keys


def test_t2fd_exposes_spacing_and_height() -> None:
    parameters = T2FDParameters(
        frequency_hz=7_100_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=20.0,
        spacing_m=0.3,
        height_m=10.0,
    )
    keys = [dimension.key for dimension in managed_dimensions(parameters)]

    assert keys == ["primary", "height", "spacing"]


def test_yagi_and_moxon_have_no_primary_dimension() -> None:
    from antennadesk.domain.antennas.moxon import moxon_20m_wire
    from antennadesk.domain.antennas.yagi import nbs_five_element

    yagi = nbs_five_element(frequency_hz=14_100_000.0, height_m=10.0)
    moxon = moxon_20m_wire(frequency_hz=14_100_000.0, height_m=10.0)

    assert managed_dimensions(yagi) == ()
    assert managed_dimensions(moxon) == ()
