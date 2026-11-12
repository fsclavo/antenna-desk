# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import discone_parameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.moxon import moxon_20m_wire
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.transmission_line_doublet import (
    DoubletPreset,
    doublet_starting_parameters,
)
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.antennas.yagi import nbs_five_element
from antennadesk.domain.antennas.zepp import zepp_starting_parameters
from antennadesk.domain.design.feed_balance import (
    FeedBalance,
    feed_balance,
    requires_current_balun,
)


def test_balanced_families_require_a_current_balun() -> None:
    balanced = (
        DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
        FoldedDipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=44.0,
            height_m=8.0,
        ),
        nbs_five_element(frequency_hz=14_100_000.0, height_m=10.0),
        moxon_20m_wire(),
        OCFDParameters(frequency_hz=7_100_000.0, total_length_m=20.4),
        T2FDParameters(
            frequency_hz=3_500_000.0,
            highest_frequency_hz=30_000_000.0,
            length_m=26.0,
            spacing_m=0.9,
        ),
        zepp_starting_parameters(),
        doublet_starting_parameters(DoubletPreset.G5RV),
    )

    for parameters in balanced:
        assert requires_current_balun(parameters) is True, type(parameters).__name__


def test_unbalanced_families_do_not_require_a_current_balun() -> None:
    unbalanced = (
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            counterpoise_length_m=2.0,
        ),
        VerticalParameters(frequency_hz=14_100_000.0, height_m=5.0),
        InvertedLParameters(
            frequency_hz=7_100_000.0,
            vertical_height_m=10.0,
            horizontal_length_m=10.0,
        ),
        JPoleParameters(
            frequency_hz=146_000_000.0,
            radiator_height_m=1.5,
            stub_length_m=0.5,
            spacing_m=0.05,
        ),
        RingoParameters(
            frequency_hz=29_000_000.0,
            radiator_height_m=5.0,
            ring_diameter_m=0.5,
        ),
        discone_parameters(frequency_hz=146_000_000.0),
        MagneticLoopParameters(frequency_hz=7_100_000.0, diameter_m=1.0),
    )

    for parameters in unbalanced:
        assert requires_current_balun(parameters) is False, type(parameters).__name__


def test_ambiguous_feeds_are_unknown() -> None:
    custom = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                id="w1",
                start=Point3D(x_m=0.0, y_m=0.0, z_m=8.0),
                end=Point3D(x_m=20.0, y_m=0.0, z_m=8.0),
                radius_m=0.001,
                material=COPPER,
            ),
        ),
        feed=FeedPoint("w1", 10.0),
    )
    magnetic_loop = MagneticLoopParameters(
        frequency_hz=7_100_000.0,
        diameter_m=1.0,
    )

    assert feed_balance(custom) is FeedBalance.UNKNOWN
    assert feed_balance(magnetic_loop) is FeedBalance.UNKNOWN
    assert requires_current_balun(custom) is False
    assert requires_current_balun(magnetic_loop) is False
