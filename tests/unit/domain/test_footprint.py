# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.footprint import (
    boom_length_m,
    rotation_center_m,
    turning_radius_m,
)
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters


def test_dipole_turning_radius_is_measured_from_the_feed() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )

    model = parameters.to_antenna()

    assert boom_length_m(parameters) is None
    assert rotation_center_m(parameters, model) == pytest.approx((0.0, 0.0))
    assert turning_radius_m(parameters, model) == pytest.approx(10.0)


def test_yagi_boom_and_turning_radius_use_the_boom_midpoint() -> None:
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
    )

    model = parameters.to_antenna()

    assert boom_length_m(parameters) == pytest.approx(2.0)
    assert rotation_center_m(parameters, model) == pytest.approx((1.0, 0.0))
    expected = math.hypot(1.0, 5.0)
    assert turning_radius_m(parameters, model) == pytest.approx(expected)


def test_moxon_boom_is_its_depth() -> None:
    parameters = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.0,
        depth_m=3.0,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
    )

    assert boom_length_m(parameters) == pytest.approx(3.0)
