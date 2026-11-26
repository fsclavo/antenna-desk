# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Presentation-only forward-axis and azimuth rules."""

from __future__ import annotations

from antennadesk.domain.antennas.dipole import DipoleOrientation, DipoleParameters
from antennadesk.domain.antennas.stacked_yagi import stacked_yagi_parameters
from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters
from antennadesk.domain.antennas.yagi import nbs_five_element
from antennadesk.ui.pattern_orientation import (
    antenna_orientation,
    forward_axis_azimuth,
)


def test_explicit_forward_axis_is_limited_to_beam_families() -> None:
    yagi = nbs_five_element(
        frequency_hz=14_100_000.0,
        height_m=10.0,
        azimuth_deg=90.0,
    )
    stacked = stacked_yagi_parameters(
        frequency_hz=14_100_000.0,
        count=2,
        height_m=10.0,
        spacing_m=10.6,
        azimuth_deg=45.0,
    )
    trap = trap_yagi_parameters(azimuth_deg=180.0)
    dipole = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        azimuth_deg=30.0,
    )

    assert forward_axis_azimuth(yagi) == 90.0
    assert forward_axis_azimuth(stacked) == 45.0
    assert forward_axis_azimuth(trap) == 180.0
    assert forward_axis_azimuth(dipole) is None


def test_antenna_orientation_distinguishes_vertical_and_horizontal() -> None:
    horizontal = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        azimuth_deg=30.0,
    )
    vertical = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=1.0,
        orientation=DipoleOrientation.VERTICAL,
    )

    assert antenna_orientation(horizontal) == (30.0, False)
    assert antenna_orientation(vertical) == (0.0, True)
    assert antenna_orientation(None) == (None, False)
