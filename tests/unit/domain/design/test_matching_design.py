# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Matching-network design target validation."""

from __future__ import annotations

import pytest

from antennadesk.domain.design.matching_design import MatchingNetworkDesign


def test_design_target_exposes_the_complex_load() -> None:
    design = MatchingNetworkDesign(
        frequency_hz=14_100_000.0,
        load_resistance_ohm=100.0,
        load_reactance_ohm=-25.0,
        source_impedance_ohm=50.0,
        origin=" simulation ",
    )

    assert design.load_impedance_ohm == complex(100.0, -25.0)
    assert design.origin == "simulation"


def test_design_target_requires_positive_resistances() -> None:
    with pytest.raises(ValueError):
        MatchingNetworkDesign(
            frequency_hz=0.0,
            load_resistance_ohm=100.0,
            load_reactance_ohm=0.0,
        )
    with pytest.raises(ValueError):
        MatchingNetworkDesign(
            frequency_hz=7_100_000.0,
            load_resistance_ohm=0.0,
            load_reactance_ohm=0.0,
        )
    with pytest.raises(ValueError):
        MatchingNetworkDesign(
            frequency_hz=7_100_000.0,
            load_resistance_ohm=100.0,
            load_reactance_ohm=0.0,
            source_impedance_ohm=0.0,
        )


def test_design_target_rejects_a_non_finite_reactance() -> None:
    with pytest.raises(ValueError):
        MatchingNetworkDesign(
            frequency_hz=7_100_000.0,
            load_resistance_ohm=100.0,
            load_reactance_ohm=float("inf"),
        )


def test_empty_origin_is_stored_as_none() -> None:
    design = MatchingNetworkDesign(
        frequency_hz=7_100_000.0,
        load_resistance_ohm=100.0,
        load_reactance_ohm=0.0,
        origin="   ",
    )

    assert design.origin is None


def test_origin_is_limited_to_the_persisted_length() -> None:
    with pytest.raises(ValueError):
        MatchingNetworkDesign(
            frequency_hz=7_100_000.0,
            load_resistance_ohm=100.0,
            load_reactance_ohm=0.0,
            origin="x" * 65,
        )
