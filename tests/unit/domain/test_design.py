# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    with_primary_dimension,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.loop import LoopParameters


def test_primary_dimensions_and_types() -> None:
    dipole = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    folded = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )
    loop = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=8,
    )

    assert primary_dimension_m(dipole) == pytest.approx(20.0)
    assert primary_dimension_m(folded) == pytest.approx(20.0)
    assert primary_dimension_m(loop) == pytest.approx(40.0)
    assert antenna_type_for(dipole) == "wire_dipole"
    assert antenna_type_for(folded) == "folded_dipole"
    assert antenna_type_for(loop) == "loop"


def test_with_primary_dimension_updates_only_the_selected_geometry() -> None:
    folded = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )
    loop = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=8,
    )

    edited_folded = with_primary_dimension(folded, 21.0)
    edited_loop = with_primary_dimension(loop, 42.0)

    assert isinstance(edited_folded, FoldedDipoleParameters)
    assert edited_folded.total_length_m == pytest.approx(21.0)
    assert edited_folded.spacing_m == pytest.approx(0.2)
    assert folded.total_length_m == pytest.approx(20.0)
    assert isinstance(edited_loop, LoopParameters)
    assert edited_loop.circumference_m == pytest.approx(42.0)
    assert edited_loop.sides == 8
    assert loop.circumference_m == pytest.approx(40.0)
